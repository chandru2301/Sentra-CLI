"""CLI entry point for sentra."""
import sys
import json
import argparse
import os
from risk_engine import RiskEngine
from decision import map_decision, explain_confidence
from git_utils import ensure_git_available
from policy_loader import load_policy
from report import generate_pr_comment
from console import console
from banner import print_banner
from license import get_license_tier, should_enforce_block, get_upgrade_message

from version import __version__


def print_pretty(result: dict, rules: list = None, license_tier: str = None, original_decision: str = None):
    """Print human-readable formatted output with enterprise-grade polish.
    
    Uses rich console with Sentra theme for consistent, professional output.
    
    Args:
        result: The analysis result dictionary
        rules: Optional list of rule results for confidence breakdown
        license_tier: Optional license tier ("free" or "pro")
        original_decision: Optional original decision if downgraded
    """
    decision = result["decision"]
    confidence = result["confidence"]
    confidence_pct = int(confidence * 100)
    metadata = result["metadata"]
    reasons = result["reasons"]
    
    # Get license tier and original decision from metadata if not provided
    if license_tier is None:
        license_tier = metadata.get("license_tier", "free")
    if original_decision is None:
        original_decision = metadata.get("original_decision")
    
    # Decision icons and styles (semantic colors)
    icon = {
        "ALLOW": "✅",
        "WARN": "⚠️",
        "BLOCK": "❌"
    }.get(decision, "❓")
    
    style_map = {
        "ALLOW": "success",
        "WARN": "warn",
        "BLOCK": "error"
    }
    decision_style = style_map.get(decision, "primary")
    
    # Header with purple rule (brand identity)
    console.print()
    console.rule(f"Sentra Policy Scan · v{__version__}", style="rule")
    console.print()
    
    # Decision (purple label, colored decision)
    console.print("Decision:", style="primary", end=" ")
    console.print(f"{icon} {decision}", style=decision_style, highlight=False)
    
    # Confidence (purple)
    console.print(f"Confidence: {confidence_pct}%", style="primary")
    
    # Metadata (muted)
    console.print(f"Base branch: {metadata.get('base_branch', 'unknown')}", style="muted")
    console.print(f"Files changed: {metadata.get('changed_files', 0)}", style="muted")
    console.print()
    
    # Findings with deterministic wording
    if reasons:
        console.print(f"Policy Findings ({len(reasons)})", style="primary.bold")
        for r in reasons:
            severity = r.get("severity", "UNKNOWN")
            rule_id = r.get("rule_id", "UNKNOWN")
            message = r.get("message", "")
            files = r.get("files", [])
            
            # Severity color mapping
            severity_style = {
                "CRITICAL": "error",
                "HIGH": "error",
                "MEDIUM": "warn",
                "LOW": "muted"
            }.get(severity, "muted")
            
            # Use deterministic wording: "Detected" or "Rule triggered"
            # Severity is visually secondary (use · instead of [])
            console.print(f"• {rule_id}", style="primary", end=" ")
            console.print(f"· {severity}", style="muted", highlight=False)
            
            if message:
                # Ensure message uses deterministic language
                deterministic_message = message
                if message.startswith("Detected") or message.startswith("Rule triggered"):
                    pass  # Already deterministic
                elif "might" in message.lower() or "possibly" in message.lower():
                    # Replace uncertain language
                    deterministic_message = message.replace("might", "detected").replace("possibly", "detected")
                console.print(f"  {deterministic_message}", style="muted")
            
            if files:
                console.print()
                for f in files[:5]:  # Limit to 5 files
                    console.print(f"  • {f}", style="muted")
                if len(files) > 5:
                    console.print(f"  ... and {len(files) - 5} more", style="muted")
            console.print()
    else:
        console.print("✅ No policy violations detected", style="success")
        console.print()
    
    # Confidence breakdown (only if confidence < 0.8)
    if confidence < 0.8 and rules:
        confidence_factors = explain_confidence(rules, decision, confidence, metadata)
        if confidence_factors:
            console.print("Confidence Breakdown", style="primary.bold")
            for factor in confidence_factors:
                console.print(f"  {factor}", style="muted")
    
    # Metadata (reduced spacing)
    ai_status = metadata.get("ai_escalation", "disabled")
    policy_status = "yes" if metadata.get("policy_applied", False) else "no"
    console.print(f"AI escalation: {ai_status}", style="muted")
    console.print(f"Policy applied: {policy_status}", style="muted")
    
    # Result summary with semantic colors (authoritative footer)
    result_messages = {
        "ALLOW": ("Safe to merge", "success"),
        "WARN": ("Review recommended", "warn"),
        "BLOCK": ("Merge blocked", "error")
    }
    result_msg, result_style = result_messages.get(decision, ("Unknown", "muted"))
    
    # Check if decision was downgraded due to Free tier
    original_decision = result.get("metadata", {}).get("original_decision")
    license_tier = result.get("metadata", {}).get("license_tier", "free")
    
    console.print("─" * 40, style="muted")
    console.print(f"Result: {result_msg}", style=result_style)
    if decision == "BLOCK":
        console.print("Policy requires manual review", style="muted")
    elif original_decision == "BLOCK" and decision == "WARN":
        # Show upgrade message for Free tier users
        from license import get_upgrade_message
        console.print(get_upgrade_message(), style="muted")
    console.print(f"CI output: sentra scan --json", style="muted")
    console.print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sentra - Analyze git diffs for PR safety"
    )
    parser.add_argument(
        "command",
        choices=["scan"],
        help="Command to execute"
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to compare against (default: main)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format (for CI/machine parsing)"
    )
    parser.add_argument(
        "--pr-comment",
        action="store_true",
        help="Output PR comment format (markdown for PR comments)"
    )
    parser.add_argument(
        "--banner",
        action="store_true",
        help="Show ASCII banner (enterprise users prefer clean by default)"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        # Show banner if requested (optional, clean by default)
        if args.banner:
            print_banner()
        
        # Preflight check: Git must be available
        try:
            ensure_git_available()
        except RuntimeError as e:
            if str(e) == "GIT_NOT_AVAILABLE":
                git_error_output = {
                    "decision": "BLOCK",
                    "confidence": 1.0,
                    "reasons": [
                        {
                            "rule_id": "GIT_NOT_AVAILABLE",
                            "severity": "CRITICAL",
                            "message": "Git is not installed or not available in PATH"
                        }
                    ],
                    "metadata": {
                        "changed_files": 0,
                        "affected_areas": [],
                        "base_branch": "unknown",
                        "ai_escalation": "disabled",
                        "policy_applied": False
                    }
                }
                
                # For git errors, check if JSON output was requested
                if args.json:
                    # JSON output: no colors, no emojis, no surprises
                    print(json.dumps(git_error_output, indent=2))
                else:
                    print_pretty(git_error_output)
                sys.exit(1)
            else:
                raise
        
        try:
            # Load policy (if exists)
            policy = load_policy()
            # Policy is applied if version is set (meaning file exists)
            policy_applied = policy is not None and policy.get("version") is not None
            
            engine = RiskEngine(base_branch=args.base)
            result = engine.analyze(policy=policy)
            
            # Map rules to decision and confidence (policy-aware)
            # Pass metadata with base_branch (resolved target branch) for policy evaluation
            metadata_for_policy = {
                "base_branch": result["base_branch"],  # Resolved target branch (where PR merges into)
                "changed_files": result["changed_files_count"],
                "affected_areas": result["affected_areas"]
            }
            decision, confidence = map_decision(
                result["rules"], 
                policy=policy if policy_applied else None,
                metadata=metadata_for_policy
            )
            
            # Apply license tier enforcement (Free tier downgrades BLOCK to WARN)
            license_tier = get_license_tier()
            original_decision = decision
            if decision == "BLOCK" and not should_enforce_block(license_tier):
                # Free tier: downgrade BLOCK to WARN
                decision = "WARN"
                # Adjust confidence slightly for downgraded decision
                confidence = min(confidence, 0.75)
            
            # Build JSON output
            # Always ensure reasons is an array, never null or omitted
            triggered_rules = [r for r in result["rules"] if r.get("triggered", False)]
            reasons = []
            for r in triggered_rules:
                reason = {
                    "rule_id": r["rule_id"],
                    "severity": r["severity"],
                    "message": r["message"],
                    "files": r.get("files", [])
                }
                # Include ai_escalated flag if present (for audit trail)
                if r.get("ai_escalated"):
                    reason["ai_escalated"] = True
                reasons.append(reason)
            
            # Build policy metadata
            policy_metadata = {}
            if policy_applied:
                policy_metadata["policy_applied"] = True
                policy_metadata["policy_file"] = "policy.yaml"
                if policy.get("version"):
                    policy_metadata["policy_version"] = policy["version"]
            else:
                policy_metadata["policy_applied"] = False
            
            output = {
                "decision": decision,
                "confidence": confidence,
                "reasons": reasons,  # Always an array, never null
                "metadata": {
                    "changed_files": result["changed_files_count"],
                    "affected_areas": result["affected_areas"],
                    "base_branch": result["base_branch"],
                    "ai_escalation": "enabled" if result.get("ai_escalation_enabled", False) else "disabled",
                    "license_tier": license_tier,
                    "original_decision": original_decision if original_decision != decision else None,
                    **policy_metadata
                }
            }
            
            # Output format based on flag
            if args.pr_comment:
                # PR comment format (markdown) - plain text, no colors
                confidence_factors = explain_confidence(
                    result["rules"], decision, confidence, output["metadata"]
                )
                pr_comment = generate_pr_comment(
                    decision=decision,
                    confidence=confidence,
                    reasons=reasons,
                    metadata=output["metadata"],
                    confidence_breakdown=confidence_factors,
                    license_tier=license_tier,
                    original_decision=original_decision if original_decision != decision else None
                )
                # Use plain print for PR comments (markdown, no colors)
                print(pr_comment)
            elif args.json:
                # Machine-readable JSON: no colors, no emojis, no surprises
                # rich respects NO_COLOR, but we also disable for JSON explicitly
                print(json.dumps(output, indent=2))
            else:
                # Human-readable format with confidence breakdown
                # rich console respects NO_COLOR environment variable automatically
                print_pretty(output, rules=result["rules"], license_tier=license_tier, original_decision=original_decision if original_decision != decision else None)
            
            # Exit code based on decision: BLOCK = 1, ALLOW/WARN = 0
            # This makes Sentra predictable for enterprises
            # Free tier: BLOCK is downgraded to WARN, so exit code is 0
            # Pro tier: BLOCK remains BLOCK, so exit code is 1
            exit_code = 1 if decision == "BLOCK" else 0
            sys.exit(exit_code)
            
        except Exception as e:
            # Use console for errors (respects NO_COLOR automatically)
            console.print(f"Error: {e}", style="error")
            sys.exit(1)


if __name__ == "__main__":
    main()

