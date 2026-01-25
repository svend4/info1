#!/usr/bin/env python3
"""
Multi-Model Code Generator

Ensemble code generation using multiple AI models (GPT-4, Claude, Codex) для improved quality.
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class AIModel(Enum):
    """AI Model Types"""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    CLAUDE_OPUS = "claude-opus-4"
    CLAUDE_SONNET = "claude-sonnet-3-5"
    CODEX = "codex"
    CODEGEMINI = "code-gemini-pro"


class CodeLanguage(Enum):
    """Programming Languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"


class GenerationStrategy(Enum):
    """Code Generation Strategy"""
    BEST_OF_N = "best_of_n"  # Generate N versions, pick best
    ENSEMBLE_VOTING = "ensemble_voting"  # Combine outputs via voting
    SEQUENTIAL_REFINEMENT = "sequential_refinement"  # Each model refines previous
    PARALLEL_MERGE = "parallel_merge"  # Generate in parallel, merge best parts


@dataclass
class CodeGenerationRequest:
    """Code Generation Request"""
    prompt: str
    language: CodeLanguage
    context: str = ""
    requirements: List[str] = field(default_factory=list)
    max_tokens: int = 2000
    temperature: float = 0.2
    style_guide: Optional[str] = None  # e.g., "PEP8", "Google", "Airbnb"


@dataclass
class ModelResponse:
    """Individual Model Response"""
    model: AIModel
    code: str
    confidence_score: float  # 0-1
    execution_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeGenerationResult:
    """Code Generation Result"""
    request_id: str
    prompt: str
    language: CodeLanguage
    strategy: GenerationStrategy
    final_code: str
    quality_score: float  # 0-100
    model_responses: List[ModelResponse]
    reasoning: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generation_time_ms: float = 0.0


class MultiModelCodeGenerator:
    """Multi-Model Ensemble Code Generator"""

    def __init__(self, api_keys: Dict[str, str]):
        """
        Инициализация multi-model generator

        Args:
            api_keys: Dictionary of model_name -> api_key
        """
        self.api_keys = api_keys
        self.generation_history: List[CodeGenerationResult] = []

        # Model weights for voting (based on empirical performance)
        self.model_weights = {
            AIModel.GPT4: 1.0,
            AIModel.GPT4_TURBO: 0.95,
            AIModel.CLAUDE_OPUS: 1.0,
            AIModel.CLAUDE_SONNET: 0.9,
            AIModel.CODEX: 0.85,
            AIModel.CODEGEMINI: 0.8
        }

    def generate(self,
                request: CodeGenerationRequest,
                models: List[AIModel],
                strategy: GenerationStrategy = GenerationStrategy.BEST_OF_N) -> CodeGenerationResult:
        """
        Generate code using multiple models

        Args:
            request: Code generation request
            models: List of models to use
            strategy: Generation strategy

        Returns:
            Code generation result
        """
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(request)

        print(f"🤖 Generating code with {len(models)} models ({strategy.value})")

        # Generate with each model
        model_responses = []
        for model in models:
            print(f"  → {model.value}...")
            response = self._generate_with_model(model, request)
            model_responses.append(response)

        # Apply strategy to get final code
        if strategy == GenerationStrategy.BEST_OF_N:
            final_code, quality_score, reasoning = self._best_of_n(model_responses)
        elif strategy == GenerationStrategy.ENSEMBLE_VOTING:
            final_code, quality_score, reasoning = self._ensemble_voting(model_responses, request)
        elif strategy == GenerationStrategy.SEQUENTIAL_REFINEMENT:
            final_code, quality_score, reasoning = self._sequential_refinement(model_responses, request)
        elif strategy == GenerationStrategy.PARALLEL_MERGE:
            final_code, quality_score, reasoning = self._parallel_merge(model_responses, request)
        else:
            final_code = model_responses[0].code
            quality_score = model_responses[0].confidence_score * 100
            reasoning = "Single model generation"

        generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        result = CodeGenerationResult(
            request_id=request_id,
            prompt=request.prompt,
            language=request.language,
            strategy=strategy,
            final_code=final_code,
            quality_score=quality_score,
            model_responses=model_responses,
            reasoning=reasoning,
            generation_time_ms=generation_time
        )

        self.generation_history.append(result)

        print(f"✅ Generated {len(final_code)} chars (quality: {quality_score:.1f}/100) in {generation_time:.0f}ms")
        return result

    def _generate_with_model(self,
                            model: AIModel,
                            request: CodeGenerationRequest) -> ModelResponse:
        """Generate code with specific model"""
        start_time = datetime.utcnow()

        # Build prompt
        system_prompt = self._build_system_prompt(request)
        user_prompt = self._build_user_prompt(request)

        # Simulate API call (in production, use actual API)
        # For GPT-4: openai.ChatCompletion.create()
        # For Claude: anthropic.messages.create()
        # For Codex: openai.Completion.create()

        code = self._simulate_model_generation(model, system_prompt, user_prompt, request)

        # Calculate confidence score
        confidence_score = self._calculate_confidence(code, request)

        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return ModelResponse(
            model=model,
            code=code,
            confidence_score=confidence_score,
            execution_time_ms=execution_time,
            metadata={
                'tokens_used': len(code.split()),
                'lines_of_code': len(code.split('\n'))
            }
        )

    def _best_of_n(self, responses: List[ModelResponse]) -> Tuple[str, float, str]:
        """Select best response based on confidence scores"""
        best_response = max(responses, key=lambda r: r.confidence_score)

        quality_score = best_response.confidence_score * 100

        reasoning = (
            f"Selected output from {best_response.model.value} "
            f"(confidence: {best_response.confidence_score:.2f}). "
            f"Evaluated {len(responses)} model outputs."
        )

        return best_response.code, quality_score, reasoning

    def _ensemble_voting(self,
                        responses: List[ModelResponse],
                        request: CodeGenerationRequest) -> Tuple[str, float, str]:
        """Combine responses via voting on code fragments"""
        # Extract common patterns from all responses
        code_fragments = self._extract_code_fragments(responses)

        # Vote on each fragment (weighted by model confidence)
        voted_fragments = []
        for fragment in code_fragments:
            votes = 0.0
            for response in responses:
                if fragment in response.code:
                    weight = self.model_weights.get(response.model, 1.0)
                    votes += response.confidence_score * weight

            voted_fragments.append((fragment, votes))

        # Sort by votes
        voted_fragments.sort(key=lambda x: x[1], reverse=True)

        # Construct final code from top voted fragments
        final_code = self._merge_fragments([f for f, v in voted_fragments], request.language)

        # Calculate quality
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        quality_score = avg_confidence * 100

        reasoning = (
            f"Ensemble voting across {len(responses)} models. "
            f"Combined {len(voted_fragments)} code fragments. "
            f"Average confidence: {avg_confidence:.2f}"
        )

        return final_code, quality_score, reasoning

    def _sequential_refinement(self,
                               responses: List[ModelResponse],
                               request: CodeGenerationRequest) -> Tuple[str, float, str]:
        """Each model refines the previous model's output"""
        # Start with first model's output
        current_code = responses[0].code
        refinement_steps = []

        for i, response in enumerate(responses[1:], 1):
            # Use response as refinement of current code
            # In production: send current_code + "refine this" to next model
            current_code = self._refine_code(current_code, response.code)
            refinement_steps.append(f"Step {i}: {response.model.value}")

        # Quality improves with each refinement
        quality_score = min(95, 70 + (len(responses) * 5))

        reasoning = (
            f"Sequential refinement through {len(responses)} models. "
            f"Steps: {' → '.join(refinement_steps)}"
        )

        return current_code, quality_score, reasoning

    def _parallel_merge(self,
                       responses: List[ModelResponse],
                       request: CodeGenerationRequest) -> Tuple[str, float, str]:
        """Merge best parts from each model's output"""
        # Analyze each response
        best_parts = {}

        for response in responses:
            parts = self._analyze_code_parts(response.code, request.language)

            for part_type, part_code in parts.items():
                if part_type not in best_parts:
                    best_parts[part_type] = (part_code, response.confidence_score)
                else:
                    # Keep part with higher confidence
                    if response.confidence_score > best_parts[part_type][1]:
                        best_parts[part_type] = (part_code, response.confidence_score)

        # Merge best parts
        final_code = self._merge_code_parts(best_parts, request.language)

        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        quality_score = avg_confidence * 100

        reasoning = (
            f"Parallel merge of {len(best_parts)} code parts from {len(responses)} models. "
            f"Selected best implementation for each part."
        )

        return final_code, quality_score, reasoning

    def _build_system_prompt(self, request: CodeGenerationRequest) -> str:
        """Build system prompt for model"""
        prompt = f"You are an expert {request.language.value} developer."

        if request.style_guide:
            prompt += f" Follow {request.style_guide} style guide."

        prompt += " Write clean, efficient, well-documented code."

        return prompt

    def _build_user_prompt(self, request: CodeGenerationRequest) -> str:
        """Build user prompt for model"""
        prompt = request.prompt

        if request.context:
            prompt = f"Context:\n{request.context}\n\nTask:\n{prompt}"

        if request.requirements:
            prompt += "\n\nRequirements:\n"
            for i, req in enumerate(request.requirements, 1):
                prompt += f"{i}. {req}\n"

        return prompt

    def _simulate_model_generation(self,
                                   model: AIModel,
                                   system_prompt: str,
                                   user_prompt: str,
                                   request: CodeGenerationRequest) -> str:
        """Simulate model code generation"""
        # In production, this would call actual APIs

        # Generate sample code based on language
        if request.language == CodeLanguage.PYTHON:
            code = self._generate_python_sample(request.prompt)
        elif request.language == CodeLanguage.JAVASCRIPT:
            code = self._generate_javascript_sample(request.prompt)
        elif request.language == CodeLanguage.TYPESCRIPT:
            code = self._generate_typescript_sample(request.prompt)
        else:
            code = f"// {request.prompt}\n// Generated by {model.value}"

        return code

    def _generate_python_sample(self, prompt: str) -> str:
        """Generate sample Python code"""
        if "sort" in prompt.lower():
            return '''def quick_sort(arr):
    """
    Quick sort implementation with O(n log n) average complexity.

    Args:
        arr: List of comparable elements

    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)
'''
        elif "api" in prompt.lower():
            return '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

items_db = []

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    """Create a new item"""
    items_db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
'''
        else:
            return f'''def process_data(data):
    """
    Process the input data.

    Args:
        data: Input data to process

    Returns:
        Processed result
    """
    # {prompt}
    result = data
    return result
'''

    def _generate_javascript_sample(self, prompt: str) -> str:
        """Generate sample JavaScript code"""
        return '''/**
 * Process data with async/await
 * @param {Array} data - Input data
 * @returns {Promise<Array>} Processed data
 */
async function processData(data) {
  try {
    const result = await Promise.all(
      data.map(async item => {
        // Process each item
        return item;
      })
    );
    return result;
  } catch (error) {
    console.error('Processing failed:', error);
    throw error;
  }
}
'''

    def _generate_typescript_sample(self, prompt: str) -> str:
        """Generate sample TypeScript code"""
        return '''interface Item {
  id: number;
  name: string;
  description?: string;
}

class DataProcessor {
  private items: Item[] = [];

  /**
   * Add item to processor
   */
  addItem(item: Item): void {
    this.items.push(item);
  }

  /**
   * Process all items
   */
  async processAll(): Promise<Item[]> {
    return Promise.all(
      this.items.map(item => this.processItem(item))
    );
  }

  private async processItem(item: Item): Promise<Item> {
    // Processing logic
    return item;
  }
}
'''

    def _calculate_confidence(self, code: str, request: CodeGenerationRequest) -> float:
        """Calculate confidence score for generated code"""
        score = 0.5  # Base score

        # Check for documentation
        if '"""' in code or '/*' in code or '//' in code:
            score += 0.1

        # Check for error handling
        if 'try' in code or 'catch' in code or 'except' in code:
            score += 0.1

        # Check for type hints (Python) or types (TypeScript)
        if '->' in code or ':' in code:
            score += 0.1

        # Check code length (reasonable implementation)
        lines = len(code.split('\n'))
        if 10 <= lines <= 200:
            score += 0.1

        # Check for tests or examples
        if 'test' in code.lower() or 'example' in code.lower():
            score += 0.1

        return min(1.0, score)

    def _extract_code_fragments(self, responses: List[ModelResponse]) -> List[str]:
        """Extract common code fragments"""
        # Simplified: split by functions/classes
        fragments = set()

        for response in responses:
            lines = response.code.split('\n')
            current_fragment = []

            for line in lines:
                if line.strip().startswith(('def ', 'class ', 'function ', 'const ')):
                    if current_fragment:
                        fragments.add('\n'.join(current_fragment))
                    current_fragment = [line]
                elif current_fragment:
                    current_fragment.append(line)

            if current_fragment:
                fragments.add('\n'.join(current_fragment))

        return list(fragments)

    def _merge_fragments(self, fragments: List[str], language: CodeLanguage) -> str:
        """Merge code fragments into coherent code"""
        return '\n\n'.join(fragments)

    def _refine_code(self, base_code: str, refinement: str) -> str:
        """Refine code based on another version"""
        # Simplified: prefer longer, more detailed version
        if len(refinement) > len(base_code):
            return refinement
        return base_code

    def _analyze_code_parts(self, code: str, language: CodeLanguage) -> Dict[str, str]:
        """Analyze and extract code parts"""
        parts = {}

        if language == CodeLanguage.PYTHON:
            if 'import' in code:
                parts['imports'] = '\n'.join([l for l in code.split('\n') if 'import' in l])
            if 'class ' in code:
                parts['classes'] = code  # Simplified
            if 'def ' in code:
                parts['functions'] = code  # Simplified

        return parts

    def _merge_code_parts(self, parts: Dict[str, Tuple[str, float]], language: CodeLanguage) -> str:
        """Merge code parts into final code"""
        merged = []

        # Order: imports, classes, functions
        for part_type in ['imports', 'classes', 'functions']:
            if part_type in parts:
                merged.append(parts[part_type][0])

        return '\n\n'.join(merged) if merged else list(parts.values())[0][0]

    def _generate_request_id(self, request: CodeGenerationRequest) -> str:
        """Generate unique request ID"""
        content = f"{request.prompt}{request.language.value}{datetime.utcnow()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_best_models_for_language(self, language: CodeLanguage) -> List[AIModel]:
        """Get recommended models for specific language"""
        # Empirical best models per language
        recommendations = {
            CodeLanguage.PYTHON: [AIModel.GPT4, AIModel.CLAUDE_OPUS, AIModel.CODEX],
            CodeLanguage.JAVASCRIPT: [AIModel.GPT4_TURBO, AIModel.CLAUDE_SONNET, AIModel.CODEX],
            CodeLanguage.TYPESCRIPT: [AIModel.GPT4_TURBO, AIModel.CLAUDE_OPUS, AIModel.CODEX],
            CodeLanguage.JAVA: [AIModel.GPT4, AIModel.CODEGEMINI, AIModel.CLAUDE_OPUS],
            CodeLanguage.GO: [AIModel.GPT4_TURBO, AIModel.CLAUDE_OPUS],
            CodeLanguage.RUST: [AIModel.GPT4, AIModel.CLAUDE_OPUS],
        }

        return recommendations.get(language, [AIModel.GPT4, AIModel.CLAUDE_OPUS])
