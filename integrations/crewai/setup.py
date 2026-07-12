"""
OverseeX CrewAI Integration

Auto-instrumentation for CrewAI multi-agent workflows.
"""
from setuptools import setup, find_packages

setup(
    name="overseex-crewai",
    version="0.1.0",
    description="OverseeX integration for CrewAI - automatic trace capture for multi-agent workflows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="OverseeX Team",
    author_email="support@overseex.com",
    url="https://github.com/overseex/overseex-crewai",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "crewai>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="crewai ai agents monitoring tracing overseex",
)
