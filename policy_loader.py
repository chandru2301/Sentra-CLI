"""Load and parse policy configuration files."""
import yaml
import os
from typing import Dict


DEFAULT_POLICY = {
    "version": None,  # None means no policy file exists
    "defaults": {
        "allow_severity": "LOW",
        "block_severity": "HIGH"
    }
}


def load_policy(path: str = "policy.yaml") -> Dict:
    """Load policy from YAML file.
    
    If policy file doesn't exist, returns safe defaults with version=None.
    Policy absence should never break the scan.
    
    Args:
        path: Path to policy.yaml file
        
    Returns:
        Policy dictionary with version=None if file missing, or loaded policy if file exists
    """
    if not os.path.exists(path):
        return DEFAULT_POLICY.copy()
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            policy = yaml.safe_load(f)
            if not policy:
                return DEFAULT_POLICY.copy()
            
            # Merge with defaults to ensure required fields exist
            merged = DEFAULT_POLICY.copy()
            merged.update(policy)
            # Ensure defaults exist
            if "defaults" not in merged:
                merged["defaults"] = DEFAULT_POLICY["defaults"]
            else:
                # Merge defaults
                merged["defaults"] = {**DEFAULT_POLICY["defaults"], **merged["defaults"]}
            
            # Ensure version is set if file exists
            if merged.get("version") is None:
                merged["version"] = 1
            
            return merged
    except Exception:
        # Policy load failure should never break the scan
        return DEFAULT_POLICY.copy()
