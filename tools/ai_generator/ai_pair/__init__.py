"""
AI Pair Programming Package

Real-time code completion, collaborative editing, code review, и intelligent refactoring.
"""

from .code_completion_engine import (
    CodeCompletionEngine,
    CompletionContext,
    CompletionSuggestion,
    CompletionResult,
    CompletionType,
    ConfidenceLevel
)

from .realtime_collaboration import (
    RealtimeCollaborationServer,
    RealtimeCollaborationClient,
    CollaborationSession,
    StreamingSuggestion,
    EditorEvent,
    MessageType,
    EditorAction
)

from .code_review_assistant import (
    CodeReviewAssistant,
    CodeReviewResult,
    ReviewIssue,
    ReviewSuggestion,
    ReviewSeverity,
    ReviewCategory
)

from .intelligent_refactoring import (
    IntelligentRefactoringAssistant,
    RefactoringAction,
    RefactoringResult,
    RefactoringType,
    RefactoringSafety,
    CodeRange
)

__all__ = [
    # Code Completion Engine
    'CodeCompletionEngine',
    'CompletionContext',
    'CompletionSuggestion',
    'CompletionResult',
    'CompletionType',
    'ConfidenceLevel',

    # Realtime Collaboration
    'RealtimeCollaborationServer',
    'RealtimeCollaborationClient',
    'CollaborationSession',
    'StreamingSuggestion',
    'EditorEvent',
    'MessageType',
    'EditorAction',

    # Code Review Assistant
    'CodeReviewAssistant',
    'CodeReviewResult',
    'ReviewIssue',
    'ReviewSuggestion',
    'ReviewSeverity',
    'ReviewCategory',

    # Intelligent Refactoring
    'IntelligentRefactoringAssistant',
    'RefactoringAction',
    'RefactoringResult',
    'RefactoringType',
    'RefactoringSafety',
    'CodeRange'
]

__version__ = '1.0.0'
