"""Sentra theme definition - single source of truth for colors."""
from rich.theme import Theme

# Sentra brand color: #9D4EDD (purple)
# Tone: confident, modern, AI-native
# Usage: headers, decisions, highlights (not everything)
# Rule: Purple for identity, not noise

SENTRA_THEME = Theme({
    "primary": "#9D4EDD",           # Brand purple for identity
    "primary.bold": "bold #9D4EDD",  # Brand purple, bold (for headers)
    "success": "green",              # ALLOW decisions
    "warn": "yellow",                # WARN decisions
    "error": "red",                  # BLOCK decisions
    "muted": "grey50",               # Secondary text
    "rule": "bold #9D4EDD",          # Section headers (purple, bold)
    "info": "blue",                  # Informational messages
})

