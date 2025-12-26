"""Rule 1: Detect changes to sensitive files."""
from typing import Dict, List
import re


def check_sensitive_files(changed_files: List[str], diff_data: Dict) -> Dict:
    """Check if diff touches sensitive files.
    
    Risk: MEDIUM to HIGH
    """
    sensitive_patterns = [
        r'.*security.*',
        r'.*auth.*',
        r'.*gateway.*',
        r'.*config.*',
        r'.*application\.yml',
        r'.*application\.yaml',
        r'.*\.properties$',
    ]
    
    sensitive_keywords = ['security', 'auth', 'gateway', 'config']
    
    matched_files = []
    risk_level = "LOW"
    
    for filepath in changed_files:
        filepath_lower = filepath.lower()
        
        # Check patterns
        for pattern in sensitive_patterns:
            if re.match(pattern, filepath_lower):
                matched_files.append(filepath)
                risk_level = "MEDIUM"
                break
        
        # Check keywords in path
        for keyword in sensitive_keywords:
            if keyword in filepath_lower:
                if filepath not in matched_files:
                    matched_files.append(filepath)
                risk_level = "MEDIUM"
                break
        
        # Check for application.yml or .properties
        if filepath.endswith('.properties') or 'application.yml' in filepath or 'application.yaml' in filepath:
            if filepath not in matched_files:
                matched_files.append(filepath)
            risk_level = "HIGH"  # Config files are high risk
    
    if matched_files:
        # If multiple sensitive files, escalate to HIGH
        if len(matched_files) > 1:
            risk_level = "HIGH"
        
        return {
            "triggered": True,
            "risk": risk_level,
            "files": matched_files,
            "reason": f"Modified sensitive files: {', '.join(matched_files[:3])}" + 
                     (f" and {len(matched_files) - 3} more" if len(matched_files) > 3 else "")
        }
    
    return {
        "triggered": False,
        "risk": "LOW",
        "files": [],
        "reason": None
    }

