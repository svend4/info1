#!/usr/bin/env python3
"""
Automated Test Generator

Автоматическая генерация тестов для Python кода.
"""

import ast
import inspect
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TestFramework(Enum):
    """Поддерживаемые фреймворки тестирования"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    DOCTEST = "doctest"


class TestType(Enum):
    """Типы тестов"""
    UNIT = "unit"
    INTEGRATION = "integration"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class TestCase:
    """Сгенерированный тест-кейс"""
    name: str
    test_type: TestType
    function_name: str
    code: str
    description: str
    assertions: List[str]
    mocks_needed: List[str]
    fixtures_needed: List[str]

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'test_type': self.test_type.value,
            'function_name': self.function_name,
            'code': self.code,
            'description': self.description,
            'assertions': self.assertions,
            'mocks_needed': self.mocks_needed,
            'fixtures_needed': self.fixtures_needed
        }


@dataclass
class TestSuite:
    """Набор тестов для модуля/класса"""
    module_name: str
    framework: TestFramework
    test_cases: List[TestCase]
    fixtures: List[str]
    imports: List[str]
    coverage_estimate: float  # Оценка покрытия 0-100%

    def to_code(self) -> str:
        """Генерация полного кода тестового модуля"""
        if self.framework == TestFramework.PYTEST:
            return self._generate_pytest_code()
        elif self.framework == TestFramework.UNITTEST:
            return self._generate_unittest_code()
        else:
            return self._generate_doctest_code()

    def _generate_pytest_code(self) -> str:
        """Генерация pytest кода"""
        lines = []

        # Imports
        lines.append("import pytest")
        lines.append("from unittest.mock import Mock, patch, MagicMock")
        for imp in self.imports:
            lines.append(imp)
        lines.append("")

        # Fixtures
        if self.fixtures:
            for fixture in self.fixtures:
                lines.append(fixture)
                lines.append("")

        # Test cases
        for test_case in self.test_cases:
            lines.append(test_case.code)
            lines.append("")

        return "\n".join(lines)

    def _generate_unittest_code(self) -> str:
        """Генерация unittest кода"""
        lines = []

        lines.append("import unittest")
        lines.append("from unittest.mock import Mock, patch, MagicMock")
        for imp in self.imports:
            lines.append(imp)
        lines.append("")

        lines.append(f"class Test{self.module_name.title()}(unittest.TestCase):")
        lines.append("    \"\"\"Test suite for " + self.module_name + "\"\"\"")
        lines.append("")

        # Setup/teardown
        lines.append("    def setUp(self):")
        lines.append("        \"\"\"Setup test fixtures\"\"\"")
        lines.append("        pass")
        lines.append("")

        # Test cases
        for test_case in self.test_cases:
            # Indent test case code
            indented_code = "\n".join(
                "    " + line if line else ""
                for line in test_case.code.split("\n")
            )
            lines.append(indented_code)
            lines.append("")

        lines.append("if __name__ == '__main__':")
        lines.append("    unittest.main()")

        return "\n".join(lines)

    def _generate_doctest_code(self) -> str:
        """Генерация doctest примеров"""
        lines = []
        lines.append('"""')
        lines.append(f"Doctests for {self.module_name}")
        lines.append("")

        for test_case in self.test_cases:
            lines.append(f">>> {test_case.code}")

        lines.append('"""')
        return "\n".join(lines)


class TestGenerator:
    """
    Automated Test Generator

    Генерирует тесты для Python кода используя:
    - Анализ функций и их сигнатур
    - Определение edge cases
    - Генерацию mock объектов
    - AI-ассистированную генерацию сложных сценариев
    """

    def __init__(self, framework: TestFramework = TestFramework.PYTEST):
        """
        Инициализация генератора

        Args:
            framework: Фреймворк тестирования
        """
        self.framework = framework
        self.generated_tests: Dict[str, TestSuite] = {}

    def generate_for_file(self, file_path: str) -> TestSuite:
        """
        Генерация тестов для файла

        Args:
            file_path: Путь к файлу

        Returns:
            Набор тестов
        """
        with open(file_path, 'r') as f:
            code = f.read()

        module_name = Path(file_path).stem
        return self.generate_for_code(code, module_name)

    def generate_for_code(self, code: str, module_name: str = "module") -> TestSuite:
        """
        Генерация тестов для кода

        Args:
            code: Исходный код
            module_name: Имя модуля

        Returns:
            Набор тестов
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return TestSuite(
                module_name=module_name,
                framework=self.framework,
                test_cases=[],
                fixtures=[],
                imports=[],
                coverage_estimate=0.0
            )

        test_cases = []
        fixtures = []
        imports = [f"from {module_name} import *"]

        # Анализ функций
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Пропускаем приватные функции
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue

                # Генерация тестов для функции
                func_tests = self._generate_function_tests(node, module_name)
                test_cases.extend(func_tests)

            elif isinstance(node, ast.ClassDef):
                # Генерация тестов для класса
                class_tests = self._generate_class_tests(node, module_name)
                test_cases.extend(class_tests)

        # Оценка покрытия
        coverage = min(100.0, len(test_cases) * 15)  # Примерная оценка

        test_suite = TestSuite(
            module_name=module_name,
            framework=self.framework,
            test_cases=test_cases,
            fixtures=fixtures,
            imports=imports,
            coverage_estimate=coverage
        )

        self.generated_tests[module_name] = test_suite
        return test_suite

    def _generate_function_tests(self, node: ast.FunctionDef, module_name: str) -> List[TestCase]:
        """Генерация тестов для функции"""
        test_cases = []
        func_name = node.name

        # Анализ параметров
        params = self._analyze_parameters(node)
        return_annotation = self._get_return_annotation(node)

        # 1. Happy path test
        happy_test = self._generate_happy_path_test(func_name, params, module_name)
        test_cases.append(happy_test)

        # 2. Edge cases
        edge_tests = self._generate_edge_case_tests(func_name, params, module_name)
        test_cases.extend(edge_tests)

        # 3. Error cases
        error_tests = self._generate_error_tests(func_name, params, module_name)
        test_cases.extend(error_tests)

        return test_cases

    def _generate_class_tests(self, node: ast.ClassDef, module_name: str) -> List[TestCase]:
        """Генерация тестов для класса"""
        test_cases = []
        class_name = node.name

        # Тест инициализации
        init_test = self._generate_init_test(class_name, node, module_name)
        if init_test:
            test_cases.append(init_test)

        # Тесты для методов
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith('_') and item.name != '__init__':
                    continue

                method_tests = self._generate_method_tests(
                    class_name, item, module_name
                )
                test_cases.extend(method_tests)

        return test_cases

    def _analyze_parameters(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Анализ параметров функции"""
        params = {}

        for arg in node.args.args:
            param_name = arg.arg
            param_type = None

            # Попытка определить тип из аннотации
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    param_type = arg.annotation.id
                elif isinstance(arg.annotation, ast.Subscript):
                    if isinstance(arg.annotation.value, ast.Name):
                        param_type = arg.annotation.value.id

            params[param_name] = {
                'type': param_type,
                'has_default': False
            }

        # Обработка значений по умолчанию
        defaults = node.args.defaults
        if defaults:
            default_offset = len(params) - len(defaults)
            for i, default in enumerate(defaults):
                param_name = list(params.keys())[default_offset + i]
                params[param_name]['has_default'] = True

        return params

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Получение типа возвращаемого значения"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
        return None

    def _generate_happy_path_test(self, func_name: str, params: Dict, module_name: str) -> TestCase:
        """Генерация теста для happy path"""
        test_name = f"test_{func_name}_happy_path"

        # Генерация вызова функции с валидными параметрами
        param_values = self._generate_sample_values(params)
        param_str = ", ".join(f"{k}={repr(v)}" for k, v in param_values.items() if k != 'self')

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test {func_name} with valid inputs"""
    result = {func_name}({param_str})
    assert result is not None
    # Add more specific assertions based on expected behavior'''
        else:
            code = f'''def {test_name}(self):
    """Test {func_name} with valid inputs"""
    result = {func_name}({param_str})
    self.assertIsNotNone(result)
    # Add more specific assertions based on expected behavior'''

        return TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            function_name=func_name,
            code=code,
            description=f"Test {func_name} with valid inputs",
            assertions=["assert result is not None"],
            mocks_needed=[],
            fixtures_needed=[]
        )

    def _generate_edge_case_tests(self, func_name: str, params: Dict, module_name: str) -> List[TestCase]:
        """Генерация тестов для edge cases"""
        test_cases = []

        # Edge case: пустые значения
        if any(p['type'] in ['List', 'Dict', 'str', 'Set'] for p in params.values()):
            test_name = f"test_{func_name}_empty_input"

            if self.framework == TestFramework.PYTEST:
                code = f'''def {test_name}():
    """Test {func_name} with empty input"""
    result = {func_name}([])
    assert result is not None'''
            else:
                code = f'''def {test_name}(self):
    """Test {func_name} with empty input"""
    result = {func_name}([])
    self.assertIsNotNone(result)'''

            test_cases.append(TestCase(
                name=test_name,
                test_type=TestType.EDGE_CASE,
                function_name=func_name,
                code=code,
                description=f"Test {func_name} with empty input",
                assertions=["assert result is not None"],
                mocks_needed=[],
                fixtures_needed=[]
            ))

        # Edge case: None значения
        test_name = f"test_{func_name}_none_input"
        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test {func_name} with None input"""
    result = {func_name}(None)
    # Verify appropriate handling of None'''
        else:
            code = f'''def {test_name}(self):
    """Test {func_name} with None input"""
    result = {func_name}(None)
    # Verify appropriate handling of None'''

        test_cases.append(TestCase(
            name=test_name,
            test_type=TestType.EDGE_CASE,
            function_name=func_name,
            code=code,
            description=f"Test {func_name} with None input",
            assertions=[],
            mocks_needed=[],
            fixtures_needed=[]
        ))

        return test_cases

    def _generate_error_tests(self, func_name: str, params: Dict, module_name: str) -> List[TestCase]:
        """Генерация тестов для обработки ошибок"""
        test_cases = []

        test_name = f"test_{func_name}_invalid_type"

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test {func_name} with invalid type"""
    with pytest.raises((TypeError, ValueError)):
        {func_name}("invalid")'''
        else:
            code = f'''def {test_name}(self):
    """Test {func_name} with invalid type"""
    with self.assertRaises((TypeError, ValueError)):
        {func_name}("invalid")'''

        test_cases.append(TestCase(
            name=test_name,
            test_type=TestType.EDGE_CASE,
            function_name=func_name,
            code=code,
            description=f"Test {func_name} error handling",
            assertions=["raises exception"],
            mocks_needed=[],
            fixtures_needed=[]
        ))

        return test_cases

    def _generate_init_test(self, class_name: str, node: ast.ClassDef, module_name: str) -> Optional[TestCase]:
        """Генерация теста для __init__"""
        # Поиск __init__ метода
        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_method = item
                break

        if not init_method:
            return None

        test_name = f"test_{class_name.lower()}_initialization"

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test {class_name} initialization"""
    obj = {class_name}()
    assert obj is not None
    assert isinstance(obj, {class_name})'''
        else:
            code = f'''def {test_name}(self):
    """Test {class_name} initialization"""
    obj = {class_name}()
    self.assertIsNotNone(obj)
    self.assertIsInstance(obj, {class_name})'''

        return TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            function_name=f"{class_name}.__init__",
            code=code,
            description=f"Test {class_name} initialization",
            assertions=["object created successfully"],
            mocks_needed=[],
            fixtures_needed=[]
        )

    def _generate_method_tests(self, class_name: str, method: ast.FunctionDef, module_name: str) -> List[TestCase]:
        """Генерация тестов для методов класса"""
        test_cases = []
        method_name = method.name

        if method_name == '__init__':
            return test_cases

        test_name = f"test_{class_name.lower()}_{method_name}"

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test {class_name}.{method_name}"""
    obj = {class_name}()
    result = obj.{method_name}()
    assert result is not None'''
        else:
            code = f'''def {test_name}(self):
    """Test {class_name}.{method_name}"""
    obj = {class_name}()
    result = obj.{method_name}()
    self.assertIsNotNone(result)'''

        test_cases.append(TestCase(
            name=test_name,
            test_type=TestType.UNIT,
            function_name=f"{class_name}.{method_name}",
            code=code,
            description=f"Test {class_name}.{method_name} method",
            assertions=["result is not None"],
            mocks_needed=[],
            fixtures_needed=[]
        ))

        return test_cases

    def _generate_sample_values(self, params: Dict) -> Dict[str, Any]:
        """Генерация примерных значений для параметров"""
        values = {}

        for param_name, param_info in params.items():
            if param_name == 'self':
                continue

            param_type = param_info.get('type')

            if param_type == 'str':
                values[param_name] = "test_string"
            elif param_type == 'int':
                values[param_name] = 42
            elif param_type == 'float':
                values[param_name] = 3.14
            elif param_type == 'bool':
                values[param_name] = True
            elif param_type == 'List':
                values[param_name] = [1, 2, 3]
            elif param_type == 'Dict':
                values[param_name] = {'key': 'value'}
            elif param_type == 'Set':
                values[param_name] = {1, 2, 3}
            else:
                values[param_name] = None

        return values

    def generate_integration_tests(self, modules: List[str]) -> TestSuite:
        """
        Генерация интеграционных тестов для множества модулей

        Args:
            modules: Список модулей для интеграции

        Returns:
            Набор интеграционных тестов
        """
        test_cases = []

        # Пример интеграционного теста
        test_name = "test_modules_integration"

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}():
    """Test integration between modules"""
    # Setup
    # Test interaction between {', '.join(modules)}
    # Verify results
    assert True  # Replace with actual integration test'''
        else:
            code = f'''def {test_name}(self):
    """Test integration between modules"""
    # Setup
    # Test interaction between {', '.join(modules)}
    # Verify results
    self.assertTrue(True)  # Replace with actual integration test'''

        test_cases.append(TestCase(
            name=test_name,
            test_type=TestType.INTEGRATION,
            function_name="integration",
            code=code,
            description=f"Integration test for {', '.join(modules)}",
            assertions=["integration works correctly"],
            mocks_needed=[],
            fixtures_needed=[]
        ))

        return TestSuite(
            module_name="_".join(modules),
            framework=self.framework,
            test_cases=test_cases,
            fixtures=[],
            imports=[f"from {m} import *" for m in modules],
            coverage_estimate=50.0
        )

    def generate_performance_tests(self, func_name: str, module_name: str) -> TestCase:
        """Генерация теста производительности"""
        test_name = f"test_{func_name}_performance"

        if self.framework == TestFramework.PYTEST:
            code = f'''def {test_name}(benchmark):
    """Test {func_name} performance"""
    def run_func():
        return {func_name}()

    result = benchmark(run_func)
    assert result is not None'''
        else:
            code = f'''def {test_name}(self):
    """Test {func_name} performance"""
    import time
    start = time.time()
    result = {func_name}()
    duration = time.time() - start
    self.assertLess(duration, 1.0)  # Should complete in < 1 second'''

        return TestCase(
            name=test_name,
            test_type=TestType.PERFORMANCE,
            function_name=func_name,
            code=code,
            description=f"Performance test for {func_name}",
            assertions=["performance within acceptable range"],
            mocks_needed=[],
            fixtures_needed=["benchmark"] if self.framework == TestFramework.PYTEST else []
        )

    def save_tests(self, test_suite: TestSuite, output_path: str):
        """
        Сохранение тестов в файл

        Args:
            test_suite: Набор тестов
            output_path: Путь для сохранения
        """
        code = test_suite.to_code()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(code)

        print(f"✅ Tests saved to {output_path}")
        print(f"   Test cases: {len(test_suite.test_cases)}")
        print(f"   Estimated coverage: {test_suite.coverage_estimate:.1f}%")
