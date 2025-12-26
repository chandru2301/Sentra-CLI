"""Rule 2: Detect cross-service changes."""
from typing import Dict, List
import re


def check_cross_service(changed_files: List[str], diff_data: Dict) -> Dict:
    """Check if PR touches multiple services or shared modules.
    
    Risk: MEDIUM
    """
    # Common service/module patterns
    service_patterns = [
        r'.*service.*',
        r'.*api.*',
        r'.*gateway.*',
        r'.*auth.*',
        r'.*identity.*',
        r'.*payment.*',
        r'.*order.*',
        r'.*user.*',
        r'.*product.*',
    ]
    
    shared_patterns = [
        r'.*common.*',
        r'.*shared.*',
        r'.*lib.*',
        r'.*library.*',
        r'.*util.*',
        r'.*utils.*',
    ]
    
    services_touched = set()
    shared_modules_touched = []
    
    for filepath in changed_files:
        filepath_lower = filepath.lower()
        
        # Check for services
        for pattern in service_patterns:
            if re.search(pattern, filepath_lower):
                # Extract service name (simple heuristic)
                parts = filepath.split('/')
                for part in parts:
                    if any(p in part.lower() for p in ['service', 'api', 'gateway', 'auth', 'identity']):
                        services_touched.add(part)
                break
        
        # Check for shared modules
        for pattern in shared_patterns:
            if re.search(pattern, filepath_lower):
                shared_modules_touched.append(filepath)
                break
    
    # Heuristic: if file structure suggests multiple services
    # (e.g., different top-level directories that look like services)
    top_level_dirs = set()
    for filepath in changed_files:
        parts = filepath.split('/')
        if len(parts) > 1:
            top_level_dirs.add(parts[0])
    
    # If we have multiple distinct top-level directories, likely cross-service
    if len(top_level_dirs) > 1:
        # Filter out common non-service dirs
        non_service_dirs = {'src', 'test', 'tests', 'docs', 'scripts', 'config', '.github'}
        service_dirs = top_level_dirs - non_service_dirs
        if len(service_dirs) > 1:
            services_touched.update(service_dirs)
    
    reasons = []
    if len(services_touched) > 1:
        reasons.append(f"Touches multiple services: {', '.join(list(services_touched)[:3])}")
    
    if shared_modules_touched:
        reasons.append(f"Modified shared modules: {', '.join(shared_modules_touched[:2])}")
    
    if reasons:
        return {
            "triggered": True,
            "risk": "MEDIUM",
            "files": changed_files,
            "reason": "; ".join(reasons)
        }
    
    return {
        "triggered": False,
        "risk": "LOW",
        "files": [],
        "reason": None
    }

