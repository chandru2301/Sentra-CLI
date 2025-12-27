"""Exit codes for CLI."""
from typing import Dict


def get_exit_code(decision: str) -> int:
    """Map decision to exit code.
    
    Exit codes:
    0 - Safe (ALLOW or WARN)
    1 - Block (BLOCK decision)
    """
    mapping = {
        "ALLOW": 0,
        "WARN": 0,
        "BLOCK": 1,
    }
    return mapping.get(decision, 0)

