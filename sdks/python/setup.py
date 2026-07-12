"""
OverseeX Python SDK

The complete testing & monitoring platform for AI agents.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="overseex",
    version="0.2.4",
    author="OverseeX Team",
    author_email="support@overseex.com",
    description="OverseeX SDK - Testing & monitoring platform for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/overseex/overseex-python",
    project_urls={
        "Documentation": "https://docs.overseex.com",
        "Bug Reports": "https://github.com/overseex/overseex-python/issues",
        "Source": "https://github.com/overseex/overseex-python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "crewai": ["overseex-crewai>=0.1.0"],
        "langchain": ["overseex-langchain>=0.1.0"],
        "all": [
            "overseex-crewai>=0.1.0",
            "overseex-langchain>=0.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
    },
    keywords="ai agents testing monitoring tracing overseex llm multi-agent coordination",
)
