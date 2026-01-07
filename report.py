"""Generate formatted safety report."""
from typing import Dict, List, Optional


def generate_report(analysis_result: Dict) -> str:
    """Generate formatted report string."""
    risk = analysis_result["risk"]
    reasons = analysis_result["reasons"]
    affected_areas = analysis_result["affected_areas"]
    recommendation = analysis_result["recommendation"]
    
    report = []
    report.append("SENTRA REPORT")
    report.append("=" * 16)
    report.append("")
    report.append(f"Overall Risk: {risk}")
    report.append("")
    
    if reasons:
        report.append("Reasons:")
        for reason in reasons:
            report.append(f"- {reason}")
        report.append("")
    
    if affected_areas:
        report.append("Affected Areas:")
        for area in affected_areas:
            report.append(f"- {area}")
        report.append("")
    
    report.append("Recommendation:")
    if recommendation == "Block merge":
        report.append("[X] Block merge")
        report.append("Manual review required.")
    elif recommendation == "Require manual review":
        report.append("[!] Require manual review")
    else:
        report.append("[OK] Allow merge")
    
    return "\n".join(report)


def generate_pr_comment(
    decision: str,
    confidence: float,
    reasons: List[Dict],
    metadata: Dict,
    confidence_breakdown: Optional[List[str]] = None,
    license_tier: Optional[str] = None,
    original_decision: Optional[str] = None
) -> str:
    """Generate perfect PR comment format for three audiences.
    
    Args:
        decision: ALLOW, WARN, or BLOCK
        confidence: Confidence score (0.0-1.0)
        reasons: List of triggered rule results
        metadata: Metadata dict with base_branch, etc.
        confidence_breakdown: Optional list of confidence explanation factors
        
    Returns:
        Formatted markdown string ready for PR comment
    """
    # Decision emoji mapping
    decision_emoji = {
        "ALLOW": "✅",
        "WARN": "⚠️",
        "BLOCK": "🚫"
    }.get(decision, "❓")
    
    confidence_pct = int(confidence * 100)
    base_branch = metadata.get("base_branch", "main")
    
    lines = []
    lines.append("## 🛡 Sentra Policy Check")
    lines.append("")
    lines.append(f"**Decision:** {decision_emoji} {decision}")
    lines.append(f"**Confidence:** {confidence_pct}%")
    lines.append(f"**Base branch:** {base_branch}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Findings section
    if reasons:
        lines.append(f"### {decision_emoji} Findings ({len(reasons)})")
        lines.append("")
        
        for reason in reasons:
            rule_id = reason.get("rule_id", "UNKNOWN")
            severity = reason.get("severity", "UNKNOWN")
            message = reason.get("message", "")
            files = reason.get("files", [])
            
            # Severity display (contextual, not scary)
            severity_display = {
                "CRITICAL": "High severity",
                "HIGH": "High severity",
                "MEDIUM": "Medium severity",
                "LOW": "Low severity"
            }.get(severity, severity.lower() + " severity")
            
            lines.append(f"**{rule_id}** · _{severity_display}_")
            if message:
                lines.append(message)
            lines.append("")
            
            # Affected files
            if files:
                if len(files) == 1:
                    lines.append("**Affected file:**")
                else:
                    lines.append("**Affected files:**")
                lines.append("")
                for file in files[:10]:  # Limit to 10 files
                    lines.append(f"- `{file}`")
                if len(files) > 10:
                    lines.append(f"- ... and {len(files) - 10} more")
                lines.append("")
    else:
        lines.append("### ✅ No Findings")
        lines.append("")
        lines.append("No policy violations detected.")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Confidence breakdown (only if confidence < 0.8)
    if confidence < 0.8 and confidence_breakdown:
        lines.append("### 📊 Confidence Breakdown")
        for factor in confidence_breakdown:
            lines.append(f"- {factor}")
        lines.append("")
        lines.append(f"_Resulting confidence: **{confidence_pct}%**_")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # What this means section
    lines.append("### ✅ What this means")
    lines.append("")
    
    if decision == "ALLOW":
        lines.append("- This change is **safe to merge**")
        if reasons:
            lines.append("- No blocking issues detected")
        else:
            lines.append("- No policy violations found")
    elif decision == "WARN":
        lines.append("- This change is **allowed to merge**")
        lines.append("- Reviewer attention is **recommended**")
        
        # Show upgrade message if this was downgraded from BLOCK due to Free tier
        if original_decision == "BLOCK":
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("### 💡 Upgrade Notice")
            lines.append("")
            lines.append("**Original Decision:** BLOCK")
            lines.append("**Result:** Merge blocked by Sentra policy")
            lines.append("")
            lines.append("⚠️ **BLOCK enforcement requires Pro tier.**")
            lines.append("")
            lines.append("Upgrade to Pro tier to enable merge blocking for policy violations.")
            lines.append("")
            lines.append("---")
            lines.append("")
        elif reasons:
            # Provide actionable guidance based on first reason
            first_rule = reasons[0].get("rule_id", "")
            if "TEST_COVERAGE" in first_rule:
                lines.append("- Adding or updating tests will remove this warning")
            elif "CROSS_SERVICE" in first_rule:
                lines.append("- Consider splitting into smaller, focused changes")
            elif "LARGE_DIFF" in first_rule:
                lines.append("- Consider breaking this into smaller PRs")
            else:
                lines.append("- Address the findings above to improve confidence")
    else:  # BLOCK
        lines.append("- This change is **blocked from merging**")
        lines.append("- Policy requires manual review")
        lines.append("- Address all findings before merging")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_This check is enforced by Sentra. Learn more → sentra.dev_")
    
    # Add version stamp at the end (tiny, powerful)
    from version import __version__
    lines.append("")
    lines.append(f"_Sentra v{__version__} · Policy engine_")
    
    return "\n".join(lines)

