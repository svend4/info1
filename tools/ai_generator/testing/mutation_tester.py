#!/usr/bin/env python3
"""
Mutation Testing Engine

Автоматическое mutation testing для оценки качества test suite.
"""

import ast
import copy
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


class MutationOperator(Enum):
    """Mutation Operator Type"""
    ARITHMETIC = "arithmetic"  # + -> -, * -> /
    RELATIONAL = "relational"  # == -> !=, < -> <=
    LOGICAL = "logical"  # and -> or, not
    ASSIGNMENT = "assignment"  # += -> -=
    CONSTANT = "constant"  # 0 -> 1, True -> False
    REMOVE_LINE = "remove_line"  # Delete statement
    NEGATE_CONDITION = "negate_condition"  # if x -> if not x


class MutantStatus(Enum):
    """Mutant Status"""
    KILLED = "killed"  # Tests failed (good)
    SURVIVED = "survived"  # Tests passed (bad)
    TIMEOUT = "timeout"  # Tests timed out
    ERROR = "error"  # Runtime error


@dataclass
class Mutation:
    """Single Mutation"""
    operator: MutationOperator
    file_path: str
    line_number: int
    original_code: str
    mutated_code: str
    description: str


@dataclass
class MutantResult:
    """Mutation Test Result"""
    mutation: Mutation
    status: MutantStatus
    test_output: str = ""
    execution_time: float = 0.0
    killed_by: Optional[str] = None  # Test that killed the mutant


@dataclass
class MutationTestReport:
    """Mutation Testing Report"""
    total_mutants: int = 0
    killed: int = 0
    survived: int = 0
    timeout: int = 0
    error: int = 0
    mutation_score: float = 0.0
    results: List[MutantResult] = field(default_factory=list)
    coverage: Dict[str, Any] = field(default_factory=dict)


class MutationTester:
    """Mutation Testing Engine"""

    def __init__(
        self,
        source_dir: Path,
        test_command: str = "pytest",
        timeout: int = 60
    ):
        """
        Initialize mutation tester

        Args:
            source_dir: Source code directory
            test_command: Command to run tests
            timeout: Test timeout in seconds
        """
        self.source_dir = source_dir
        self.test_command = test_command
        self.timeout = timeout
        self.mutations: List[Mutation] = []

    def generate_mutations(self, file_path: Path) -> List[Mutation]:
        """
        Generate all possible mutations for file

        Args:
            file_path: File to mutate

        Returns:
            List of mutations
        """
        print(f"🧬 Generating mutations for {file_path}")

        mutations = []

        # Read source code
        code = file_path.read_text()
        lines = code.split('\n')

        try:
            tree = ast.parse(code)

            # Generate mutations using different operators
            mutations.extend(self._mutate_arithmetic(tree, file_path, lines))
            mutations.extend(self._mutate_relational(tree, file_path, lines))
            mutations.extend(self._mutate_logical(tree, file_path, lines))
            mutations.extend(self._mutate_constants(tree, file_path, lines))
            mutations.extend(self._mutate_conditions(tree, file_path, lines))

        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path}: {e}")

        print(f"✅ Generated {len(mutations)} mutations")
        return mutations

    def run_mutation_testing(
        self,
        file_paths: List[Path]
    ) -> MutationTestReport:
        """
        Run mutation testing on files

        Args:
            file_paths: Files to test

        Returns:
            Mutation test report
        """
        print("🧪 Running mutation testing...")

        report = MutationTestReport()

        # Generate all mutations
        all_mutations = []
        for file_path in file_paths:
            mutations = self.generate_mutations(file_path)
            all_mutations.extend(mutations)

        report.total_mutants = len(all_mutations)

        # Test each mutant
        for i, mutation in enumerate(all_mutations):
            print(f"Testing mutant {i + 1}/{len(all_mutations)}: {mutation.description}")

            result = self._test_mutant(mutation)
            report.results.append(result)

            if result.status == MutantStatus.KILLED:
                report.killed += 1
            elif result.status == MutantStatus.SURVIVED:
                report.survived += 1
            elif result.status == MutantStatus.TIMEOUT:
                report.timeout += 1
            elif result.status == MutantStatus.ERROR:
                report.error += 1

        # Calculate mutation score
        if report.total_mutants > 0:
            report.mutation_score = (report.killed / report.total_mutants) * 100

        print(f"\n✅ Mutation testing complete:")
        print(f"   Mutation Score: {report.mutation_score:.1f}%")
        print(f"   Killed: {report.killed}/{report.total_mutants}")
        print(f"   Survived: {report.survived}")

        return report

    def _test_mutant(self, mutation: Mutation) -> MutantResult:
        """
        Test single mutant

        Args:
            mutation: Mutation to test

        Returns:
            Mutant result
        """
        result = MutantResult(mutation=mutation, status=MutantStatus.ERROR)

        # Save original file
        file_path = Path(mutation.file_path)
        original_code = file_path.read_text()

        try:
            # Apply mutation
            mutated_code = self._apply_mutation(original_code, mutation)
            file_path.write_text(mutated_code)

            # Run tests
            start_time = datetime.now()

            try:
                process = subprocess.run(
                    self.test_command.split(),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.source_dir
                )

                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time = execution_time
                result.test_output = process.stdout + process.stderr

                # Check if tests failed (mutant killed)
                if process.returncode != 0:
                    result.status = MutantStatus.KILLED
                    # Extract which test failed
                    result.killed_by = self._extract_failed_test(result.test_output)
                else:
                    result.status = MutantStatus.SURVIVED

            except subprocess.TimeoutExpired:
                result.status = MutantStatus.TIMEOUT
                result.test_output = "Tests timed out"

        except Exception as e:
            result.status = MutantStatus.ERROR
            result.test_output = str(e)

        finally:
            # Restore original file
            file_path.write_text(original_code)

        return result

    def _apply_mutation(self, code: str, mutation: Mutation) -> str:
        """
        Apply mutation to code

        Args:
            code: Original code
            mutation: Mutation to apply

        Returns:
            Mutated code
        """
        lines = code.split('\n')
        line_idx = mutation.line_number - 1

        if 0 <= line_idx < len(lines):
            lines[line_idx] = lines[line_idx].replace(
                mutation.original_code,
                mutation.mutated_code,
                1  # Replace only first occurrence
            )

        return '\n'.join(lines)

    def _mutate_arithmetic(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: List[str]
    ) -> List[Mutation]:
        """Mutate arithmetic operators"""
        mutations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and hasattr(node, 'lineno'):
                line = lines[node.lineno - 1]

                # + -> -
                if isinstance(node.op, ast.Add):
                    if '+' in line:
                        mutations.append(Mutation(
                            operator=MutationOperator.ARITHMETIC,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='+',
                            mutated_code='-',
                            description="Replace + with -"
                        ))

                # - -> +
                elif isinstance(node.op, ast.Sub):
                    if '-' in line:
                        mutations.append(Mutation(
                            operator=MutationOperator.ARITHMETIC,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='-',
                            mutated_code='+',
                            description="Replace - with +"
                        ))

                # * -> /
                elif isinstance(node.op, ast.Mult):
                    if '*' in line:
                        mutations.append(Mutation(
                            operator=MutationOperator.ARITHMETIC,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='*',
                            mutated_code='/',
                            description="Replace * with /"
                        ))

                # / -> *
                elif isinstance(node.op, ast.Div):
                    if '/' in line:
                        mutations.append(Mutation(
                            operator=MutationOperator.ARITHMETIC,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='/',
                            mutated_code='*',
                            description="Replace / with *"
                        ))

        return mutations

    def _mutate_relational(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: List[str]
    ) -> List[Mutation]:
        """Mutate relational operators"""
        mutations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and hasattr(node, 'lineno'):
                line = lines[node.lineno - 1]

                for op in node.ops:
                    # == -> !=
                    if isinstance(op, ast.Eq):
                        mutations.append(Mutation(
                            operator=MutationOperator.RELATIONAL,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='==',
                            mutated_code='!=',
                            description="Replace == with !="
                        ))

                    # != -> ==
                    elif isinstance(op, ast.NotEq):
                        mutations.append(Mutation(
                            operator=MutationOperator.RELATIONAL,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='!=',
                            mutated_code='==',
                            description="Replace != with =="
                        ))

                    # < -> <=
                    elif isinstance(op, ast.Lt):
                        mutations.append(Mutation(
                            operator=MutationOperator.RELATIONAL,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='<',
                            mutated_code='<=',
                            description="Replace < with <="
                        ))

                    # > -> >=
                    elif isinstance(op, ast.Gt):
                        mutations.append(Mutation(
                            operator=MutationOperator.RELATIONAL,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            original_code='>',
                            mutated_code='>=',
                            description="Replace > with >="
                        ))

        return mutations

    def _mutate_logical(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: List[str]
    ) -> List[Mutation]:
        """Mutate logical operators"""
        mutations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp) and hasattr(node, 'lineno'):
                # and -> or
                if isinstance(node.op, ast.And):
                    mutations.append(Mutation(
                        operator=MutationOperator.LOGICAL,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code=' and ',
                        mutated_code=' or ',
                        description="Replace and with or"
                    ))

                # or -> and
                elif isinstance(node.op, ast.Or):
                    mutations.append(Mutation(
                        operator=MutationOperator.LOGICAL,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code=' or ',
                        mutated_code=' and ',
                        description="Replace or with and"
                    ))

        return mutations

    def _mutate_constants(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: List[str]
    ) -> List[Mutation]:
        """Mutate constant values"""
        mutations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and hasattr(node, 'lineno'):
                # True -> False
                if node.value is True:
                    mutations.append(Mutation(
                        operator=MutationOperator.CONSTANT,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code='True',
                        mutated_code='False',
                        description="Replace True with False"
                    ))

                # False -> True
                elif node.value is False:
                    mutations.append(Mutation(
                        operator=MutationOperator.CONSTANT,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code='False',
                        mutated_code='True',
                        description="Replace False with True"
                    ))

                # 0 -> 1
                elif isinstance(node.value, int) and node.value == 0:
                    mutations.append(Mutation(
                        operator=MutationOperator.CONSTANT,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code='0',
                        mutated_code='1',
                        description="Replace 0 with 1"
                    ))

                # Numeric constants: n -> n+1
                elif isinstance(node.value, int) and node.value > 0 and node.value < 100:
                    mutations.append(Mutation(
                        operator=MutationOperator.CONSTANT,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code=str(node.value),
                        mutated_code=str(node.value + 1),
                        description=f"Replace {node.value} with {node.value + 1}"
                    ))

        return mutations

    def _mutate_conditions(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: List[str]
    ) -> List[Mutation]:
        """Negate conditions"""
        mutations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If) and hasattr(node, 'lineno'):
                line = lines[node.lineno - 1].strip()

                # Extract condition
                if line.startswith('if '):
                    condition = line[3:].rstrip(':')

                    # Add 'not' to condition
                    mutations.append(Mutation(
                        operator=MutationOperator.NEGATE_CONDITION,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        original_code=f'if {condition}:',
                        mutated_code=f'if not ({condition}):',
                        description="Negate if condition"
                    ))

        return mutations

    def _extract_failed_test(self, test_output: str) -> Optional[str]:
        """Extract name of test that failed"""
        # Parse pytest output
        for line in test_output.split('\n'):
            if 'FAILED' in line:
                # Extract test name
                parts = line.split('::')
                if len(parts) >= 2:
                    return parts[-1].split(' ')[0]
        return None

    def generate_report(
        self,
        report: MutationTestReport,
        output_path: Path
    ):
        """
        Generate HTML report

        Args:
            report: Mutation test report
            output_path: Output file path
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mutation Testing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {"green" if report.mutation_score >= 80 else "orange" if report.mutation_score >= 60 else "red"}; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .killed {{ background-color: #90EE90; }}
        .survived {{ background-color: #FFB6C1; }}
        .timeout {{ background-color: #FFA500; }}
        .error {{ background-color: #FF6347; }}
    </style>
</head>
<body>
    <h1>Mutation Testing Report</h1>

    <div class="summary">
        <div class="score">{report.mutation_score:.1f}%</div>
        <p>Mutation Score</p>
        <p>Killed: {report.killed} | Survived: {report.survived} | Timeout: {report.timeout} | Error: {report.error}</p>
        <p>Total Mutants: {report.total_mutants}</p>
    </div>

    <h2>Mutation Results</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Line</th>
            <th>Operator</th>
            <th>Description</th>
            <th>Status</th>
            <th>Killed By</th>
        </tr>
"""

        for result in report.results:
            mutation = result.mutation
            html += f"""        <tr class="{result.status.value}">
            <td>{mutation.file_path}</td>
            <td>{mutation.line_number}</td>
            <td>{mutation.operator.value}</td>
            <td>{mutation.description}</td>
            <td>{result.status.value.upper()}</td>
            <td>{result.killed_by or '-'}</td>
        </tr>
"""

        html += """    </table>
</body>
</html>
"""

        output_path.write_text(html)
        print(f"✅ Report saved to {output_path}")
