#!/usr/bin/env python3
"""
GPT-4 Integration Module

Интеграция с GPT-4 для улучшенной генерации кода, анализа и рефакторинга.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from datetime import datetime


class GPT4Model(Enum):
    """Доступные модели GPT-4"""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4_32K = "gpt-4-32k"
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"


class GenerationTask(Enum):
    """Типы задач генерации"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    BUG_ANALYSIS = "bug_analysis"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"


@dataclass
class GPT4Request:
    """Запрос к GPT-4"""
    task_type: GenerationTask
    prompt: str
    context: Dict[str, Any]
    model: GPT4Model = GPT4Model.GPT4_TURBO
    temperature: float = 0.7
    max_tokens: int = 4000
    user_id: Optional[str] = None
    organization_id: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['model'] = self.model.value
        return data


@dataclass
class GPT4Response:
    """Ответ от GPT-4"""
    request_id: str
    task_type: GenerationTask
    content: str
    model: GPT4Model
    tokens_used: int
    cost: float
    quality_score: float
    metadata: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['model'] = self.model.value
        return data


class GPT4Integration:
    """
    GPT-4 Integration Manager

    Управляет взаимодействием с GPT-4 API для различных задач генерации кода.
    """

    # Цены за 1K tokens (USD)
    PRICING = {
        GPT4Model.GPT4: {'input': 0.03, 'output': 0.06},
        GPT4Model.GPT4_TURBO: {'input': 0.01, 'output': 0.03},
        GPT4Model.GPT4_32K: {'input': 0.06, 'output': 0.12},
        GPT4Model.GPT4O: {'input': 0.005, 'output': 0.015},
        GPT4Model.GPT4O_MINI: {'input': 0.00015, 'output': 0.0006}
    }

    # Промпты для различных задач
    SYSTEM_PROMPTS = {
        GenerationTask.CODE_GENERATION: """You are an expert software engineer specializing in writing high-quality, production-ready code.
Focus on:
- Clean, readable code following best practices
- Proper error handling and edge cases
- Type hints and documentation
- Security considerations
- Performance optimization""",

        GenerationTask.CODE_REVIEW: """You are an expert code reviewer with deep knowledge of software engineering best practices.
Review code for:
- Bugs and potential issues
- Security vulnerabilities
- Performance bottlenecks
- Code quality and maintainability
- Best practices compliance""",

        GenerationTask.TEST_GENERATION: """You are an expert in software testing and test automation.
Generate comprehensive tests that cover:
- Happy path scenarios
- Edge cases and error conditions
- Integration points
- Performance considerations
- Security aspects""",

        GenerationTask.REFACTORING: """You are an expert in code refactoring and software architecture.
Focus on:
- Improving code structure and readability
- Eliminating code smells
- Applying design patterns where appropriate
- Maintaining backward compatibility
- Preserving functionality""",

        GenerationTask.BUG_ANALYSIS: """You are an expert debugger and root cause analyst.
Analyze code to:
- Identify potential bugs
- Predict failure modes
- Suggest preventive measures
- Explain root causes
- Provide actionable fixes""",

        GenerationTask.OPTIMIZATION: """You are an expert in performance optimization and algorithm design.
Optimize for:
- Time complexity
- Space complexity
- Resource utilization
- Scalability
- Maintainability""",

        GenerationTask.DOCUMENTATION: """You are an expert technical writer specializing in code documentation.
Create documentation that:
- Clearly explains purpose and usage
- Includes practical examples
- Documents edge cases and limitations
- Follows documentation best practices
- Is accessible to target audience"""
    }

    def __init__(self, api_key: Optional[str] = None, storage_path: str = './gpt4_cache'):
        """
        Инициализация GPT-4 интеграции

        Args:
            api_key: OpenAI API key (если None, берется из переменной окружения)
            storage_path: Путь для кеширования результатов
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.storage_path = storage_path
        self.cache_enabled = True
        self.response_cache: Dict[str, GPT4Response] = {}

        os.makedirs(storage_path, exist_ok=True)
        self._load_cache()

    def _load_cache(self):
        """Загрузка кеша из файла"""
        cache_file = os.path.join(self.storage_path, 'response_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    for key, data in cache_data.items():
                        data['task_type'] = GenerationTask(data['task_type'])
                        data['model'] = GPT4Model(data['model'])
                        self.response_cache[key] = GPT4Response(**data)
            except Exception as e:
                print(f"Warning: Failed to load cache: {e}")

    def _save_cache(self):
        """Сохранение кеша в файл"""
        cache_file = os.path.join(self.storage_path, 'response_cache.json')
        cache_data = {k: v.to_dict() for k, v in self.response_cache.items()}
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def _get_cache_key(self, request: GPT4Request) -> str:
        """Генерация ключа кеша для запроса"""
        cache_str = f"{request.task_type.value}:{request.prompt}:{request.model.value}"
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def _calculate_cost(self, model: GPT4Model, input_tokens: int, output_tokens: int) -> float:
        """Расчет стоимости запроса"""
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        return round(input_cost + output_cost, 6)

    def _simulate_api_call(self, request: GPT4Request) -> Dict[str, Any]:
        """
        Симуляция вызова API (для демонстрации без реального API key)
        В production это заменяется на реальный вызов OpenAI API
        """
        # Симулируем ответ в зависимости от типа задачи
        simulated_responses = {
            GenerationTask.CODE_GENERATION: """```python
def process_data(data: List[Dict]) -> List[Dict]:
    \"\"\"
    Process and validate data entries.

    Args:
        data: List of data dictionaries

    Returns:
        Processed and validated data

    Raises:
        ValueError: If data format is invalid
    \"\"\"
    if not data:
        return []

    processed = []
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid entry type: {type(entry)}")

        # Validate required fields
        if 'id' not in entry or 'value' not in entry:
            continue

        processed.append({
            'id': str(entry['id']),
            'value': entry['value'],
            'processed_at': datetime.now().isoformat()
        })

    return processed
```""",

            GenerationTask.CODE_REVIEW: """## Code Review Results

### Issues Found: 3

**1. Security Issue (HIGH)**
- Location: Line 45
- Issue: SQL query concatenation vulnerable to injection
- Fix: Use parameterized queries instead

**2. Performance Issue (MEDIUM)**
- Location: Lines 78-82
- Issue: N+1 query problem in loop
- Fix: Use bulk query with JOIN

**3. Code Quality (LOW)**
- Location: Line 103
- Issue: Magic number used without constant
- Fix: Define as named constant

### Recommendations:
- Add input validation
- Implement proper error handling
- Add unit tests for edge cases""",

            GenerationTask.TEST_GENERATION: """```python
import pytest
from unittest.mock import Mock, patch

def test_process_data_happy_path():
    \"\"\"Test normal data processing\"\"\"
    data = [
        {'id': 1, 'value': 'test1'},
        {'id': 2, 'value': 'test2'}
    ]
    result = process_data(data)
    assert len(result) == 2
    assert result[0]['id'] == '1'

def test_process_data_empty_input():
    \"\"\"Test with empty input\"\"\"
    result = process_data([])
    assert result == []

def test_process_data_invalid_entry():
    \"\"\"Test with invalid entry type\"\"\"
    with pytest.raises(ValueError):
        process_data([None, 'invalid'])

def test_process_data_missing_fields():
    \"\"\"Test entries with missing required fields\"\"\"
    data = [
        {'id': 1},  # missing value
        {'value': 'test'}  # missing id
    ]
    result = process_data(data)
    assert len(result) == 0
```""",

            GenerationTask.REFACTORING: """## Refactoring Suggestions

### 1. Extract Method
**Before:**
```python
def process_order(order):
    # validate
    if not order.get('items'):
        raise ValueError("No items")
    # calculate
    total = sum(item['price'] * item['qty'] for item in order['items'])
    # apply discount
    if total > 100:
        total *= 0.9
    return total
```

**After:**
```python
def process_order(order: Dict) -> float:
    validate_order(order)
    subtotal = calculate_subtotal(order['items'])
    return apply_discount(subtotal)

def validate_order(order: Dict) -> None:
    if not order.get('items'):
        raise ValueError("No items in order")

def calculate_subtotal(items: List[Dict]) -> float:
    return sum(item['price'] * item['qty'] for item in items)

def apply_discount(amount: float, threshold: float = 100.0) -> float:
    return amount * 0.9 if amount > threshold else amount
```""",

            GenerationTask.BUG_ANALYSIS: """## Bug Analysis Report

### Potential Bugs Detected: 4

**1. Race Condition (CRITICAL)**
- Location: Lines 67-72
- Description: Shared state modification without locking
- Impact: Data corruption in concurrent scenarios
- Fix: Add threading lock or use atomic operations

**2. Memory Leak (HIGH)**
- Location: Line 134
- Description: Circular reference in callback
- Impact: Memory not freed, eventual OOM
- Fix: Use weak references or explicit cleanup

**3. Null Pointer (MEDIUM)**
- Location: Line 89
- Description: Potential None access without check
- Impact: AttributeError at runtime
- Fix: Add None check before access

**4. Off-by-One (LOW)**
- Location: Line 201
- Description: Range iteration may skip last element
- Impact: Incomplete processing
- Fix: Use `range(len(items))` instead of `range(len(items)-1)`""",

            GenerationTask.OPTIMIZATION: """## Performance Optimization Report

### Current Performance: O(n²)
### Optimized Performance: O(n log n)
### Expected Speedup: 10-100x for large datasets

### Optimization 1: Algorithm Improvement
**Before:**
```python
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
```

**After:**
```python
def find_duplicates(items):
    from collections import Counter
    counts = Counter(items)
    return [item for item, count in counts.items() if count > 1]
```

### Optimization 2: Caching
- Add memoization for expensive calculations
- Use LRU cache for frequently accessed data
- Implement lazy loading for heavy resources

### Optimization 3: Database Query
- Use batch operations instead of loops
- Add proper indexing
- Implement query result caching""",

            GenerationTask.DOCUMENTATION: """# Module Documentation

## Overview
This module provides data processing utilities for handling and validating structured data.

## Installation
```bash
pip install data-processor
```

## Quick Start
```python
from data_processor import process_data

data = [
    {'id': 1, 'value': 'example'},
    {'id': 2, 'value': 'test'}
]

result = process_data(data)
```

## API Reference

### process_data(data: List[Dict]) -> List[Dict]
Process and validate data entries.

**Parameters:**
- `data` (List[Dict]): Input data to process

**Returns:**
- List[Dict]: Processed and validated data

**Raises:**
- `ValueError`: If data format is invalid

**Example:**
```python
data = [{'id': 1, 'value': 'test'}]
result = process_data(data)
# [{'id': '1', 'value': 'test', 'processed_at': '2026-01-25T10:30:00'}]
```

## Best Practices
- Always validate input data
- Handle edge cases (empty lists, None values)
- Use type hints for better IDE support
"""
        }

        content = simulated_responses.get(
            request.task_type,
            "Generated content based on the request."
        )

        # Симулируем использование токенов
        input_tokens = len(request.prompt.split()) * 2
        output_tokens = len(content.split()) * 2

        return {
            'content': content,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }

    def generate(self, request: GPT4Request) -> GPT4Response:
        """
        Генерация контента через GPT-4

        Args:
            request: Запрос к GPT-4

        Returns:
            Ответ от GPT-4
        """
        # Проверка кеша
        cache_key = self._get_cache_key(request)
        if self.cache_enabled and cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            print(f"✅ Using cached response for {request.task_type.value}")
            return cached

        # Получение системного промпта
        system_prompt = self.SYSTEM_PROMPTS.get(request.task_type, "")

        # В production здесь будет реальный вызов OpenAI API
        # import openai
        # response = openai.ChatCompletion.create(
        #     model=request.model.value,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": request.prompt}
        #     ],
        #     temperature=request.temperature,
        #     max_tokens=request.max_tokens
        # )

        # Для демонстрации используем симуляцию
        api_response = self._simulate_api_call(request)

        # Расчет стоимости
        cost = self._calculate_cost(
            request.model,
            api_response['input_tokens'],
            api_response['output_tokens']
        )

        # Оценка качества (в реальности это может быть ML модель)
        quality_score = self._assess_quality(api_response['content'], request.task_type)

        # Создание ответа
        response = GPT4Response(
            request_id=hashlib.sha256(f"{datetime.now().isoformat()}:{cache_key}".encode()).hexdigest()[:16],
            task_type=request.task_type,
            content=api_response['content'],
            model=request.model,
            tokens_used=api_response['input_tokens'] + api_response['output_tokens'],
            cost=cost,
            quality_score=quality_score,
            metadata={
                'input_tokens': api_response['input_tokens'],
                'output_tokens': api_response['output_tokens'],
                'user_id': request.user_id,
                'organization_id': request.organization_id
            },
            timestamp=datetime.now().isoformat()
        )

        # Кеширование
        if self.cache_enabled:
            self.response_cache[cache_key] = response
            self._save_cache()

        return response

    def _assess_quality(self, content: str, task_type: GenerationTask) -> float:
        """
        Оценка качества сгенерированного контента

        Args:
            content: Сгенерированный контент
            task_type: Тип задачи

        Returns:
            Оценка качества от 0.0 до 1.0
        """
        score = 0.7  # Базовая оценка

        # Проверка наличия кода для задач генерации
        if task_type in [GenerationTask.CODE_GENERATION, GenerationTask.TEST_GENERATION]:
            if '```' in content:
                score += 0.15
            if 'def ' in content or 'class ' in content:
                score += 0.1
            if '"""' in content or "'''" in content:  # Docstrings
                score += 0.05

        # Проверка структуры для ревью
        elif task_type == GenerationTask.CODE_REVIEW:
            if 'Issue' in content or 'Bug' in content:
                score += 0.1
            if 'Fix:' in content or 'Recommendation' in content:
                score += 0.1
            if 'Security' in content or 'Performance' in content:
                score += 0.1

        # Проверка для документации
        elif task_type == GenerationTask.DOCUMENTATION:
            if '##' in content:  # Headers
                score += 0.1
            if '```' in content:  # Code examples
                score += 0.1
            if 'Example' in content:
                score += 0.1

        return min(score, 1.0)

    def batch_generate(self, requests: List[GPT4Request]) -> List[GPT4Response]:
        """
        Пакетная генерация для множества запросов

        Args:
            requests: Список запросов

        Returns:
            Список ответов
        """
        return [self.generate(req) for req in requests]

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования"""
        total_cost = sum(resp.cost for resp in self.response_cache.values())
        total_tokens = sum(resp.tokens_used for resp in self.response_cache.values())

        task_counts = {}
        for resp in self.response_cache.values():
            task_type = resp.task_type.value
            task_counts[task_type] = task_counts.get(task_type, 0) + 1

        return {
            'total_requests': len(self.response_cache),
            'total_cost_usd': round(total_cost, 2),
            'total_tokens': total_tokens,
            'average_quality_score': round(
                sum(r.quality_score for r in self.response_cache.values()) / len(self.response_cache)
                if self.response_cache else 0,
                2
            ),
            'requests_by_task': task_counts,
            'cache_size': len(self.response_cache)
        }

    def clear_cache(self):
        """Очистка кеша"""
        self.response_cache.clear()
        self._save_cache()


# Удобные функции для быстрого использования
def generate_code(prompt: str, context: Dict = None, model: GPT4Model = GPT4Model.GPT4_TURBO) -> str:
    """Быстрая генерация кода"""
    gpt4 = GPT4Integration()
    request = GPT4Request(
        task_type=GenerationTask.CODE_GENERATION,
        prompt=prompt,
        context=context or {},
        model=model
    )
    response = gpt4.generate(request)
    return response.content


def review_code(code: str, focus_areas: List[str] = None) -> str:
    """Быстрый ревью кода"""
    gpt4 = GPT4Integration()
    prompt = f"Review the following code:\n\n```\n{code}\n```"
    if focus_areas:
        prompt += f"\n\nFocus on: {', '.join(focus_areas)}"

    request = GPT4Request(
        task_type=GenerationTask.CODE_REVIEW,
        prompt=prompt,
        context={'focus_areas': focus_areas or []}
    )
    response = gpt4.generate(request)
    return response.content


def generate_tests(code: str, test_framework: str = 'pytest') -> str:
    """Быстрая генерация тестов"""
    gpt4 = GPT4Integration()
    request = GPT4Request(
        task_type=GenerationTask.TEST_GENERATION,
        prompt=f"Generate {test_framework} tests for:\n\n```\n{code}\n```",
        context={'framework': test_framework}
    )
    response = gpt4.generate(request)
    return response.content
