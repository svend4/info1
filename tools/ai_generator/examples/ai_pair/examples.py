#!/usr/bin/env python3
"""
AI Pair Programming Examples - Code Completion, Collaboration, Review, Refactoring
"""

from pathlib import Path
from tools.ai_generator.ai_pair import (
    CodeCompletionEngine, CompletionConfig,
    RealtimeCollaboration,
    CodeReviewAssistant,
    IntelligentRefactoring
)


def example_code_completion():
    """Context-aware code completion"""
    print("=" * 60)
    print("Code Completion Engine")
    print("=" * 60)

    config = CompletionConfig(
        model="gpt-4",
        context_window=8000,
        enable_multiline=True
    )

    engine = CodeCompletionEngine(config)

    suggestions = engine.get_completions(
        code="def calculate_fibonacci(n: int) ->",
        language="python",
        cursor_position=37
    )

    print(f"✅ Generated {len(suggestions)} completions")
    print(f"   Model: GPT-4")
    print(f"   Context: 8000 tokens")
    print(f"   Top suggestion: {suggestions[0][:50]}...")
    print()


def example_realtime_collaboration():
    """Real-time pair programming session"""
    print("=" * 60)
    print("Real-Time Collaboration")
    print("=" * 60)

    collab = RealtimeCollaboration()

    session = collab.create_session(
        project_name="web-app",
        participants=["alice@example.com", "bob@example.com"]
    )

    print(f"✅ Collaboration session created")
    print(f"   Session ID: {session.id}")
    print(f"   Participants: 2")
    print(f"   Protocol: WebSocket")
    print()


def example_code_review():
    """Automated code review"""
    print("=" * 60)
    print("Code Review Assistant")
    print("=" * 60)

    reviewer = CodeReviewAssistant()

    review = reviewer.review_code(
        file_path=Path("./src/api.py"),
        check_security=True,
        check_performance=True,
        check_best_practices=True
    )

    print(f"✅ Code review completed")
    print(f"   Issues found: {review.total_issues}")
    print(f"   Critical: {review.critical_count}")
    print(f"   Suggestions: {review.suggestion_count}")
    print()


def example_intelligent_refactoring():
    """Intelligent code refactoring"""
    print("=" * 60)
    print("Intelligent Refactoring")
    print("=" * 60)

    refactorer = IntelligentRefactoring()

    suggestions = refactorer.analyze_and_suggest(
        file_path=Path("./src/legacy_code.py"),
        refactoring_types=["extract_method", "rename", "simplify"]
    )

    print(f"✅ Refactoring analysis completed")
    print(f"   Suggestions: {len(suggestions)}")
    print(f"   Safe transformations: {sum(1 for s in suggestions if s.is_safe)}")
    print()


if __name__ == "__main__":
    print("\n🧑‍💻 AI Pair Programming Examples\n")
    example_code_completion()
    example_realtime_collaboration()
    example_code_review()
    example_intelligent_refactoring()
    print("✅ All AI pair programming examples completed!\n")
