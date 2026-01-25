"""
AI Generator Toolkit - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "tools" / "ai_generator" / "README.md").read_text()

setup(
    name="ai-generator-toolkit",
    version="1.0.0",
    author="AI Development Team",
    author_email="dev@example.com",
    description="Comprehensive AI-powered development automation toolkit for modern software engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/info1",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies will be read from requirements.txt
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "security": [
            "cryptography>=41.0.0",
            "pyjwt>=2.8.0",
        ],
        "mlops": [
            "mlflow>=2.9.0",
            "scipy>=1.11.0",
            "numpy>=1.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-generator=tools.ai_generator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
