"""
Advanced Code Generation Package

Multi-model code generation, UI to code, API generation, refactoring, и documentation.
"""

from .multi_model_generator import (
    MultiModelCodeGenerator,
    CodeGenerationRequest,
    CodeGenerationResult,
    AIModel,
    CodeLanguage,
    GenerationStrategy,
    ModelResponse
)

from .figma_to_code import (
    FigmaToCodeConverter,
    FigmaNode,
    GeneratedComponent,
    ConversionResult,
    FrameworkType,
    ComponentType
)

from .openapi_to_backend import (
    OpenAPIToBackendGenerator,
    GeneratedBackend,
    APIEndpoint,
    APISchema,
    BackendFramework,
    HTTPMethod
)

from .refactoring_engine import (
    AdvancedRefactoringEngine,
    RefactoringResult,
    CodeIssue,
    RefactoringType,
    CodeIssueType
)

from .doc_generator import (
    DocumentationGenerator,
    ModuleDoc,
    ClassDoc,
    FunctionDoc,
    DocStyle,
    DocFormat
)

__all__ = [
    # Multi-Model Generator
    'MultiModelCodeGenerator',
    'CodeGenerationRequest',
    'CodeGenerationResult',
    'AIModel',
    'CodeLanguage',
    'GenerationStrategy',
    'ModelResponse',

    # Figma to Code
    'FigmaToCodeConverter',
    'FigmaNode',
    'GeneratedComponent',
    'ConversionResult',
    'FrameworkType',
    'ComponentType',

    # OpenAPI to Backend
    'OpenAPIToBackendGenerator',
    'GeneratedBackend',
    'APIEndpoint',
    'APISchema',
    'BackendFramework',
    'HTTPMethod',

    # Refactoring Engine
    'AdvancedRefactoringEngine',
    'RefactoringResult',
    'CodeIssue',
    'RefactoringType',
    'CodeIssueType',

    # Documentation Generator
    'DocumentationGenerator',
    'ModuleDoc',
    'ClassDoc',
    'FunctionDoc',
    'DocStyle',
    'DocFormat'
]

__version__ = '1.0.0'
