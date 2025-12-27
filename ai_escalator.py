"""AI escalator for MEDIUM severity rules.

AI can only escalate MEDIUM to HIGH or CRITICAL.
AI cannot downgrade, decide, or affect non-MEDIUM rules.
"""
import os
import requests
from typing import Optional


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("AI_ESCALATOR_MODEL", "")
ENABLED = os.getenv("AI_ESCALATOR_ENABLED", "false").lower() == "true"
TIMEOUT = int(os.getenv("AI_ESCALATOR_TIMEOUT", "5"))


def is_ai_enabled() -> bool:
    """Check if AI escalation is enabled and properly configured.
    
    Returns:
        True if AI escalation is enabled, False otherwise
    """
    return ENABLED and bool(OPENROUTER_API_KEY) and bool(MODEL)


def ai_escalate(message: str) -> Optional[str]:
    """
    Escalate MEDIUM severity rule to HIGH or CRITICAL.
    
    Returns one of: "HIGH", "CRITICAL", or None (means keep original severity).
    Never returns "LOW" or "MEDIUM".
    
    Args:
        message: The rule message to evaluate
        
    Returns:
        "HIGH", "CRITICAL", or None (KEEP)
    """
    if not ENABLED or not OPENROUTER_API_KEY or not MODEL:
        return None

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a security risk escalator.\n"
                            "Input: a code change summary.\n"
                            "Output ONLY one token:\n"
                            "- HIGH\n"
                            "- CRITICAL\n"
                            "- KEEP\n"
                            "Rules:\n"
                            "- NEVER explain\n"
                            "- NEVER downgrade risk\n"
                            "- If unsure, return KEEP"
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            },
            timeout=TIMEOUT,
        )

        content = response.json()["choices"][0]["message"]["content"].strip()

        if content in ("HIGH", "CRITICAL"):
            return content

        return None  # KEEP

    except Exception:
        # AI failure must NEVER break the scan
        return None

