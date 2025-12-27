"""Setup configuration for sentra."""
from setuptools import setup, find_packages

setup(
    name="sentra",
    version="0.1.0",
    description="CLI tool that analyzes git diffs and decides whether a PR is safe to merge",
    author="Sentra Team",
    py_modules=["cli", "diff_reader", "risk_engine", "report", "exit_codes", "version", "theme", "console", "banner"],
    packages=["rules"],
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sentra=cli:main",
        ],
    },
    python_requires=">=3.7",
)

