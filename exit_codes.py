"""Exit codes for CLI."""
from typing import Dict


def get_exit_code(risk_level: str) -> int:
    """Map risk level to exit code.
    
    Exit codes:
    0 - Safe (LOW risk)
    1 - Warning (MEDIUM risk)
    2 - Block (HIGH risk)
    """
    mapping = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
    }
    return mapping.get(risk_level, 1)

