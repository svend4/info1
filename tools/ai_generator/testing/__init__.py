"""
Advanced Testing & Quality Package

E2E testing, mutation testing, load testing, и security scanning.
"""

from .e2e_test_generator import (
    E2ETestGenerator,
    E2ETestConfig,
    TestScenario,
    UserAction,
    E2EFramework,
    BrowserType,
    ActionType
)

from .mutation_tester import (
    MutationTester,
    Mutation,
    MutantResult,
    MutationTestReport,
    MutationOperator,
    MutantStatus
)

from .load_test_generator import (
    LoadTestGenerator,
    LoadTestConfig,
    LoadScenario,
    HTTPRequest,
    LoadTestFramework,
    LoadProfile,
    HTTPMethod
)

from .security_scanner import (
    SecurityScanner,
    ScanConfig,
    SecurityScanResult,
    SecurityFinding,
    VulnerabilityType,
    RiskLevel
)

__all__ = [
    # E2E Test Generator
    'E2ETestGenerator',
    'E2ETestConfig',
    'TestScenario',
    'UserAction',
    'E2EFramework',
    'BrowserType',
    'ActionType',

    # Mutation Tester
    'MutationTester',
    'Mutation',
    'MutantResult',
    'MutationTestReport',
    'MutationOperator',
    'MutantStatus',

    # Load Test Generator
    'LoadTestGenerator',
    'LoadTestConfig',
    'LoadScenario',
    'HTTPRequest',
    'LoadTestFramework',
    'LoadProfile',
    'HTTPMethod',

    # Security Scanner
    'SecurityScanner',
    'ScanConfig',
    'SecurityScanResult',
    'SecurityFinding',
    'VulnerabilityType',
    'RiskLevel'
]

__version__ = '1.0.0'
