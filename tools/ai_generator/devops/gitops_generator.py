#!/usr/bin/env python3
"""
GitOps Generator

Автоматическая генерация GitOps configuration для ArgoCD, FluxCD, и Kubernetes manifests.
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class GitOpsTool(Enum):
    """GitOps Tool"""
    ARGOCD = "argocd"
    FLUXCD = "fluxcd"
    JENKINS_X = "jenkinsx"


class SyncPolicy(Enum):
    """Sync Policy"""
    MANUAL = "manual"
    AUTO = "auto"
    AUTO_PRUNE = "auto_prune"


@dataclass
class AppConfig:
    """Application Configuration"""
    name: str
    namespace: str
    repo_url: str
    path: str
    target_revision: str = "HEAD"
    values_file: Optional[str] = None


@dataclass
class GitOpsConfig:
    """GitOps Configuration"""
    tool: GitOpsTool
    cluster_url: str
    apps: List[AppConfig] = field(default_factory=list)
    sync_policy: SyncPolicy = SyncPolicy.AUTO
    project: str = "default"


class GitOpsGenerator:
    """GitOps Configuration Generator"""

    def __init__(self, config: GitOpsConfig):
        """
        Initialize GitOps generator

        Args:
            config: GitOps configuration
        """
        self.config = config

    def generate(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate GitOps configuration

        Args:
            output_dir: Output directory

        Returns:
            Generated files
        """
        print(f"🔄 Generating GitOps configuration ({self.config.tool.value})...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        if self.config.tool == GitOpsTool.ARGOCD:
            files.update(self._generate_argocd_config(output_dir))
        elif self.config.tool == GitOpsTool.FLUXCD:
            files.update(self._generate_fluxcd_config(output_dir))

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} GitOps files")
        return files

    def _generate_argocd_config(self, output_dir: Path) -> Dict[str, str]:
        """Generate ArgoCD configuration"""
        files = {}

        # Install ArgoCD
        files['argocd/install.yaml'] = self._generate_argocd_install()

        # Generate application manifests
        for app in self.config.apps:
            files[f'argocd/apps/{app.name}.yaml'] = self._generate_argocd_application(app)

        # Generate App of Apps pattern
        files['argocd/apps/root-app.yaml'] = self._generate_argocd_app_of_apps()

        # Generate project
        files['argocd/projects/default.yaml'] = self._generate_argocd_project()

        # Generate README
        files['README.md'] = self._generate_argocd_readme()

        return files

    def _generate_argocd_install(self) -> str:
        """Generate ArgoCD installation manifest"""
        return """# ArgoCD Installation

Run:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
"""

    def _generate_argocd_application(self, app: AppConfig) -> str:
        """Generate ArgoCD Application manifest"""
        sync_policy = {}

        if self.config.sync_policy == SyncPolicy.AUTO:
            sync_policy = {
                'automated': {
                    'prune': False,
                    'selfHeal': True
                }
            }
        elif self.config.sync_policy == SyncPolicy.AUTO_PRUNE:
            sync_policy = {
                'automated': {
                    'prune': True,
                    'selfHeal': True
                }
            }

        manifest = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Application',
            'metadata': {
                'name': app.name,
                'namespace': 'argocd',
                'finalizers': ['resources-finalizer.argocd.argoproj.io']
            },
            'spec': {
                'project': self.config.project,
                'source': {
                    'repoURL': app.repo_url,
                    'targetRevision': app.target_revision,
                    'path': app.path
                },
                'destination': {
                    'server': self.config.cluster_url,
                    'namespace': app.namespace
                },
                'syncPolicy': sync_policy
            }
        }

        if app.values_file:
            manifest['spec']['source']['helm'] = {
                'valueFiles': [app.values_file]
            }

        return yaml.dump(manifest, default_flow_style=False)

    def _generate_argocd_app_of_apps(self) -> str:
        """Generate App of Apps pattern"""
        manifest = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Application',
            'metadata': {
                'name': 'root-app',
                'namespace': 'argocd'
            },
            'spec': {
                'project': self.config.project,
                'source': {
                    'repoURL': self.config.apps[0].repo_url if self.config.apps else '',
                    'targetRevision': 'HEAD',
                    'path': 'argocd/apps'
                },
                'destination': {
                    'server': self.config.cluster_url,
                    'namespace': 'argocd'
                },
                'syncPolicy': {
                    'automated': {
                        'prune': True,
                        'selfHeal': True
                    }
                }
            }
        }

        return yaml.dump(manifest, default_flow_style=False)

    def _generate_argocd_project(self) -> str:
        """Generate ArgoCD Project"""
        project = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'AppProject',
            'metadata': {
                'name': self.config.project,
                'namespace': 'argocd'
            },
            'spec': {
                'description': 'Default project',
                'sourceRepos': ['*'],
                'destinations': [
                    {
                        'namespace': '*',
                        'server': '*'
                    }
                ],
                'clusterResourceWhitelist': [
                    {
                        'group': '*',
                        'kind': '*'
                    }
                ]
            }
        }

        return yaml.dump(project, default_flow_style=False)

    def _generate_argocd_readme(self) -> str:
        """Generate ArgoCD README"""
        return f"""# GitOps with ArgoCD

## Applications

{chr(10).join([f"- **{app.name}**: {app.repo_url}/{app.path}" for app in self.config.apps])}

## Setup

1. Install ArgoCD:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f argocd/install.yaml
```

2. Access ArgoCD UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

3. Login (admin/password from secret):
```bash
argocd login localhost:8080
```

4. Create applications:
```bash
kubectl apply -f argocd/apps/
```

## Sync Policy

- **Policy**: {self.config.sync_policy.value}
- **Auto-sync**: {"Yes" if self.config.sync_policy != SyncPolicy.MANUAL else "No"}
- **Auto-prune**: {"Yes" if self.config.sync_policy == SyncPolicy.AUTO_PRUNE else "No"}

## ArgoCD CLI

```bash
# List apps
argocd app list

# Sync app
argocd app sync {self.config.apps[0].name if self.config.apps else 'app-name'}

# Get app details
argocd app get {self.config.apps[0].name if self.config.apps else 'app-name'}

# Delete app
argocd app delete {self.config.apps[0].name if self.config.apps else 'app-name'}
```
"""

    def _generate_fluxcd_config(self, output_dir: Path) -> Dict[str, str]:
        """Generate FluxCD configuration"""
        files = {}

        # Bootstrap FluxCD
        files['flux/bootstrap.sh'] = self._generate_flux_bootstrap()

        # Generate GitRepository
        for app in self.config.apps:
            files[f'flux/sources/{app.name}-source.yaml'] = self._generate_flux_git_repository(app)
            files[f'flux/kustomizations/{app.name}-kustomization.yaml'] = self._generate_flux_kustomization(app)

        # Generate README
        files['README.md'] = self._generate_flux_readme()

        return files

    def _generate_flux_bootstrap(self) -> str:
        """Generate FluxCD bootstrap script"""
        return """#!/bin/bash

# Bootstrap FluxCD

flux bootstrap github \\
  --owner=YOUR_GITHUB_USERNAME \\
  --repository=YOUR_REPO_NAME \\
  --branch=main \\
  --path=./clusters/production \\
  --personal

echo "FluxCD bootstrapped successfully"
"""

    def _generate_flux_git_repository(self, app: AppConfig) -> str:
        """Generate FluxCD GitRepository"""
        manifest = {
            'apiVersion': 'source.toolkit.fluxcd.io/v1',
            'kind': 'GitRepository',
            'metadata': {
                'name': f"{app.name}-source",
                'namespace': 'flux-system'
            },
            'spec': {
                'interval': '1m',
                'url': app.repo_url,
                'ref': {
                    'branch': app.target_revision
                }
            }
        }

        return yaml.dump(manifest, default_flow_style=False)

    def _generate_flux_kustomization(self, app: AppConfig) -> str:
        """Generate FluxCD Kustomization"""
        manifest = {
            'apiVersion': 'kustomize.toolkit.fluxcd.io/v1',
            'kind': 'Kustomization',
            'metadata': {
                'name': app.name,
                'namespace': 'flux-system'
            },
            'spec': {
                'interval': '5m',
                'path': app.path,
                'prune': self.config.sync_policy == SyncPolicy.AUTO_PRUNE,
                'sourceRef': {
                    'kind': 'GitRepository',
                    'name': f"{app.name}-source"
                },
                'targetNamespace': app.namespace
            }
        }

        return yaml.dump(manifest, default_flow_style=False)

    def _generate_flux_readme(self) -> str:
        """Generate FluxCD README"""
        return """# GitOps with FluxCD

## Install Flux CLI

```bash
curl -s https://fluxcd.io/install.sh | sudo bash
```

## Bootstrap

```bash
flux bootstrap github \\
  --owner=YOUR_GITHUB_USERNAME \\
  --repository=YOUR_REPO_NAME \\
  --branch=main \\
  --path=./clusters/production \\
  --personal
```

## Apply manifests

```bash
kubectl apply -f flux/sources/
kubectl apply -f flux/kustomizations/
```

## Flux CLI commands

```bash
# Check Flux components
flux check

# Get sources
flux get sources git

# Get kustomizations
flux get kustomizations

# Reconcile source
flux reconcile source git <name>

# Suspend/resume
flux suspend kustomization <name>
flux resume kustomization <name>
```
"""

    def create_kubernetes_manifests(
        self,
        app_name: str,
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Create basic Kubernetes manifests

        Args:
            app_name: Application name
            output_dir: Output directory

        Returns:
            Generated manifests
        """
        files = {}

        # Deployment
        files[f'k8s/{app_name}/deployment.yaml'] = self._generate_deployment(app_name)

        # Service
        files[f'k8s/{app_name}/service.yaml'] = self._generate_service(app_name)

        # Ingress
        files[f'k8s/{app_name}/ingress.yaml'] = self._generate_ingress(app_name)

        # ConfigMap
        files[f'k8s/{app_name}/configmap.yaml'] = self._generate_configmap(app_name)

        return files

    def _generate_deployment(self, app_name: str) -> str:
        """Generate Kubernetes Deployment"""
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': app_name,
                'labels': {'app': app_name}
            },
            'spec': {
                'replicas': 3,
                'selector': {
                    'matchLabels': {'app': app_name}
                },
                'template': {
                    'metadata': {
                        'labels': {'app': app_name}
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': app_name,
                                'image': f'{app_name}:latest',
                                'ports': [{'containerPort': 8080}],
                                'env': [
                                    {
                                        'name': 'CONFIG',
                                        'valueFrom': {
                                            'configMapKeyRef': {
                                                'name': f'{app_name}-config',
                                                'key': 'config.json'
                                            }
                                        }
                                    }
                                ],
                                'resources': {
                                    'requests': {'cpu': '100m', 'memory': '128Mi'},
                                    'limits': {'cpu': '500m', 'memory': '512Mi'}
                                },
                                'livenessProbe': {
                                    'httpGet': {'path': '/health', 'port': 8080},
                                    'initialDelaySeconds': 30,
                                    'periodSeconds': 10
                                },
                                'readinessProbe': {
                                    'httpGet': {'path': '/ready', 'port': 8080},
                                    'initialDelaySeconds': 5,
                                    'periodSeconds': 5
                                }
                            }
                        ]
                    }
                }
            }
        }

        return yaml.dump(deployment, default_flow_style=False)

    def _generate_service(self, app_name: str) -> str:
        """Generate Kubernetes Service"""
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': app_name,
                'labels': {'app': app_name}
            },
            'spec': {
                'type': 'ClusterIP',
                'ports': [
                    {
                        'port': 80,
                        'targetPort': 8080,
                        'protocol': 'TCP',
                        'name': 'http'
                    }
                ],
                'selector': {'app': app_name}
            }
        }

        return yaml.dump(service, default_flow_style=False)

    def _generate_ingress(self, app_name: str) -> str:
        """Generate Kubernetes Ingress"""
        ingress = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': app_name,
                'annotations': {
                    'kubernetes.io/ingress.class': 'nginx',
                    'cert-manager.io/cluster-issuer': 'letsencrypt-prod'
                }
            },
            'spec': {
                'tls': [
                    {
                        'hosts': [f'{app_name}.example.com'],
                        'secretName': f'{app_name}-tls'
                    }
                ],
                'rules': [
                    {
                        'host': f'{app_name}.example.com',
                        'http': {
                            'paths': [
                                {
                                    'path': '/',
                                    'pathType': 'Prefix',
                                    'backend': {
                                        'service': {
                                            'name': app_name,
                                            'port': {'number': 80}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        return yaml.dump(ingress, default_flow_style=False)

    def _generate_configmap(self, app_name: str) -> str:
        """Generate Kubernetes ConfigMap"""
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': f'{app_name}-config'
            },
            'data': {
                'config.json': json.dumps({
                    'app_name': app_name,
                    'environment': 'production',
                    'log_level': 'info'
                }, indent=2)
            }
        }

        return yaml.dump(configmap, default_flow_style=False)
