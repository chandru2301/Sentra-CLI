"""Git utility functions for preflight checks."""
import subprocess


def ensure_git_available():
    """Check if git is installed and available in PATH.
    
    Raises:
        RuntimeError: If git is not available, with message "GIT_NOT_AVAILABLE"
    """
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception:
        raise RuntimeError("GIT_NOT_AVAILABLE")

