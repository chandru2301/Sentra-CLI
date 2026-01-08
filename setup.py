from setuptools import setup, find_packages

setup(
    name="sentra",
    version="0.1.0",
    description="Deterministic safety gate for code changes",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sentra",
    author_email="contact@sentra.dev",
    url="https://github.com/your-org/sentra",
    license="Apache-2.0",
    py_modules=["cli", "diff_reader", "risk_engine", "report", "exit_codes", "version", "theme", "console", "banner", "decision", "policy_engine", "policy_loader", "git_utils", "license", "ai_escalator"],
    packages=["rules"],
    install_requires=[
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "sentra=cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
