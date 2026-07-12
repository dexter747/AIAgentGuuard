"""
AgentGuard Python SDK Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="overseex",
    version="1.0.0",
    author="OverseeX Team",
    author_email="support@overseex.com",
    description="Official Python SDK for OverseeX - AI Agent Testing & Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/overseex/python-sdk",
    project_urls={
        "Homepage": "https://overseex.com",
        "Documentation": "https://docs.overseex.com",
        "Source": "https://github.com/overseex/python-sdk",
        "Bug Reports": "https://github.com/overseex/python-sdk/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
)
