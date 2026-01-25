#!/usr/bin/env python3
"""
Testing & Quality Examples - E2E, Mutation, Load, Security Testing
"""

from pathlib import Path
from tools.ai_generator.testing import (
    E2ETestGenerator, E2EFramework, TestScenario,
    MutationTester,
    LoadTestGenerator, LoadTestFramework,
    SecurityScanner, ScanConfig
)


def example_e2e_test_generation():
    """Generate E2E tests with Playwright"""
    print("=" * 60)
    print("E2E Test Generation")
    print("=" * 60)

    generator = E2ETestGenerator(framework=E2EFramework.PLAYWRIGHT)

    generator.add_scenario("User Login Flow", [
        {"action": "navigate", "url": "/login"},
        {"action": "fill", "selector": "#email", "value": "user@example.com"},
        {"action": "fill", "selector": "#password", "value": "password123"},
        {"action": "click", "selector": "#login-button"},
        {"action": "assert", "selector": ".dashboard", "visible": True}
    ])

    files = generator.generate(Path("./output/e2e-tests"))

    print(f"✅ Generated E2E tests")
    print(f"   Framework: Playwright")
    print(f"   Scenarios: 1")
    print(f"   Files: {len(files)}")
    print()


def example_mutation_testing():
    """Run mutation testing"""
    print("=" * 60)
    print("Mutation Testing")
    print("=" * 60)

    tester = MutationTester()

    report = tester.run_mutations(
        source_file=Path("./src/calculator.py"),
        test_file=Path("./tests/test_calculator.py")
    )

    print(f"✅ Mutation testing completed")
    print(f"   Mutants generated: {report.total_mutants}")
    print(f"   Mutants killed: {report.killed_mutants}")
    print(f"   Mutation score: {report.mutation_score:.1%}")
    print()


def example_load_testing():
    """Generate load test scenarios"""
    print("=" * 60)
    print("Load Test Generation")
    print("=" * 60)

    generator = LoadTestGenerator(framework=LoadTestFramework.K6)

    files = generator.generate_scenario(
        name="API Load Test",
        target_url="https://api.example.com",
        vus=100,  # Virtual users
        duration="5m",
        requests=[
            {"method": "GET", "path": "/api/users"},
            {"method": "POST", "path": "/api/orders", "payload": {...}}
        ],
        output_dir=Path("./output/load-tests")
    )

    print(f"✅ Generated load test")
    print(f"   Framework: k6")
    print(f"   VUs: 100")
    print(f"   Duration: 5 minutes")
    print()


def example_security_scanning():
    """Run security vulnerability scan"""
    print("=" * 60)
    print("Security Scanning")
    print("=" * 60)

    scanner = SecurityScanner()

    results = scanner.scan_web_app(
        url="https://demo.testfire.net",
        scan_types=["sql_injection", "xss", "csrf"],
        max_depth=3
    )

    print(f"✅ Security scan completed")
    print(f"   Pages scanned: {results.pages_scanned}")
    print(f"   Vulnerabilities: {results.total_vulnerabilities}")
    print(f"   Critical: {results.critical_count}")
    print()


if __name__ == "__main__":
    print("\n🧪 Testing & Quality Examples\n")
    example_e2e_test_generation()
    example_mutation_testing()
    example_load_testing()
    example_security_scanning()
    print("✅ All testing examples completed!\n")
