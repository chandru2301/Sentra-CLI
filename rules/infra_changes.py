"""Rule 3: Detect infrastructure configuration changes."""
from typing import Dict, List
import re


def check_infra_changes(changed_files: List[str], diff_data: Dict) -> Dict:
    """Check for infrastructure configuration changes.
    
    Detects:
    - Port changes
    - Eureka URLs
    - Environment variables
    - Docker files
    - CI files
    
    Risk: HIGH
    """
    infra_patterns = [
        r'.*dockerfile.*',
        r'.*docker-compose.*',
        r'.*\.env.*',
        r'.*\.env\.example.*',
        r'.*jenkinsfile.*',
        r'.*\.github/workflows/.*',
        r'.*\.gitlab-ci\.yml.*',
        r'.*\.circleci/.*',
        r'.*kubernetes.*',
        r'.*k8s.*',
        r'.*helm.*',
    ]
    
    matched_files = []
    infra_keywords = ['docker', 'ci', 'jenkins', 'kubernetes', 'helm', 'deploy']
    
    for filepath in changed_files:
        filepath_lower = filepath.lower()
        
        # Check patterns
        for pattern in infra_patterns:
            if re.match(pattern, filepath_lower):
                matched_files.append(filepath)
                break
        
        # Check keywords
        for keyword in infra_keywords:
            if keyword in filepath_lower:
                if filepath not in matched_files:
                    matched_files.append(filepath)
                break
    
    # Check diff content for port/eureka/env changes
    port_patterns = [
        r'port\s*[:=]\s*\d+',
        r':\d{4,5}',
        r'eureka\s*[:=]',
        r'eureka\.',
        r'server\.port',
    ]
    
    env_patterns = [
        r'env\s*[:=]',
        r'environment\s*[:=]',
        r'\$\{[A-Z_]+}',
    ]
    
    content_matches = []
    for filepath, file_data in diff_data.items():
        for chunk in file_data.get("chunks", []):
            for line_type, line_content in chunk.get("lines", []):
                if line_type in ("added", "removed"):
                    line_lower = line_content.lower()
                    
                    # Check for port changes
                    for pattern in port_patterns:
                        if re.search(pattern, line_lower, re.IGNORECASE):
                            if filepath not in matched_files:
                                matched_files.append(filepath)
                            content_matches.append("port configuration")
                            break
                    
                    # Check for Eureka
                    if 'eureka' in line_lower:
                        if filepath not in matched_files:
                            matched_files.append(filepath)
                        content_matches.append("Eureka configuration")
                    
                    # Check for env vars
                    for pattern in env_patterns:
                        if re.search(pattern, line_lower, re.IGNORECASE):
                            if filepath not in matched_files:
                                matched_files.append(filepath)
                            content_matches.append("environment variables")
                            break
    
    if matched_files or content_matches:
        reasons = []
        if matched_files:
            reasons.append(f"Modified infrastructure files: {', '.join(matched_files[:2])}")
        if content_matches:
            unique_matches = list(set(content_matches))
            reasons.append(f"Detected changes to: {', '.join(unique_matches)}")
        
        return {
            "triggered": True,
            "rule_id": "INFRA_CHANGE",
            "severity": "HIGH",
            "message": "; ".join(reasons),
            "files": matched_files,
            "risk": "HIGH",
            "reason": "; ".join(reasons)
        }
    
    return {
        "triggered": False,
        "rule_id": "INFRA_CHANGE",
        "severity": "LOW",
        "message": None,
        "files": [],
        "risk": "LOW",
        "reason": None
    }

