#!/usr/bin/env python3
"""
Load Test Generator

Автоматическая генерация load tests для k6, Locust, и JMeter.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class LoadTestFramework(Enum):
    """Load Testing Framework"""
    K6 = "k6"
    LOCUST = "locust"
    JMETER = "jmeter"
    ARTILLERY = "artillery"


class LoadProfile(Enum):
    """Load Testing Profile"""
    CONSTANT = "constant"  # Constant VUs
    RAMP_UP = "ramp_up"  # Gradual increase
    SPIKE = "spike"  # Sudden spike
    STRESS = "stress"  # Increasing load to find breaking point
    SOAK = "soak"  # Sustained load over long period


class HTTPMethod(Enum):
    """HTTP Method"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class HTTPRequest:
    """HTTP Request Configuration"""
    method: HTTPMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    params: Dict[str, str] = field(default_factory=dict)
    expected_status: int = 200
    think_time: float = 1.0  # Seconds


@dataclass
class LoadScenario:
    """Load Test Scenario"""
    name: str
    requests: List[HTTPRequest] = field(default_factory=list)
    weight: int = 1  # Scenario weight for distribution


@dataclass
class LoadTestConfig:
    """Load Test Configuration"""
    framework: LoadTestFramework
    profile: LoadProfile
    vus: int = 10  # Virtual users
    duration: str = "30s"
    ramp_up_time: str = "10s"
    thresholds: Dict[str, List[str]] = field(default_factory=dict)
    base_url: str = "http://localhost"


class LoadTestGenerator:
    """Load Test Generator"""

    def __init__(self, config: LoadTestConfig):
        """
        Initialize load test generator

        Args:
            config: Load test configuration
        """
        self.config = config
        self.scenarios: List[LoadScenario] = []

    def add_scenario(self, scenario: LoadScenario):
        """
        Add test scenario

        Args:
            scenario: Load test scenario
        """
        self.scenarios.append(scenario)
        print(f"✅ Added scenario: {scenario.name}")

    def generate_tests(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate load tests

        Args:
            output_dir: Output directory

        Returns:
            Generated test files
        """
        print(f"⚡ Generating load tests ({self.config.framework.value})...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        if self.config.framework == LoadTestFramework.K6:
            files.update(self._generate_k6_tests(output_dir))
        elif self.config.framework == LoadTestFramework.LOCUST:
            files.update(self._generate_locust_tests(output_dir))
        elif self.config.framework == LoadTestFramework.JMETER:
            files.update(self._generate_jmeter_tests(output_dir))
        elif self.config.framework == LoadTestFramework.ARTILLERY:
            files.update(self._generate_artillery_tests(output_dir))

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} test files")
        return files

    def _generate_k6_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate k6 tests"""
        files = {}

        # Generate main test file
        files['load-test.js'] = self._generate_k6_script()

        # Generate config
        files['k6-config.json'] = self._generate_k6_config()

        # Generate README
        files['README.md'] = self._generate_k6_readme()

        # Generate run script
        files['run.sh'] = self._generate_k6_run_script()

        return files

    def _generate_k6_script(self) -> str:
        """Generate k6 JavaScript test script"""
        # Generate scenarios
        scenarios_code = []

        for scenario in self.scenarios:
            requests_code = []

            for req in scenario.requests:
                # Build request
                if req.method == HTTPMethod.GET:
                    requests_code.append(f"""
    // {req.method.value} {req.url}
    let response = http.get('{self.config.base_url}{req.url}', {{
      headers: {json.dumps(req.headers)},
    }});
    check(response, {{
      'status is {req.expected_status}': (r) => r.status === {req.expected_status},
      'response time < 500ms': (r) => r.timings.duration < 500,
    }});
    sleep({req.think_time});
""")

                elif req.method == HTTPMethod.POST:
                    requests_code.append(f"""
    // {req.method.value} {req.url}
    let response = http.post('{self.config.base_url}{req.url}', {json.dumps(req.body or '{}')}, {{
      headers: {json.dumps(req.headers)},
    }});
    check(response, {{
      'status is {req.expected_status}': (r) => r.status === {req.expected_status},
    }});
    sleep({req.think_time});
""")

            scenario_func = f"""
function {scenario.name.replace(' ', '_')}() {{
    {''.join(requests_code)}
}}
"""
            scenarios_code.append(scenario_func)

        # Generate options based on profile
        options = self._generate_k6_options()

        return f"""import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate, Trend }} from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

// Test configuration
export const options = {options};

// Scenarios
{''.join(scenarios_code)}

// Main test function
export default function() {{
    // Execute scenarios based on weight
    {self._generate_k6_scenario_execution()}
}}

// Setup (runs once)
export function setup() {{
    console.log('Starting load test...');
    return {{ baseURL: '{self.config.base_url}' }};
}}

// Teardown (runs once)
export function teardown(data) {{
    console.log('Load test completed');
}}
"""

    def _generate_k6_options(self) -> str:
        """Generate k6 options based on load profile"""
        thresholds = self.config.thresholds or {
            'http_req_duration': ['p(95)<500', 'p(99)<1000'],
            'http_req_failed': ['rate<0.01'],
        }

        if self.config.profile == LoadProfile.CONSTANT:
            return json.dumps({
                'vus': self.config.vus,
                'duration': self.config.duration,
                'thresholds': thresholds
            }, indent=2)

        elif self.config.profile == LoadProfile.RAMP_UP:
            return json.dumps({
                'stages': [
                    {'duration': self.config.ramp_up_time, 'target': self.config.vus},
                    {'duration': self.config.duration, 'target': self.config.vus},
                ],
                'thresholds': thresholds
            }, indent=2)

        elif self.config.profile == LoadProfile.SPIKE:
            return json.dumps({
                'stages': [
                    {'duration': '10s', 'target': 10},
                    {'duration': '1m', 'target': self.config.vus},  # Spike
                    {'duration': '10s', 'target': 10},
                ],
                'thresholds': thresholds
            }, indent=2)

        elif self.config.profile == LoadProfile.STRESS:
            return json.dumps({
                'stages': [
                    {'duration': '2m', 'target': 100},
                    {'duration': '5m', 'target': 200},
                    {'duration': '2m', 'target': 300},
                    {'duration': '5m', 'target': 400},
                    {'duration': '2m', 'target': 0},
                ],
                'thresholds': thresholds
            }, indent=2)

        elif self.config.profile == LoadProfile.SOAK:
            return json.dumps({
                'stages': [
                    {'duration': '5m', 'target': self.config.vus},
                    {'duration': '3h', 'target': self.config.vus},  # Soak
                    {'duration': '5m', 'target': 0},
                ],
                'thresholds': thresholds
            }, indent=2)

    def _generate_k6_scenario_execution(self) -> str:
        """Generate scenario execution code"""
        if not self.scenarios:
            return "// No scenarios defined"

        # Simple execution based on weights
        total_weight = sum(s.weight for s in self.scenarios)
        code = []

        for scenario in self.scenarios:
            probability = scenario.weight / total_weight
            code.append(f"if (Math.random() < {probability:.2f}) {{")
            code.append(f"    {scenario.name.replace(' ', '_')}();")
            code.append("}")

        return '\n    '.join(code)

    def _generate_k6_config(self) -> str:
        """Generate k6 configuration file"""
        return json.dumps({
            'out': ['json=results.json', 'influxdb=http://localhost:8086/k6'],
            'no-color': False,
            'verbose': True
        }, indent=2)

    def _generate_k6_readme(self) -> str:
        """Generate README for k6"""
        return f"""# Load Tests (k6)

## Configuration

- Load Profile: {self.config.profile.value}
- Virtual Users: {self.config.vus}
- Duration: {self.config.duration}
- Base URL: {self.config.base_url}

## Run Tests

```bash
# Install k6
brew install k6  # macOS
# or
choco install k6  # Windows

# Run test
k6 run load-test.js

# Run with custom VUs
k6 run --vus {self.config.vus} --duration {self.config.duration} load-test.js

# Generate HTML report
k6 run --out json=results.json load-test.js
```

## Scenarios

{chr(10).join([f"- {s.name} (weight: {s.weight})" for s in self.scenarios])}

## Thresholds

{chr(10).join([f"- {k}: {v}" for k, v in (self.config.thresholds or {}).items()])}
"""

    def _generate_k6_run_script(self) -> str:
        """Generate k6 run script"""
        return f"""#!/bin/bash

# Run k6 load test

echo "Starting k6 load test..."
echo "Profile: {self.config.profile.value}"
echo "VUs: {self.config.vus}"
echo "Duration: {self.config.duration}"
echo ""

k6 run \\
  --vus {self.config.vus} \\
  --duration {self.config.duration} \\
  --out json=results.json \\
  load-test.js

echo ""
echo "Load test completed"
echo "Results saved to results.json"
"""

    def _generate_locust_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate Locust tests"""
        files = {}

        files['locustfile.py'] = self._generate_locust_script()
        files['requirements.txt'] = "locust>=2.19.0\n"
        files['README.md'] = self._generate_locust_readme()

        return files

    def _generate_locust_script(self) -> str:
        """Generate Locust Python script"""
        tasks = []

        for scenario in self.scenarios:
            task_methods = []

            for i, req in enumerate(scenario.requests):
                method_name = f"request_{i}"

                if req.method == HTTPMethod.GET:
                    task_methods.append(f"""
    @task({scenario.weight})
    def {method_name}(self):
        self.client.get("{req.url}", headers={req.headers})
        time.sleep({req.think_time})
""")

                elif req.method == HTTPMethod.POST:
                    task_methods.append(f"""
    @task({scenario.weight})
    def {method_name}(self):
        self.client.post("{req.url}", json={req.body or '{}'}, headers={req.headers})
        time.sleep({req.think_time})
""")

            class_code = f"""
class {scenario.name.replace(' ', '')}User(HttpUser):
    wait_time = between(1, 3)
    {''.join(task_methods)}
"""
            tasks.append(class_code)

        return f"""from locust import HttpUser, task, between
import time

# Base configuration
host = "{self.config.base_url}"

{''.join(tasks)}
"""

    def _generate_locust_readme(self) -> str:
        """Generate README for Locust"""
        return f"""# Load Tests (Locust)

## Run Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run Locust with web UI
locust -f locustfile.py --host {self.config.base_url}

# Run headless
locust -f locustfile.py --host {self.config.base_url} --users {self.config.vus} --spawn-rate 10 --run-time {self.config.duration} --headless
```

## Access Web UI

Open http://localhost:8089 in your browser.
"""

    def _generate_jmeter_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate JMeter tests"""
        files = {}

        # Generate JMX file (simplified XML structure)
        files['test-plan.jmx'] = self._generate_jmeter_jmx()
        files['README.md'] = self._generate_jmeter_readme()

        return files

    def _generate_jmeter_jmx(self) -> str:
        """Generate JMeter JMX file"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.5">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Load Test">
      <stringProp name="TestPlan.comments">Generated load test</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
        <stringProp name="ThreadGroup.num_threads">{self.config.vus}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">10</stringProp>
        <stringProp name="ThreadGroup.duration">{self.config.duration.rstrip('s')}</stringProp>
      </ThreadGroup>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""

    def _generate_jmeter_readme(self) -> str:
        """Generate README for JMeter"""
        return """# Load Tests (JMeter)

## Run Tests

```bash
# Run JMeter test
jmeter -n -t test-plan.jmx -l results.jtl

# Generate HTML report
jmeter -g results.jtl -o report/
```
"""

    def _generate_artillery_tests(self, output_dir: Path) -> Dict[str, str]:
        """Generate Artillery tests"""
        files = {}

        files['load-test.yml'] = self._generate_artillery_config()
        files['package.json'] = self._generate_artillery_package_json()

        return files

    def _generate_artillery_config(self) -> str:
        """Generate Artillery YAML configuration"""
        scenarios = []

        for scenario in self.scenarios:
            flow = []
            for req in scenario.requests:
                flow.append({
                    req.method.value.lower(): {
                        'url': req.url,
                        'headers': req.headers
                    }
                })
                if req.think_time > 0:
                    flow.append({'think': req.think_time})

            scenarios.append({
                'name': scenario.name,
                'weight': scenario.weight,
                'flow': flow
            })

        config = {
            'config': {
                'target': self.config.base_url,
                'phases': [
                    {
                        'duration': int(self.config.duration.rstrip('s')),
                        'arrivalRate': self.config.vus
                    }
                ]
            },
            'scenarios': scenarios
        }

        import yaml
        return yaml.dump(config, default_flow_style=False)

    def _generate_artillery_package_json(self) -> str:
        """Generate package.json for Artillery"""
        return json.dumps({
            "name": "load-tests",
            "version": "1.0.0",
            "scripts": {
                "test": "artillery run load-test.yml"
            },
            "devDependencies": {
                "artillery": "^2.0.0"
            }
        }, indent=2)

    def create_api_load_scenario(
        self,
        name: str,
        endpoints: List[str]
    ) -> LoadScenario:
        """
        Create load scenario for API endpoints

        Args:
            name: Scenario name
            endpoints: List of endpoint URLs

        Returns:
            Load scenario
        """
        scenario = LoadScenario(name=name)

        for endpoint in endpoints:
            scenario.requests.append(HTTPRequest(
                method=HTTPMethod.GET,
                url=endpoint,
                expected_status=200,
                think_time=1.0
            ))

        self.add_scenario(scenario)
        return scenario
