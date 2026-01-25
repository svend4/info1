#!/usr/bin/env python3
"""
Policy as Code Generator

Автоматическая генерация policy definitions для OPA, Kyverno, и admission controllers.
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class PolicyEngine(Enum):
    """Policy Engine"""
    OPA = "opa"  # Open Policy Agent
    KYVERNO = "kyverno"
    GATEKEEPER = "gatekeeper"  # OPA Gatekeeper


class PolicyAction(Enum):
    """Policy Action"""
    ENFORCE = "enforce"
    AUDIT = "audit"
    WARN = "warn"
    DENY = "deny"


class ResourceKind(Enum):
    """Kubernetes Resource Kind"""
    POD = "Pod"
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    INGRESS = "Ingress"
    NAMESPACE = "Namespace"
    CONFIGMAP = "ConfigMap"


@dataclass
class PolicyRule:
    """Policy Rule"""
    name: str
    description: str
    kind: ResourceKind
    action: PolicyAction
    conditions: Dict[str, Any] = field(default_factory=dict)
    rego_code: Optional[str] = None  # For OPA
    validations: List[Dict[str, Any]] = field(default_factory=list)  # For Kyverno


@dataclass
class PolicyConfig:
    """Policy as Code Configuration"""
    engine: PolicyEngine
    policies: List[PolicyRule] = field(default_factory=list)
    enable_audit_mode: bool = False


class PolicyAsCodeGenerator:
    """Policy as Code Generator"""

    def __init__(self, config: PolicyConfig):
        """
        Initialize policy generator

        Args:
            config: Policy configuration
        """
        self.config = config

    def add_policy(self, policy: PolicyRule):
        """
        Add policy rule

        Args:
            policy: Policy rule
        """
        self.config.policies.append(policy)
        print(f"✅ Added policy: {policy.name}")

    def generate(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate policy code

        Args:
            output_dir: Output directory

        Returns:
            Generated files
        """
        print(f"🔐 Generating Policy as Code ({self.config.engine.value})...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        if self.config.engine == PolicyEngine.OPA:
            files.update(self._generate_opa_policies(output_dir))
        elif self.config.engine == PolicyEngine.KYVERNO:
            files.update(self._generate_kyverno_policies(output_dir))
        elif self.config.engine == PolicyEngine.GATEKEEPER:
            files.update(self._generate_gatekeeper_policies(output_dir))

        # Common files
        files['README.md'] = self._generate_readme()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} policy files")
        return files

    def _generate_opa_policies(self, output_dir: Path) -> Dict[str, str]:
        """Generate OPA policies"""
        files = {}

        # Generate Rego policies
        for policy in self.config.policies:
            files[f'policies/{policy.name}.rego'] = self._generate_rego_policy(policy)

        # Generate test cases
        for policy in self.config.policies:
            files[f'policies/{policy.name}_test.rego'] = self._generate_rego_test(policy)

        # Generate OPA configuration
        files['opa-config.yaml'] = self._generate_opa_config()

        # Generate deployment
        files['deployment.yaml'] = self._generate_opa_deployment()

        return files

    def _generate_rego_policy(self, policy: PolicyRule) -> str:
        """Generate Rego policy code"""
        if policy.rego_code:
            return policy.rego_code

        # Generate basic Rego based on conditions
        package_name = policy.name.replace('-', '_')

        if policy.kind == ResourceKind.POD:
            return f"""package {package_name}

# {policy.description}

deny[msg] {{
    input.kind == "Pod"
    {self._generate_rego_conditions(policy.conditions)}
    msg := "{policy.description}"
}}
"""
        elif policy.kind == ResourceKind.DEPLOYMENT:
            return f"""package {package_name}

# {policy.description}

violation[{{"msg": msg}}] {{
    input.kind == "Deployment"
    {self._generate_rego_conditions(policy.conditions)}
    msg := sprintf("{policy.description}: %v", [input.metadata.name])
}}
"""
        else:
            return f"""package {package_name}

# {policy.description}

deny[msg] {{
    input.kind == "{policy.kind.value}"
    {self._generate_rego_conditions(policy.conditions)}
    msg := "{policy.description}"
}}
"""

    def _generate_rego_conditions(self, conditions: Dict[str, Any]) -> str:
        """Generate Rego conditions from dictionary"""
        rego_lines = []

        if 'no_root' in conditions:
            rego_lines.append("container := input.spec.containers[_]")
            rego_lines.append("container.securityContext.runAsUser == 0")

        if 'require_labels' in conditions:
            for label in conditions['require_labels']:
                rego_lines.append(f'not input.metadata.labels["{label}"]')

        if 'max_replicas' in conditions:
            max_replicas = conditions['max_replicas']
            rego_lines.append(f"input.spec.replicas > {max_replicas}")

        if 'required_probes' in conditions:
            rego_lines.append("container := input.spec.containers[_]")
            rego_lines.append("not container.livenessProbe")

        return "\n    ".join(rego_lines) if rego_lines else "true"

    def _generate_rego_test(self, policy: PolicyRule) -> str:
        """Generate Rego test cases"""
        package_name = policy.name.replace('-', '_')

        return f"""package {package_name}

test_deny_running_as_root {{
    deny["test"] with input as {{
        "kind": "{policy.kind.value}",
        "metadata": {{"name": "test"}},
        "spec": {{
            "containers": [{{
                "name": "test",
                "securityContext": {{"runAsUser": 0}}
            }}]
        }}
    }}
}}

test_allow_non_root {{
    not deny["test"] with input as {{
        "kind": "{policy.kind.value}",
        "metadata": {{"name": "test"}},
        "spec": {{
            "containers": [{{
                "name": "test",
                "securityContext": {{"runAsUser": 1000}}
            }}]
        }}
    }}
}}
"""

    def _generate_opa_config(self) -> str:
        """Generate OPA configuration"""
        config = {
            'services': {
                'kubernetes': {
                    'url': 'https://kubernetes.default.svc',
                    'credentials': {
                        'bearer': {
                            'token_path': '/var/run/secrets/kubernetes.io/serviceaccount/token'
                        }
                    }
                }
            },
            'labels': {
                'environment': 'production'
            }
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_opa_deployment(self) -> str:
        """Generate OPA Kubernetes deployment"""
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'opa',
                'namespace': 'opa'
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {'app': 'opa'}
                },
                'template': {
                    'metadata': {
                        'labels': {'app': 'opa'}
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'opa',
                                'image': 'openpolicyagent/opa:latest',
                                'args': [
                                    'run',
                                    '--server',
                                    '--addr=0.0.0.0:8181',
                                    '/policies'
                                ],
                                'ports': [{'containerPort': 8181}],
                                'volumeMounts': [
                                    {
                                        'name': 'policies',
                                        'mountPath': '/policies'
                                    }
                                ]
                            }
                        ],
                        'volumes': [
                            {
                                'name': 'policies',
                                'configMap': {
                                    'name': 'opa-policies'
                                }
                            }
                        ]
                    }
                }
            }
        }

        return yaml.dump(deployment, default_flow_style=False)

    def _generate_kyverno_policies(self, output_dir: Path) -> Dict[str, str]:
        """Generate Kyverno policies"""
        files = {}

        for policy in self.config.policies:
            files[f'policies/{policy.name}.yaml'] = self._generate_kyverno_policy(policy)

        # Generate Kyverno installation
        files['install.yaml'] = self._generate_kyverno_install()

        return files

    def _generate_kyverno_policy(self, policy: PolicyRule) -> str:
        """Generate Kyverno policy"""
        validation_rules = []

        if policy.validations:
            validation_rules = policy.validations
        else:
            # Generate default validations based on conditions
            if 'no_root' in policy.conditions:
                validation_rules.append({
                    'message': 'Running as root is not allowed',
                    'pattern': {
                        'spec': {
                            'containers': [
                                {
                                    'securityContext': {
                                        'runAsNonRoot': True
                                    }
                                }
                            ]
                        }
                    }
                })

            if 'require_labels' in policy.conditions:
                required_labels = {}
                for label in policy.conditions['require_labels']:
                    required_labels[label] = '?*'

                validation_rules.append({
                    'message': f'Required labels are missing: {", ".join(policy.conditions["require_labels"])}',
                    'pattern': {
                        'metadata': {
                            'labels': required_labels
                        }
                    }
                })

        kyverno_policy = {
            'apiVersion': 'kyverno.io/v1',
            'kind': 'ClusterPolicy',
            'metadata': {
                'name': policy.name
            },
            'spec': {
                'validationFailureAction': policy.action.value if policy.action != PolicyAction.DENY else 'Enforce',
                'background': True,
                'rules': [
                    {
                        'name': policy.name,
                        'match': {
                            'any': [
                                {
                                    'resources': {
                                        'kinds': [policy.kind.value]
                                    }
                                }
                            ]
                        },
                        'validate': {
                            'message': policy.description,
                            **(validation_rules[0] if validation_rules else {})
                        }
                    }
                ]
            }
        }

        return yaml.dump(kyverno_policy, default_flow_style=False)

    def _generate_kyverno_install(self) -> str:
        """Generate Kyverno installation instructions"""
        return """# Kyverno Installation

kubectl create -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml

# Verify installation
kubectl get pods -n kyverno
"""

    def _generate_gatekeeper_policies(self, output_dir: Path) -> Dict[str, str]:
        """Generate OPA Gatekeeper policies"""
        files = {}

        for policy in self.config.policies:
            # Generate ConstraintTemplate
            files[f'templates/{policy.name}-template.yaml'] = self._generate_constraint_template(policy)

            # Generate Constraint
            files[f'constraints/{policy.name}-constraint.yaml'] = self._generate_constraint(policy)

        # Generate Gatekeeper installation
        files['install.yaml'] = self._generate_gatekeeper_install()

        return files

    def _generate_constraint_template(self, policy: PolicyRule) -> str:
        """Generate Gatekeeper ConstraintTemplate"""
        template_name = f'{policy.name.title().replace("-", "")}'

        template = {
            'apiVersion': 'templates.gatekeeper.sh/v1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': policy.name
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': template_name
                        }
                    }
                },
                'targets': [
                    {
                        'target': 'admission.k8s.gatekeeper.sh',
                        'rego': self._generate_rego_policy(policy)
                    }
                ]
            }
        }

        return yaml.dump(template, default_flow_style=False)

    def _generate_constraint(self, policy: PolicyRule) -> str:
        """Generate Gatekeeper Constraint"""
        template_name = f'{policy.name.title().replace("-", "")}'

        constraint = {
            'apiVersion': 'constraints.gatekeeper.sh/v1beta1',
            'kind': template_name,
            'metadata': {
                'name': policy.name
            },
            'spec': {
                'match': {
                    'kinds': [
                        {
                            'apiGroups': [''],
                            'kinds': [policy.kind.value]
                        }
                    ]
                },
                'parameters': {}
            }
        }

        return yaml.dump(constraint, default_flow_style=False)

    def _generate_gatekeeper_install(self) -> str:
        """Generate Gatekeeper installation instructions"""
        return """# OPA Gatekeeper Installation

kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Verify installation
kubectl get pods -n gatekeeper-system
"""

    def _generate_readme(self) -> str:
        """Generate README"""
        return f"""# Policy as Code

Kubernetes policy management using {self.config.engine.value.upper()}.

## Policies

{chr(10).join([f"- **{p.name}**: {p.description} (Action: {p.action.value})" for p in self.config.policies])}

## Setup

### {self.config.engine.value.upper()} Installation

```bash
# Install {self.config.engine.value}
{'kubectl apply -f install.yaml' if self.config.engine in [PolicyEngine.KYVERNO, PolicyEngine.GATEKEEPER] else 'helm install opa stable/opa'}
```

## Apply Policies

```bash
# Apply all policies
kubectl apply -f policies/

{f'# Apply constraints (Gatekeeper)' if self.config.engine == PolicyEngine.GATEKEEPER else ''}
{f'kubectl apply -f constraints/' if self.config.engine == PolicyEngine.GATEKEEPER else ''}
```

## Test Policies

```bash
{self._generate_test_commands()}
```

## Policy Engine

- **Engine**: {self.config.engine.value.upper()}
- **Audit Mode**: {'Enabled' if self.config.enable_audit_mode else 'Disabled'}
- **Total Policies**: {len(self.config.policies)}
"""

    def _generate_test_commands(self) -> str:
        """Generate test commands for policy engine"""
        if self.config.engine == PolicyEngine.OPA:
            return """# Test OPA policies
opa test policies/

# Evaluate policy
opa eval -d policies/ -i input.json "data.{package_name}.deny"
"""
        elif self.config.engine == PolicyEngine.KYVERNO:
            return """# Test with kubectl
kubectl run test-pod --image=nginx --dry-run=server

# View policy reports
kubectl get policyreport -A
"""
        else:  # Gatekeeper
            return """# Test constraint
kubectl apply -f test-resource.yaml --dry-run=server

# View constraint status
kubectl get constraint
"""

    def create_security_policies(self) -> List[PolicyRule]:
        """Create common security policies"""
        policies = [
            PolicyRule(
                name="no-privileged-containers",
                description="Prohibit privileged containers",
                kind=ResourceKind.POD,
                action=PolicyAction.DENY,
                conditions={'privileged': False}
            ),
            PolicyRule(
                name="require-non-root",
                description="Containers must not run as root",
                kind=ResourceKind.POD,
                action=PolicyAction.ENFORCE,
                conditions={'no_root': True}
            ),
            PolicyRule(
                name="require-labels",
                description="Require specific labels on resources",
                kind=ResourceKind.DEPLOYMENT,
                action=PolicyAction.WARN,
                conditions={'require_labels': ['app', 'environment']}
            ),
            PolicyRule(
                name="limit-replicas",
                description="Limit maximum replicas",
                kind=ResourceKind.DEPLOYMENT,
                action=PolicyAction.AUDIT,
                conditions={'max_replicas': 10}
            ),
            PolicyRule(
                name="require-probes",
                description="Require liveness and readiness probes",
                kind=ResourceKind.DEPLOYMENT,
                action=PolicyAction.WARN,
                conditions={'required_probes': True}
            )
        ]

        for policy in policies:
            self.add_policy(policy)

        return policies
