"""
Setup script for ai-api-wrapper.

This file exists for backward compatibility with older pip versions and
development workflows that expect a setup.py file.

Most of the actual configuration is in pyproject.toml.
"""

from setuptools import setup

if __name__ == "__main__":
    # The actual configuration is in pyproject.toml
    # This just provides a hook for pip install -e . and similar commands
    setup(
        name="ai-api-wrapper",
        description="A unified wrapper for various AI API services",
        author="James Ding",
        author_email="xingshizhai@gmail.com",
        packages=["ai_api_wrapper"],
        package_dir={"": "src"},
        python_requires=">=3.12",
    )