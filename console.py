"""Sentra console - centrally themed output."""
import os
from rich.console import Console
from theme import SENTRA_THEME

# Respect NO_COLOR standard (enterprise requirement)
# rich automatically handles NO_COLOR environment variable
# Also disable colors for JSON output (handled in CLI)

console = Console(theme=SENTRA_THEME)

