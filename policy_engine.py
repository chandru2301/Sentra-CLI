"""Policy engine that applies policy rules to rule results."""
from typing import Dict, List


SEVERITY_ORDER = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3
}


def apply_policy(rules: List[Dict], metadata: Dict, policy: Dict) -> List[str]:
    """Apply policy to rule results.
    
    Policy can:
    - Force BLOCK on specific rules (always_block)
    - Lower tolerance for specific paths
    - Override default thresholds
    
    Policy cannot:
    - Change rule logic
    - Modify AI behavior
    - Downgrade detected severity
    - Silence a triggered rule
    
    Args:
        rules: List of rule results with 'triggered', 'severity', 'rule_id', 'files'
        metadata: Metadata dict with 'changed_files', 'affected_areas', 'base_branch', etc.
        policy: Policy configuration dict
        
    Returns:
        List of enforced severities (after policy application)
    """
    enforced_severities = []
    
    # Get path-based policies
    path_policies = policy.get("paths", {})
    protected_branches = policy.get("branches", {}).get("protected", [])
    
    # Use base_branch (target branch where PR is being merged into)
    # This is the resolved branch name, not the source branch
    # Example: feature-branch → main (base_branch = "main", which is protected)
    base_branch = metadata.get("base_branch", "")
    
    # Check if target branch (base_branch) is protected
    # Policy applies based on where the PR is going, not where it's coming from
    is_protected = False
    for pattern in protected_branches:
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            if base_branch.startswith(prefix):
                is_protected = True
                break
        elif base_branch == pattern:
            is_protected = True
            break
    
    for rule in rules:
        if not rule.get("triggered", False):
            continue
        
        severity = rule["severity"]
        original_severity = severity  # Store original for invariant check
        rule_id = rule.get("rule_id", "")
        rule_files = rule.get("files", [])
        
        # Rule-level enforcement (highest priority)
        rule_policy = policy.get("rules", {}).get(rule_id, {})
        if rule_policy.get("always_block"):
            enforced_severity = "CRITICAL"
            # Invariant: enforced severity must be >= original severity
            assert SEVERITY_ORDER.get(enforced_severity, 0) >= SEVERITY_ORDER.get(original_severity, 0), \
                f"Policy violation: enforced {enforced_severity} < original {original_severity}"
            enforced_severities.append(enforced_severity)
            continue
        
        # Check max_allowed_severity for this rule
        max_allowed = rule_policy.get("max_allowed_severity")
        if max_allowed and SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(max_allowed, 0):
            # Severity exceeds max allowed, escalate to CRITICAL
            enforced_severity = "CRITICAL"
            # Invariant: enforced severity must be >= original severity
            assert SEVERITY_ORDER.get(enforced_severity, 0) >= SEVERITY_ORDER.get(original_severity, 0), \
                f"Policy violation: enforced {enforced_severity} < original {original_severity}"
            enforced_severities.append(enforced_severity)
            continue
        
        # Path-based enforcement
        # Check if any file matches a path policy
        path_escalated = False
        for filepath in rule_files:
            for path_pattern, path_config in path_policies.items():
                # Simple prefix matching (can be enhanced later)
                pattern = path_pattern.rstrip("/")
                if filepath.startswith(pattern + "/") or filepath == pattern:
                    block_severity = path_config.get("block_severity")
                    if block_severity:
                        # If current severity >= block_severity for this path, escalate
                        if SEVERITY_ORDER.get(severity, 0) >= SEVERITY_ORDER.get(block_severity, 0):
                            enforced_severity = "CRITICAL"
                            # Invariant: enforced severity must be >= original severity
                            assert SEVERITY_ORDER.get(enforced_severity, 0) >= SEVERITY_ORDER.get(original_severity, 0), \
                                f"Policy violation: enforced {enforced_severity} < original {original_severity}"
                            enforced_severities.append(enforced_severity)
                            path_escalated = True
                            break
            if path_escalated:
                break
        
        if not path_escalated:
            # No policy override, use original severity
            # Invariant: enforced severity must be >= original severity (trivially true here)
            enforced_severity = severity
            assert SEVERITY_ORDER.get(enforced_severity, 0) >= SEVERITY_ORDER.get(original_severity, 0), \
                f"Policy violation: enforced {enforced_severity} < original {original_severity}"
            enforced_severities.append(enforced_severity)
    
    return enforced_severities


def policy_decision(enforced_severities: List[str], policy: Dict) -> str:
    """Map enforced severities to decision based on policy.
    
    Args:
        enforced_severities: List of severities after policy application
        policy: Policy configuration dict
        
    Returns:
        Decision: "ALLOW", "WARN", or "BLOCK"
    """
    if not enforced_severities:
        return "ALLOW"
    
    defaults = policy.get("defaults", {})
    block_severity = defaults.get("block_severity", "HIGH")
    allow_severity = defaults.get("allow_severity", "LOW")
    
    # Find maximum severity
    max_sev = max(enforced_severities, key=lambda s: SEVERITY_ORDER.get(s, 0))
    
    # Check if we should BLOCK
    if SEVERITY_ORDER.get(max_sev, 0) >= SEVERITY_ORDER.get(block_severity, 2):
        return "BLOCK"
    
    # Check if we should WARN (MEDIUM severity)
    if max_sev == "MEDIUM":
        return "WARN"
    
    # Otherwise ALLOW
    return "ALLOW"

