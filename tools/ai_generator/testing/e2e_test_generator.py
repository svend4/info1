#!/usr/bin/env python3
"""
E2E Test Generator

Автоматическая генерация end-to-end tests для Playwright, Cypress, и Selenium.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class E2EFramework(Enum):
    """E2E Testing Framework"""
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"


class BrowserType(Enum):
    """Browser Type"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"


class ActionType(Enum):
    """User Action Type"""
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    NAVIGATE = "navigate"
    WAIT = "wait"
    ASSERT = "assert"
    SCREENSHOT = "screenshot"
    HOVER = "hover"
    DRAG = "drag"


@dataclass
class UserAction:
    """User Action in Test"""
    type: ActionType
    selector: str = ""
    value: str = ""
    description: str = ""
    timeout: int = 5000


@dataclass
class TestScenario:
    """E2E Test Scenario"""
    name: str
    description: str
    url: str
    actions: List[UserAction] = field(default_factory=list)
    setup_actions: List[UserAction] = field(default_factory=list)
    teardown_actions: List[UserAction] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class E2ETestConfig:
    """E2E Test Configuration"""
    framework: E2EFramework
    base_url: str
    browsers: List[BrowserType] = field(default_factory=list)
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    headless: bool = True
    record_video: bool = False
    screenshots_on_failure: bool = True


class E2ETestGenerator:
    """E2E Test Generator"""

    def __init__(self, config: E2ETestConfig):
        """
        Initialize E2E test generator

        Args:
            config: Test configuration
        """
        self.config = config
        self.scenarios: List[TestScenario] = []

    def add_scenario(self, scenario: TestScenario):
        """
        Add test scenario

        Args:
            scenario: Test scenario
        """
        self.scenarios.append(scenario)
        print(f"✅ Added scenario: {scenario.name}")

    def generate_tests(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate E2E tests

        Args:
            output_dir: Output directory

        Returns:
            Generated test files
        """
        print(f"🧪 Generating E2E tests ({self.config.framework.value})...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        if self.config.framework == E2EFramework.PLAYWRIGHT:
            files.update(self._generate_playwright_tests(output_dir))
        elif self.config.framework == E2EFramework.CYPRESS:
            files.update(self._generate_cypress_tests(output_dir))
        elif self.config.framework == E2EFramework.SELENIUM:
            files.update(self._generate_selenium_tests(output_dir))

        # Generate configuration
        files.update(self._generate_config(output_dir))

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} test files")
        return files

    def _generate_playwright_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate Playwright tests"""
        files = {}

        # Generate test file for each scenario
        for scenario in self.scenarios:
            test_name = scenario.name.lower().replace(' ', '_')
            files[f'tests/{test_name}.spec.ts'] = self._generate_playwright_scenario(scenario)

        # Generate playwright config
        files['playwright.config.ts'] = self._generate_playwright_config()

        # Generate package.json
        files['package.json'] = self._generate_playwright_package_json()

        # Generate helpers
        files['tests/helpers.ts'] = self._generate_playwright_helpers()

        return files

    def _generate_playwright_scenario(self, scenario: TestScenario) -> str:
        """Generate Playwright test scenario"""
        actions_code = []

        for action in scenario.actions:
            if action.type == ActionType.NAVIGATE:
                actions_code.append(f"  await page.goto('{action.value}');")
            elif action.type == ActionType.CLICK:
                actions_code.append(f"  await page.click('{action.selector}');")
            elif action.type == ActionType.FILL:
                actions_code.append(f"  await page.fill('{action.selector}', '{action.value}');")
            elif action.type == ActionType.WAIT:
                actions_code.append(f"  await page.waitForSelector('{action.selector}');")
            elif action.type == ActionType.ASSERT:
                actions_code.append(f"  await expect(page.locator('{action.selector}')).toContainText('{action.value}');")
            elif action.type == ActionType.SCREENSHOT:
                actions_code.append(f"  await page.screenshot({{ path: '{action.value}' }});")

        return f"""import {{ test, expect }} from '@playwright/test';

test.describe('{scenario.name}', () => {{
  test('{scenario.description}', async ({{ page }}) => {{
    // Navigate to base URL
    await page.goto('{scenario.url}');

    // Test actions
{chr(10).join(actions_code)}
  }});
}});
"""

    def _generate_playwright_config(self) -> str:
        """Generate Playwright configuration"""
        browsers = [b.value for b in self.config.browsers] or ['chromium']

        return f"""import {{ defineConfig, devices }} from '@playwright/test';

export default defineConfig({{
  testDir: './tests',
  timeout: {self.config.timeout},
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {{
    baseURL: '{self.config.base_url}',
    trace: 'on-first-retry',
    screenshot: '{"on" if self.config.screenshots_on_failure else "off"}',
    video: '{"on" if self.config.record_video else "off"}',
  }},

  projects: [
    {{
      name: 'chromium',
      use: {{ ...devices['Desktop Chrome'] }},
    }},
    {{
      name: 'firefox',
      use: {{ ...devices['Desktop Firefox'] }},
    }},
    {{
      name: 'webkit',
      use: {{ ...devices['Desktop Safari'] }},
    }},
  ],

  webServer: {{
    command: 'npm run dev',
    url: '{self.config.base_url}',
    reuseExistingServer: !process.env.CI,
  }},
}});
"""

    def _generate_playwright_package_json(self) -> str:
        """Generate package.json for Playwright"""
        return json.dumps({
            "name": "e2e-tests",
            "version": "1.0.0",
            "scripts": {
                "test": "playwright test",
                "test:headed": "playwright test --headed",
                "test:debug": "playwright test --debug",
                "report": "playwright show-report"
            },
            "devDependencies": {
                "@playwright/test": "^1.40.0"
            }
        }, indent=2)

    def _generate_playwright_helpers(self) -> str:
        """Generate Playwright helper functions"""
        return """import { Page, expect } from '@playwright/test';

export async function login(page: Page, email: string, password: string) {
  await page.fill('[name="email"]', email);
  await page.fill('[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForNavigation();
}

export async function logout(page: Page) {
  await page.click('[data-testid="logout-button"]');
  await page.waitForURL('**/login');
}

export async function fillForm(page: Page, data: Record<string, string>) {
  for (const [field, value] of Object.entries(data)) {
    await page.fill(`[name="${field}"]`, value);
  }
}

export async function waitForApiResponse(
  page: Page,
  urlPattern: string,
  callback: () => Promise<void>
) {
  const responsePromise = page.waitForResponse(
    response => response.url().includes(urlPattern) && response.status() === 200
  );
  await callback();
  return await responsePromise;
}
"""

    def _generate_cypress_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate Cypress tests"""
        files = {}

        for scenario in self.scenarios:
            test_name = scenario.name.lower().replace(' ', '_')
            files[f'cypress/e2e/{test_name}.cy.ts'] = self._generate_cypress_scenario(scenario)

        files['cypress.config.ts'] = self._generate_cypress_config()
        files['package.json'] = self._generate_cypress_package_json()
        files['cypress/support/commands.ts'] = self._generate_cypress_commands()

        return files

    def _generate_cypress_scenario(self, scenario: TestScenario) -> str:
        """Generate Cypress test scenario"""
        actions_code = []

        for action in scenario.actions:
            if action.type == ActionType.NAVIGATE:
                actions_code.append(f"    cy.visit('{action.value}');")
            elif action.type == ActionType.CLICK:
                actions_code.append(f"    cy.get('{action.selector}').click();")
            elif action.type == ActionType.FILL:
                actions_code.append(f"    cy.get('{action.selector}').type('{action.value}');")
            elif action.type == ActionType.WAIT:
                actions_code.append(f"    cy.get('{action.selector}').should('be.visible');")
            elif action.type == ActionType.ASSERT:
                actions_code.append(f"    cy.get('{action.selector}').should('contain', '{action.value}');")

        return f"""describe('{scenario.name}', () => {{
  beforeEach(() => {{
    cy.visit('{scenario.url}');
  }});

  it('{scenario.description}', () => {{
{chr(10).join(actions_code)}
  }});
}});
"""

    def _generate_cypress_config(self) -> str:
        """Generate Cypress configuration"""
        return f"""import {{ defineConfig }} from 'cypress';

export default defineConfig({{
  e2e: {{
    baseUrl: '{self.config.base_url}',
    viewportWidth: {self.config.viewport_width},
    viewportHeight: {self.config.viewport_height},
    video: {str(self.config.record_video).lower()},
    screenshotOnRunFailure: {str(self.config.screenshots_on_failure).lower()},
    setupNodeEvents(on, config) {{
      // implement node event listeners here
    }},
  }},
}});
"""

    def _generate_cypress_package_json(self) -> str:
        """Generate package.json for Cypress"""
        return json.dumps({
            "name": "cypress-tests",
            "version": "1.0.0",
            "scripts": {
                "test": "cypress run",
                "test:open": "cypress open",
                "test:headed": "cypress run --headed"
            },
            "devDependencies": {
                "cypress": "^13.6.0"
            }
        }, indent=2)

    def _generate_cypress_commands(self) -> str:
        """Generate Cypress custom commands"""
        return """/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
      fillForm(data: Record<string, string>): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (email: string, password: string) => {
  cy.get('[name="email"]').type(email);
  cy.get('[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
  cy.url().should('not.include', '/login');
});

Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="logout-button"]').click();
  cy.url().should('include', '/login');
});

Cypress.Commands.add('fillForm', (data: Record<string, string>) => {
  Object.entries(data).forEach(([field, value]) => {
    cy.get(`[name="${field}"]`).type(value);
  });
});

export {};
"""

    def _generate_selenium_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate Selenium tests"""
        files = {}

        for scenario in self.scenarios:
            test_name = scenario.name.lower().replace(' ', '_')
            files[f'tests/test_{test_name}.py'] = self._generate_selenium_scenario(scenario)

        files['conftest.py'] = self._generate_selenium_conftest()
        files['requirements.txt'] = self._generate_selenium_requirements()

        return files

    def _generate_selenium_scenario(self, scenario: TestScenario) -> str:
        """Generate Selenium test scenario"""
        actions_code = []

        for action in scenario.actions:
            if action.type == ActionType.NAVIGATE:
                actions_code.append(f"    driver.get('{action.value}')")
            elif action.type == ActionType.CLICK:
                actions_code.append(f"    driver.find_element(By.CSS_SELECTOR, '{action.selector}').click()")
            elif action.type == ActionType.FILL:
                actions_code.append(f"    driver.find_element(By.CSS_SELECTOR, '{action.selector}').send_keys('{action.value}')")
            elif action.type == ActionType.WAIT:
                actions_code.append(f"    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '{action.selector}')))")
            elif action.type == ActionType.ASSERT:
                actions_code.append(f"    assert '{action.value}' in driver.find_element(By.CSS_SELECTOR, '{action.selector}').text")

        return f"""import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_{scenario.name.lower().replace(' ', '_')}(driver):
    \"\"\"
    {scenario.description}
    \"\"\"
    # Navigate to page
    driver.get('{scenario.url}')

    # Test actions
{chr(10).join(actions_code)}
"""

    def _generate_selenium_conftest(self) -> str:
        """Generate Selenium pytest configuration"""
        return f"""import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    \"\"\"Create WebDriver instance\"\"\"
    options = Options()
    {'options.add_argument("--headless")' if self.config.headless else ''}
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size({self.config.viewport_width}, {self.config.viewport_height})

    yield driver

    driver.quit()

@pytest.fixture
def base_url():
    return '{self.config.base_url}'
"""

    def _generate_selenium_requirements(self) -> str:
        """Generate requirements.txt for Selenium"""
        return """selenium>=4.15.0
pytest>=7.4.0
pytest-xdist>=3.5.0
webdriver-manager>=4.0.1
"""

    def _generate_config(self, output_dir: Path) -> Dict[str, str]:
        """Generate general configuration files"""
        files = {}

        # Generate .gitignore
        files['.gitignore'] = """node_modules/
test-results/
playwright-report/
cypress/videos/
cypress/screenshots/
__pycache__/
*.pyc
.pytest_cache/
"""

        # Generate README
        files['README.md'] = f"""# E2E Tests

Generated E2E tests using {self.config.framework.value.upper()}.

## Setup

```bash
{"npm install" if self.config.framework in [E2EFramework.PLAYWRIGHT, E2EFramework.CYPRESS] else "pip install -r requirements.txt"}
```

## Run Tests

```bash
{"npm test" if self.config.framework in [E2EFramework.PLAYWRIGHT, E2EFramework.CYPRESS] else "pytest"}
```

## Configuration

- Base URL: {self.config.base_url}
- Viewport: {self.config.viewport_width}x{self.config.viewport_height}
- Timeout: {self.config.timeout}ms
- Headless: {self.config.headless}

## Scenarios

{chr(10).join([f"- {s.name}: {s.description}" for s in self.scenarios])}
"""

        return files

    def record_user_flow(
        self,
        scenario_name: str,
        description: str,
        start_url: str
    ) -> TestScenario:
        """
        Create scenario for recording user flow

        Args:
            scenario_name: Scenario name
            description: Scenario description
            start_url: Starting URL

        Returns:
            Empty scenario ready for recording
        """
        scenario = TestScenario(
            name=scenario_name,
            description=description,
            url=start_url
        )

        print(f"🎥 Created scenario for recording: {scenario_name}")
        return scenario

    def generate_from_har(self, har_file: Path) -> List[TestScenario]:
        """
        Generate test scenarios from HAR file

        Args:
            har_file: HAR file path

        Returns:
            Generated scenarios
        """
        print(f"📄 Generating tests from HAR: {har_file}")

        # Parse HAR file (simplified)
        scenarios = []

        # In production, parse HAR and extract user interactions
        # For now, return empty list

        return scenarios
