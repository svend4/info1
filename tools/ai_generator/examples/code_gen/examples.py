#!/usr/bin/env python3
"""
Code Generation Examples - Multi-Model, Figma to Code, OpenAPI to Backend
"""

from pathlib import Path
from tools.ai_generator.code_gen import (
    MultiModelGenerator, AIModel,
    FigmaToCodeConverter, UIFramework,
    OpenAPIBackendGenerator, BackendFramework
)


def example_multi_model_generation():
    """Generate code using AI model ensemble"""
    print("=" * 60)
    print("Multi-Model Code Generation")
    print("=" * 60)

    generator = MultiModelGenerator(models=[AIModel.GPT4, AIModel.CLAUDE, AIModel.CODEX])

    code = generator.generate_from_prompt(
        prompt="Create a user authentication service with JWT tokens and password hashing",
        language="python",
        framework="fastapi"
    )

    print(f"✅ Generated authentication service")
    print(f"   Models: GPT-4, Claude, Codex")
    print(f"   Language: Python (FastAPI)")
    print(f"   Consensus score: {code.consensus_score:.2f}")
    print()


def example_figma_to_react():
    """Convert Figma design to React components"""
    print("=" * 60)
    print("Figma to React Conversion")
    print("=" * 60)

    converter = FigmaToCodeConverter(framework=UIFramework.REACT)

    components = converter.convert_figma_file(
        figma_url="https://www.figma.com/file/ABC123/Dashboard",
        component_library="material-ui"
    )

    print(f"✅ Generated {len(components)} React components")
    print(f"   Components: {', '.join(components.keys())}")
    print(f"   Library: Material-UI")
    print()


def example_openapi_to_fastapi():
    """Generate FastAPI backend from OpenAPI spec"""
    print("=" * 60)
    print("OpenAPI to FastAPI Backend")
    print("=" * 60)

    generator = OpenAPIBackendGenerator(framework=BackendFramework.FASTAPI)

    files = generator.generate_from_spec(
        openapi_spec="./specs/petstore.yaml",
        output_dir=Path("./output/petstore-api"),
        database="postgresql",
        enable_auth=True
    )

    print(f"✅ Generated FastAPI backend")
    print(f"   Files: {len(files)}")
    print(f"   Database: PostgreSQL")
    print(f"   Auth: Enabled")
    print()


if __name__ == "__main__":
    print("\n💻 Code Generation Examples\n")
    example_multi_model_generation()
    example_figma_to_react()
    example_openapi_to_fastapi()
    print("✅ All code generation examples completed!\n")
