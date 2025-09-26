"""Setup configuration for UFC scraper."""
from setuptools import setup, find_packages

setup(
    name="ufc-scraper",
    version="2.0.0",
    description="Professional UFC statistics scraper",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "pytest>=7.0.0",
        "pytest-mock>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ufc-scraper=src.pipeline.orchestrator:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)