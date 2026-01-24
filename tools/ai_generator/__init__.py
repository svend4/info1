"""
AI-powered Project Generator

Интеллектуальная генерация проектов на основе естественного языка.
ЭТАП 9: AI-assisted Project Generation

Уровень абстракции: α=-4 (исполняемый код)
"""

__version__ = "0.1.0"
__author__ = "info1 Project"

from .nlp_parser import NLPParser
from .classifier import ProjectClassifier

__all__ = ['NLPParser', 'ProjectClassifier']
