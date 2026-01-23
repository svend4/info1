#!/usr/bin/env python3
"""
Setup script для карточной системы
Информационно-операционная система для домашнего использования

Установка:
    pip install -e .                # Базовая установка
    pip install -e .[web]           # С веб-фреймворком
    pip install -e .[bot]           # С Telegram-ботом
    pip install -e .[dev]           # Для разработки
    pip install -e .[all]           # Всё вместе
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README для длинного описания
readme_file = Path(__file__).parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Читаем requirements.txt для зависимостей
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
extras_require = {
    "web": ["flask>=2.0.0"],
    "bot": ["python-telegram-bot>=13.0"],
    "test": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    "dev": ["black>=22.0.0", "flake8>=4.0.0", "mypy>=0.950"],
    "docs": ["sphinx>=4.0.0", "sphinx-rtd-theme>=1.0.0"],
}
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="card-system",
    version="1.0.0",
    author="Claude & User",
    author_email="",
    description="Информационно-операционная система для домашнего использования на основе карточек",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svend4/info1",
    packages=find_packages(where="card_system"),
    package_dir={"": "card_system"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,  # Базовая система не требует внешних зависимостей
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "card-cli=cli:main",
            "card-demo=demo:main",
            "card-automation=automation:main",
        ],
    },
    include_package_data=True,
    package_data={
        "card_system": [
            "*.py",
            "*.md",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/svend4/info1/issues",
        "Documentation": "https://github.com/svend4/info1/blob/main/08-Программная-реализация/API-REFERENCE.md",
        "Source": "https://github.com/svend4/info1",
    },
    keywords="cards task-management medicine-tracking home-automation elderly-care",
    zip_safe=False,
)
