#!/usr/bin/env python3
"""
Observability Stack Generator

Автоматическая генерация observability stack с Prometheus, Grafana, Loki, и Jaeger.
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ObservabilityTool(Enum):
    """Observability Tool"""
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    LOKI = "loki"
    JAEGER = "jaeger"
    TEMPO = "tempo"
    ALERTMANAGER = "alertmanager"


class MetricType(Enum):
    """Metric Type"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class PrometheusTarget:
    """Prometheus Scrape Target"""
    job_name: str
    targets: List[str] = field(default_factory=list)
    scrape_interval: str = "15s"
    metrics_path: str = "/metrics"
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Prometheus Alert Rule"""
    name: str
    expr: str
    duration: str = "5m"
    severity: str = "warning"
    summary: str = ""
    description: str = ""
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class GrafanaDashboard:
    """Grafana Dashboard Configuration"""
    title: str
    uid: str
    panels: List[Dict[str, Any]] = field(default_factory=list)
    refresh: str = "10s"


@dataclass
class ObservabilityConfig:
    """Observability Stack Configuration"""
    tools: List[ObservabilityTool] = field(default_factory=list)
    prometheus_targets: List[PrometheusTarget] = field(default_factory=list)
    alert_rules: List[AlertRule] = field(default_factory=list)
    dashboards: List[GrafanaDashboard] = field(default_factory=list)


class ObservabilityGenerator:
    """Observability Stack Generator"""

    def __init__(self, config: ObservabilityConfig):
        """
        Initialize observability generator

        Args:
            config: Observability configuration
        """
        self.config = config

    def generate(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate observability stack

        Args:
            output_dir: Output directory

        Returns:
            Generated files
        """
        print("📊 Generating observability stack...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate docker-compose
        files['docker-compose.yml'] = self._generate_docker_compose()

        # Generate Prometheus config
        if ObservabilityTool.PROMETHEUS in self.config.tools:
            files['prometheus/prometheus.yml'] = self._generate_prometheus_config()
            files['prometheus/alerts.yml'] = self._generate_alert_rules()

        # Generate Grafana provisioning
        if ObservabilityTool.GRAFANA in self.config.tools:
            files['grafana/provisioning/datasources/prometheus.yml'] = self._generate_grafana_datasource()
            files['grafana/provisioning/dashboards/dashboard.yml'] = self._generate_grafana_provisioning()

            for dashboard in self.config.dashboards:
                files[f'grafana/dashboards/{dashboard.uid}.json'] = self._generate_dashboard_json(dashboard)

        # Generate Loki config
        if ObservabilityTool.LOKI in self.config.tools:
            files['loki/loki-config.yml'] = self._generate_loki_config()

        # Generate Jaeger config
        if ObservabilityTool.JAEGER in self.config.tools:
            files['jaeger/jaeger-config.yml'] = self._generate_jaeger_config()

        # Generate Kubernetes manifests
        files['k8s/prometheus.yaml'] = self._generate_prometheus_k8s()
        files['k8s/grafana.yaml'] = self._generate_grafana_k8s()

        # Generate README
        files['README.md'] = self._generate_readme()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} observability files")
        return files

    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml"""
        services = {}

        if ObservabilityTool.PROMETHEUS in self.config.tools:
            services['prometheus'] = {
                'image': 'prom/prometheus:latest',
                'container_name': 'prometheus',
                'ports': ['9090:9090'],
                'volumes': [
                    './prometheus:/etc/prometheus',
                    'prometheus-data:/prometheus'
                ],
                'command': [
                    '--config.file=/etc/prometheus/prometheus.yml',
                    '--storage.tsdb.path=/prometheus'
                ],
                'restart': 'unless-stopped'
            }

        if ObservabilityTool.GRAFANA in self.config.tools:
            services['grafana'] = {
                'image': 'grafana/grafana:latest',
                'container_name': 'grafana',
                'ports': ['3000:3000'],
                'volumes': [
                    'grafana-data:/var/lib/grafana',
                    './grafana/provisioning:/etc/grafana/provisioning',
                    './grafana/dashboards:/var/lib/grafana/dashboards'
                ],
                'environment': {
                    'GF_SECURITY_ADMIN_USER': 'admin',
                    'GF_SECURITY_ADMIN_PASSWORD': 'admin',
                    'GF_USERS_ALLOW_SIGN_UP': 'false'
                },
                'restart': 'unless-stopped'
            }

        if ObservabilityTool.LOKI in self.config.tools:
            services['loki'] = {
                'image': 'grafana/loki:latest',
                'container_name': 'loki',
                'ports': ['3100:3100'],
                'volumes': ['./loki:/etc/loki'],
                'command': '-config.file=/etc/loki/loki-config.yml',
                'restart': 'unless-stopped'
            }

            services['promtail'] = {
                'image': 'grafana/promtail:latest',
                'container_name': 'promtail',
                'volumes': [
                    '/var/log:/var/log',
                    './promtail:/etc/promtail'
                ],
                'command': '-config.file=/etc/promtail/promtail-config.yml',
                'restart': 'unless-stopped'
            }

        if ObservabilityTool.JAEGER in self.config.tools:
            services['jaeger'] = {
                'image': 'jaegertracing/all-in-one:latest',
                'container_name': 'jaeger',
                'ports': [
                    '5775:5775/udp',
                    '6831:6831/udp',
                    '6832:6832/udp',
                    '5778:5778',
                    '16686:16686',
                    '14268:14268',
                    '14250:14250',
                    '9411:9411'
                ],
                'environment': {
                    'COLLECTOR_ZIPKIN_HOST_PORT': ':9411'
                },
                'restart': 'unless-stopped'
            }

        if ObservabilityTool.ALERTMANAGER in self.config.tools:
            services['alertmanager'] = {
                'image': 'prom/alertmanager:latest',
                'container_name': 'alertmanager',
                'ports': ['9093:9093'],
                'volumes': ['./alertmanager:/etc/alertmanager'],
                'command': '--config.file=/etc/alertmanager/alertmanager.yml',
                'restart': 'unless-stopped'
            }

        compose = {
            'version': '3.8',
            'services': services,
            'volumes': {
                'prometheus-data': {},
                'grafana-data': {}
            }
        }

        return yaml.dump(compose, default_flow_style=False, sort_keys=False)

    def _generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""
        scrape_configs = []

        for target in self.config.prometheus_targets:
            scrape_config = {
                'job_name': target.job_name,
                'scrape_interval': target.scrape_interval,
                'metrics_path': target.metrics_path,
                'static_configs': [
                    {
                        'targets': target.targets,
                        'labels': target.labels
                    }
                ]
            }
            scrape_configs.append(scrape_config)

        # Add self-monitoring
        scrape_configs.append({
            'job_name': 'prometheus',
            'static_configs': [
                {'targets': ['localhost:9090']}
            ]
        })

        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {'targets': ['alertmanager:9093']}
                        ]
                    }
                ]
            },
            'rule_files': ['alerts.yml'],
            'scrape_configs': scrape_configs
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_alert_rules(self) -> str:
        """Generate Prometheus alert rules"""
        groups = []

        if self.config.alert_rules:
            rules = []

            for alert in self.config.alert_rules:
                rule = {
                    'alert': alert.name,
                    'expr': alert.expr,
                    'for': alert.duration,
                    'labels': {
                        'severity': alert.severity
                    },
                    'annotations': {
                        'summary': alert.summary or f'Alert: {alert.name}',
                        'description': alert.description or alert.expr,
                        **alert.annotations
                    }
                }
                rules.append(rule)

            groups.append({
                'name': 'application_alerts',
                'rules': rules
            })
        else:
            # Default alerts
            groups.append({
                'name': 'default_alerts',
                'rules': [
                    {
                        'alert': 'InstanceDown',
                        'expr': 'up == 0',
                        'for': '5m',
                        'labels': {'severity': 'critical'},
                        'annotations': {
                            'summary': 'Instance {{ $labels.instance }} down',
                            'description': 'Instance has been down for more than 5 minutes'
                        }
                    },
                    {
                        'alert': 'HighMemoryUsage',
                        'expr': 'node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.1',
                        'for': '5m',
                        'labels': {'severity': 'warning'},
                        'annotations': {
                            'summary': 'High memory usage on {{ $labels.instance }}',
                            'description': 'Memory usage is above 90%'
                        }
                    },
                    {
                        'alert': 'HighCPUUsage',
                        'expr': '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80',
                        'for': '10m',
                        'labels': {'severity': 'warning'},
                        'annotations': {
                            'summary': 'High CPU usage on {{ $labels.instance }}',
                            'description': 'CPU usage is above 80%'
                        }
                    }
                ]
            })

        return yaml.dump({'groups': groups}, default_flow_style=False)

    def _generate_grafana_datasource(self) -> str:
        """Generate Grafana datasource configuration"""
        datasources = [
            {
                'name': 'Prometheus',
                'type': 'prometheus',
                'access': 'proxy',
                'url': 'http://prometheus:9090',
                'isDefault': True,
                'editable': True
            }
        ]

        if ObservabilityTool.LOKI in self.config.tools:
            datasources.append({
                'name': 'Loki',
                'type': 'loki',
                'access': 'proxy',
                'url': 'http://loki:3100',
                'editable': True
            })

        if ObservabilityTool.JAEGER in self.config.tools:
            datasources.append({
                'name': 'Jaeger',
                'type': 'jaeger',
                'access': 'proxy',
                'url': 'http://jaeger:16686',
                'editable': True
            })

        config = {
            'apiVersion': 1,
            'datasources': datasources
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_grafana_provisioning(self) -> str:
        """Generate Grafana dashboard provisioning"""
        config = {
            'apiVersion': 1,
            'providers': [
                {
                    'name': 'dashboards',
                    'type': 'file',
                    'options': {
                        'path': '/var/lib/grafana/dashboards'
                    }
                }
            ]
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_dashboard_json(self, dashboard: GrafanaDashboard) -> str:
        """Generate Grafana dashboard JSON"""
        panels = dashboard.panels if dashboard.panels else [
            {
                'id': 1,
                'title': 'CPU Usage',
                'type': 'graph',
                'targets': [
                    {
                        'expr': '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                        'legendFormat': '{{ instance }}'
                    }
                ],
                'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 0}
            },
            {
                'id': 2,
                'title': 'Memory Usage',
                'type': 'graph',
                'targets': [
                    {
                        'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100',
                        'legendFormat': '{{ instance }}'
                    }
                ],
                'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 0}
            }
        ]

        dashboard_json = {
            'uid': dashboard.uid,
            'title': dashboard.title,
            'tags': ['generated'],
            'timezone': 'browser',
            'refresh': dashboard.refresh,
            'schemaVersion': 16,
            'version': 0,
            'panels': panels
        }

        return json.dumps(dashboard_json, indent=2)

    def _generate_loki_config(self) -> str:
        """Generate Loki configuration"""
        config = {
            'auth_enabled': False,
            'server': {
                'http_listen_port': 3100
            },
            'ingester': {
                'lifecycler': {
                    'address': '127.0.0.1',
                    'ring': {
                        'kvstore': {
                            'store': 'inmemory'
                        },
                        'replication_factor': 1
                    }
                },
                'chunk_idle_period': '5m',
                'chunk_retain_period': '30s'
            },
            'schema_config': {
                'configs': [
                    {
                        'from': '2020-10-24',
                        'store': 'boltdb',
                        'object_store': 'filesystem',
                        'schema': 'v11',
                        'index': {
                            'prefix': 'index_',
                            'period': '168h'
                        }
                    }
                ]
            },
            'storage_config': {
                'boltdb': {
                    'directory': '/tmp/loki/index'
                },
                'filesystem': {
                    'directory': '/tmp/loki/chunks'
                }
            }
        }

        return yaml.dump(config, default_flow_style=False)

    def _generate_jaeger_config(self) -> str:
        """Generate Jaeger configuration"""
        return """# Jaeger runs with default configuration
# Access UI at http://localhost:16686
"""

    def _generate_prometheus_k8s(self) -> str:
        """Generate Prometheus Kubernetes manifests"""
        manifests = [
            {
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {
                    'name': 'prometheus-config',
                    'namespace': 'monitoring'
                },
                'data': {
                    'prometheus.yml': self._generate_prometheus_config()
                }
            },
            {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'prometheus',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'replicas': 1,
                    'selector': {
                        'matchLabels': {'app': 'prometheus'}
                    },
                    'template': {
                        'metadata': {
                            'labels': {'app': 'prometheus'}
                        },
                        'spec': {
                            'containers': [
                                {
                                    'name': 'prometheus',
                                    'image': 'prom/prometheus:latest',
                                    'ports': [{'containerPort': 9090}],
                                    'volumeMounts': [
                                        {
                                            'name': 'config',
                                            'mountPath': '/etc/prometheus'
                                        }
                                    ]
                                }
                            ],
                            'volumes': [
                                {
                                    'name': 'config',
                                    'configMap': {
                                        'name': 'prometheus-config'
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': 'prometheus',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'selector': {'app': 'prometheus'},
                    'ports': [
                        {
                            'port': 9090,
                            'targetPort': 9090
                        }
                    ]
                }
            }
        ]

        return '---\n'.join([yaml.dump(m, default_flow_style=False) for m in manifests])

    def _generate_grafana_k8s(self) -> str:
        """Generate Grafana Kubernetes manifests"""
        manifests = [
            {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'grafana',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'replicas': 1,
                    'selector': {
                        'matchLabels': {'app': 'grafana'}
                    },
                    'template': {
                        'metadata': {
                            'labels': {'app': 'grafana'}
                        },
                        'spec': {
                            'containers': [
                                {
                                    'name': 'grafana',
                                    'image': 'grafana/grafana:latest',
                                    'ports': [{'containerPort': 3000}],
                                    'env': [
                                        {
                                            'name': 'GF_SECURITY_ADMIN_PASSWORD',
                                            'value': 'admin'
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
            {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': 'grafana',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'selector': {'app': 'grafana'},
                    'ports': [
                        {
                            'port': 3000,
                            'targetPort': 3000
                        }
                    ],
                    'type': 'LoadBalancer'
                }
            }
        ]

        return '---\n'.join([yaml.dump(m, default_flow_style=False) for m in manifests])

    def _generate_readme(self) -> str:
        """Generate README"""
        tools_list = ', '.join([t.value for t in self.config.tools])

        return f"""# Observability Stack

Complete observability solution with {tools_list}.

## Components

{chr(10).join([f"- **{t.value.title()}**" for t in self.config.tools])}

## Quick Start

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Jaeger: http://localhost:16686
- Loki: http://localhost:3100

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace monitoring

# Deploy Prometheus
kubectl apply -f k8s/prometheus.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana.yaml

# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

## Prometheus Targets

{chr(10).join([f"- **{t.job_name}**: {', '.join(t.targets)}" for t in self.config.prometheus_targets])}

## Alert Rules

{len(self.config.alert_rules)} alert rules configured

## Dashboards

{len(self.config.dashboards)} Grafana dashboards provisioned
"""

    def add_prometheus_target(self, target: PrometheusTarget):
        """Add Prometheus scrape target"""
        self.config.prometheus_targets.append(target)
        print(f"✅ Added Prometheus target: {target.job_name}")

    def add_alert_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.config.alert_rules.append(rule)
        print(f"✅ Added alert rule: {rule.name}")

    def add_dashboard(self, dashboard: GrafanaDashboard):
        """Add Grafana dashboard"""
        self.config.dashboards.append(dashboard)
        print(f"✅ Added dashboard: {dashboard.title}")
