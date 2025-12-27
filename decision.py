"""Map rule results to decision and confidence."""
from typing import Tuple, List, Dict, Optional


def map_decision(rules: List[Dict], policy: Optional[Dict] = None, metadata: Optional[Dict] = None) -> Tuple[str, float]:
    """Map triggered rules to decision (ALLOW/WARN/BLOCK) and confidence.
    
    If policy is provided, it takes precedence over default decision logic.
    
    Confidence rules:
    - ALLOW: ≤ 0.95
    - WARN: ≤ 0.75
    - BLOCK (rule-based): ≤ 0.90
    - BLOCK (infra failure): 1.0 (handled in CLI)
    
    Args:
        rules: List of rule results with 'triggered' and 'severity' fields
        policy: Optional policy dict (if None, uses default decision logic)
        metadata: Optional metadata dict with base_branch, etc. (for policy evaluation)
    
    Returns:
        Tuple of (decision, confidence)
    """
    severities = [r["severity"] for r in rules if r.get("triggered", False)]
    
    if not severities:
        return "ALLOW", 0.95
    
    # If policy is provided and has a version, use policy-based decision
    if policy and policy.get("version") is not None:
        from policy_engine import apply_policy, policy_decision
        # Use provided metadata or create minimal one
        # metadata should contain base_branch (resolved target branch name)
        policy_metadata = metadata or {}
        enforced_severities = apply_policy(rules, policy_metadata, policy)
        decision = policy_decision(enforced_severities, policy)
        
        # Map decision to confidence
        if decision == "BLOCK":
            return "BLOCK", 0.9
        elif decision == "WARN":
            return "WARN", 0.6
        else:
            return "ALLOW", 0.95
    
    # Default decision logic (no policy)
    if "CRITICAL" in severities or "HIGH" in severities:
        return "BLOCK", 0.9
    elif "MEDIUM" in severities:
        return "WARN", 0.6
    else:
        return "ALLOW", 0.95


def explain_confidence(
    rules: List[Dict],
    decision: str,
    confidence: float,
    metadata: Optional[Dict] = None
) -> List[str]:
    """Generate human-readable confidence breakdown explanation.
    
    Only returns factors when confidence < 0.8 (needs explanation).
    
    Args:
        rules: List of rule results
        decision: Decision (ALLOW/WARN/BLOCK)
        confidence: Confidence score (0.0-1.0)
        metadata: Optional metadata dict
        
    Returns:
        List of confidence factor explanations (empty if confidence >= 0.8)
    """
    if confidence >= 0.8:
        return []
    
    factors = []
    triggered_rules = [r for r in rules if r.get("triggered", False)]
    
    # Check for deterministic rules (test coverage, etc.)
    deterministic_rules = ["TEST_COVERAGE", "LARGE_DIFF", "CROSS_SERVICE"]
    has_deterministic = any(
        r.get("rule_id", "") in deterministic_rules for r in triggered_rules
    )
    if has_deterministic:
        factors.append("✔ Deterministic rule evaluation")
    
    # Check for test coverage
    has_test_coverage_issue = any(
        "TEST_COVERAGE" in r.get("rule_id", "") for r in triggered_rules
    )
    if has_test_coverage_issue:
        factors.append("✖ No test coverage changes detected")
    else:
        # Check if tests were updated (heuristic: look for test files in changed files)
        changed_files = []
        for rule in triggered_rules:
            changed_files.extend(rule.get("files", []))
        has_tests = any(
            "test" in f.lower() or "spec" in f.lower() for f in changed_files
        )
        if has_tests:
            factors.append("✔ Test files updated")
    
    # Check for core module changes
    core_modules = ["auth", "gateway", "config", "identity", "security"]
    has_core_module = any(
        any(module in f.lower() for module in core_modules)
        for rule in triggered_rules
        for f in rule.get("files", [])
    )
    if has_core_module:
        factors.append("✖ Core module touched")
    else:
        # Check if truly single module or small number of modules
        # Extract top-level directories/modules from changed files
        changed_files = []
        for rule in triggered_rules:
            changed_files.extend(rule.get("files", []))
        
        # Count distinct top-level modules (heuristic: first path component)
        modules = set()
        for f in changed_files:
            parts = f.split('/')
            if len(parts) > 1:
                # Skip common non-module dirs
                if parts[0] not in ['src', 'test', 'tests', 'docs', 'scripts', 'config', '.github']:
                    modules.add(parts[0])
            elif len(parts) == 1 and '.' not in parts[0]:
                # Root-level file, count as a module
                modules.add('root')
        
        if len(modules) <= 1:
            factors.append("✔ Change limited to a single module")
        else:
            factors.append("✔ Change limited to a small number of modules")
    
    # Check for AI escalation
    has_ai_escalation = any(r.get("ai_escalated", False) for r in triggered_rules)
    if has_ai_escalation:
        factors.append("✖ AI-generated code escalation")
    else:
        factors.append("✔ No AI-generated code escalation")
    
    return factors