"""
AI Enhancements Package

AI-powered улучшения для генерации и анализа кода.
"""

from .gpt4_integration import (
    GPT4Integration,
    GPT4Model,
    GenerationTask,
    GPT4Request,
    GPT4Response,
    generate_code,
    review_code,
    generate_tests
)

from .code_reviewer import (
    CodeReviewer,
    CodeIssue,
    ReviewResult,
    IssueSeverity,
    IssueCategory
)

from .test_generator import (
    TestGenerator,
    TestFramework,
    TestType,
    TestCase,
    TestSuite
)

from .performance_optimizer import (
    PerformanceOptimizer,
    PerformanceIssue,
    OptimizationReport,
    OptimizationType
)

from .bug_predictor import (
    BugPredictor,
    BugPrediction,
    BugReport,
    BugType,
    BugSeverity
)

from .refactoring_engine import (
    RefactoringEngine,
    RefactoringOperation,
    RefactoringPlan,
    RefactoringType
)

__all__ = [
    # GPT-4 Integration
    'GPT4Integration',
    'GPT4Model',
    'GenerationTask',
    'GPT4Request',
    'GPT4Response',
    'generate_code',
    'review_code',
    'generate_tests',

    # Code Reviewer
    'CodeReviewer',
    'CodeIssue',
    'ReviewResult',
    'IssueSeverity',
    'IssueCategory',

    # Test Generator
    'TestGenerator',
    'TestFramework',
    'TestType',
    'TestCase',
    'TestSuite',

    # Performance Optimizer
    'PerformanceOptimizer',
    'PerformanceIssue',
    'OptimizationReport',
    'OptimizationType',

    # Bug Predictor
    'BugPredictor',
    'BugPrediction',
    'BugReport',
    'BugType',
    'BugSeverity',

    # Refactoring Engine
    'RefactoringEngine',
    'RefactoringOperation',
    'RefactoringPlan',
    'RefactoringType'
]

__version__ = '1.0.0'
