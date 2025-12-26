"""Setup configuration for ai-safety."""
from setuptools import setup, find_packages

setup(
    name="ai-safety",
    version="0.1.0",
    description="CLI tool that analyzes git diffs and decides whether a PR is safe to merge",
    author="AI Safety Team",
    py_modules=["cli", "diff_reader", "risk_engine", "report", "exit_codes"],
    packages=["rules"],
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ai-safety=cli:main",
        ],
    },
    python_requires=">=3.7",
)

