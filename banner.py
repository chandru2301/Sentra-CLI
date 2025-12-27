"""Optional ASCII banner for Sentra."""
from console import console


def print_banner():
    """Print Sentra banner (Gemini-style, but Sentra).
    
    Keep it simple and readable. Enterprise users prefer clean by default.
    """
    console.print()
    console.print("▶ SENTRA", style="primary.bold")
    console.print("Policy gate for AI-assisted code", style="muted")
    console.print()

