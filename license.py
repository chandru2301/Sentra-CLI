"""License tier checking and enforcement."""
import os
from typing import Optional, Literal


LicenseTier = Literal["free", "pro"]


def get_license_tier() -> LicenseTier:
    """Determine license tier from environment variable.
    
    Checks SENTRA_LICENSE_KEY environment variable:
    - If set and non-empty: Pro tier
    - If not set or empty: Free tier
    
    Returns:
        "pro" or "free"
    """
    license_key = os.getenv("SENTRA_LICENSE_KEY", "").strip()
    
    if license_key:
        return "pro"
    return "free"


def should_enforce_block(license_tier: LicenseTier) -> bool:
    """Determine if BLOCK decisions should be enforced based on license tier.
    
    Args:
        license_tier: "pro" or "free"
        
    Returns:
        True if BLOCK should be enforced (Pro tier), False if downgraded to WARN (Free tier)
    """
    return license_tier == "pro"


def get_upgrade_message() -> str:
    """Get upgrade messaging for Free tier users when BLOCK is downgraded.
    
    Returns:
        Message explaining that BLOCK enforcement requires Pro tier
    """
    return "Note: BLOCK enforcement requires Pro tier. Upgrade to enable merge blocking."

