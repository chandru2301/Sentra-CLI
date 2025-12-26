"""Rule 5: Check if tests were added with production code changes."""
from typing import Dict, List
import re


def check_test_coverage(changed_files: List[str], diff_data: Dict) -> Dict:
    """Check if production code changed without corresponding tests.
    
    Risk: MEDIUM
    """
    test_patterns = [
        r'.*test.*',
        r'.*spec.*',
        r'.*__tests__.*',
        r'.*\.test\.',
        r'.*\.spec\.',
    ]
    
    production_files = []
    test_files = []
    
    # Common production file extensions
    prod_extensions = ['.py', '.java', '.js', '.ts', '.go', '.rs', '.cpp', '.c']
    # But exclude test files
    test_extensions = ['.test.', '.spec.', '_test.', '_spec.']
    
    for filepath in changed_files:
        filepath_lower = filepath.lower()
        
        # Check if it's a test file
        is_test = False
        for pattern in test_patterns:
            if re.search(pattern, filepath_lower):
                test_files.append(filepath)
                is_test = True
                break
        
        # Check for test extensions
        for ext in test_extensions:
            if ext in filepath_lower:
                test_files.append(filepath)
                is_test = True
                break
        
        # If not a test file, check if it's production code
        if not is_test:
            # Check if it has a production extension
            has_prod_ext = any(filepath.endswith(ext) for ext in prod_extensions)
            # Exclude config, docs, etc.
            is_config = any(x in filepath_lower for x in ['.yml', '.yaml', '.json', '.md', '.txt', '.properties'])
            
            if has_prod_ext and not is_config:
                production_files.append(filepath)
    
    if production_files and not test_files:
        return {
            "triggered": True,
            "risk": "MEDIUM",
            "files": production_files,
            "reason": f"Production code changed ({len(production_files)} files) but no test files updated"
        }
    
    return {
        "triggered": False,
        "risk": "LOW",
        "files": [],
        "reason": None
    }

