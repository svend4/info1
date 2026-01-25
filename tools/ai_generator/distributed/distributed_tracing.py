#!/usr/bin/env python3
"""
Distributed Tracing Generator (OpenTelemetry)

Генерация OpenTelemetry instrumentation для distributed tracing, metrics, и logs.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class TracingBackend(Enum):
    """Tracing Backend Types"""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    TEMPO = "tempo"
    DATADOG = "datadog"
    NEW_RELIC = "newrelic"


class SamplingStrategy(Enum):
    """Trace Sampling Strategy"""
    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    TRACE_ID_RATIO = "trace_id_ratio"
    PARENT_BASED = "parent_based"


@dataclass
class TracingConfig:
    """OpenTelemetry Tracing Configuration"""
    service_name: str
    backend: TracingBackend
    endpoint: str
    sampling_rate: float = 1.0
    sampling_strategy: SamplingStrategy = SamplingStrategy.PARENT_BASED
    export_interval_ms: int = 5000


@dataclass
class MetricsConfig:
    """OpenTelemetry Metrics Configuration"""
    service_name: str
    export_endpoint: str
    export_interval_ms: int = 60000
    enable_runtime_metrics: bool = True
    enable_custom_metrics: bool = True


class DistributedTracingGenerator:
    """OpenTelemetry Distributed Tracing Generator"""

    def __init__(self):
        """Инициализация distributed tracing generator"""
        self.configs: Dict[str, TracingConfig] = {}

    def generate_python_instrumentation(self,
                                       config: TracingConfig,
                                       framework: str = "fastapi") -> Dict[str, str]:
        """
        Generate Python OpenTelemetry instrumentation

        Args:
            config: Tracing configuration
            framework: Framework (fastapi, flask, django)

        Returns:
            Generated code files
        """
        print(f"🔍 Generating Python OpenTelemetry for {framework}...")

        files = {}

        # Main tracing setup
        tracing_py = self._generate_python_tracing_setup(config, framework)
        files['tracing.py'] = tracing_py

        # Instrumented application
        if framework == "fastapi":
            app_py = self._generate_fastapi_instrumented(config)
            files['main.py'] = app_py
        elif framework == "flask":
            app_py = self._generate_flask_instrumented(config)
            files['app.py'] = app_py

        # Requirements
        requirements = self._get_python_requirements(config, framework)
        files['requirements.txt'] = '\n'.join(requirements)

        # Configuration file
        config_yaml = self._generate_otel_config(config)
        files['otel-config.yaml'] = config_yaml

        print(f"✅ Generated {len(files)} Python files")
        return files

    def generate_go_instrumentation(self,
                                   config: TracingConfig) -> Dict[str, str]:
        """
        Generate Go OpenTelemetry instrumentation

        Args:
            config: Tracing configuration

        Returns:
            Generated code files
        """
        print(f"🔍 Generating Go OpenTelemetry instrumentation...")

        files = {}

        # Tracing setup
        tracing_go = self._generate_go_tracing_setup(config)
        files['tracing.go'] = tracing_go

        # Main application
        main_go = self._generate_go_instrumented_app(config)
        files['main.go'] = main_go

        # go.mod
        go_mod = self._generate_go_mod(config)
        files['go.mod'] = go_mod

        print(f"✅ Generated {len(files)} Go files")
        return files

    def generate_docker_compose_observability(self,
                                             services: List[str],
                                             output_path: Path):
        """
        Generate docker-compose with observability stack

        Args:
            services: List of service names
            output_path: Output file path
        """
        print("🐳 Generating observability stack (Jaeger + Prometheus + Grafana)...")

        compose = {
            'version': '3.8',
            'services': {
                # Jaeger (tracing)
                'jaeger': {
                    'image': 'jaegertracing/all-in-one:latest',
                    'ports': [
                        '16686:16686',  # UI
                        '14268:14268',  # HTTP collector
                        '4317:4317',    # OTLP gRPC
                        '4318:4318'     # OTLP HTTP
                    ],
                    'environment': {
                        'COLLECTOR_OTLP_ENABLED': 'true'
                    }
                },

                # Prometheus (metrics)
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './prometheus.yml:/etc/prometheus/prometheus.yml'
                    ],
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus'
                    ]
                },

                # Grafana (visualization)
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'ports': ['3000:3000'],
                    'environment': {
                        'GF_AUTH_ANONYMOUS_ENABLED': 'true',
                        'GF_AUTH_ANONYMOUS_ORG_ROLE': 'Admin'
                    },
                    'volumes': [
                        './grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml'
                    ]
                },

                # OTLP Collector
                'otel-collector': {
                    'image': 'otel/opentelemetry-collector-contrib:latest',
                    'ports': [
                        '4317:4317',  # OTLP gRPC
                        '4318:4318',  # OTLP HTTP
                        '8888:8888',  # Prometheus metrics
                        '8889:8889'   # Prometheus exporter
                    ],
                    'volumes': [
                        './otel-collector-config.yaml:/etc/otel-collector-config.yaml'
                    ],
                    'command': [
                        '--config=/etc/otel-collector-config.yaml'
                    ]
                }
            },
            'networks': {
                'observability': {
                    'driver': 'bridge'
                }
            }
        }

        # Add instrumented services
        for service in services:
            compose['services'][service] = {
                'build': f'./{service}',
                'environment': {
                    'OTEL_EXPORTER_OTLP_ENDPOINT': 'http://otel-collector:4317',
                    'OTEL_SERVICE_NAME': service
                },
                'networks': ['observability']
            }

        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False)

        # Generate accompanying config files
        self._generate_prometheus_config(services, output_path.parent)
        self._generate_otel_collector_config(output_path.parent)
        self._generate_grafana_datasources(output_path.parent)

        print(f"✅ Generated observability stack at {output_path}")

    def _generate_python_tracing_setup(self, config: TracingConfig, framework: str) -> str:
        """Generate Python tracing setup code"""
        code = f'''from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.{framework} import {framework.capitalize()}Instrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_tracing():
    """
    Setup OpenTelemetry tracing for {config.service_name}
    """
    # Create resource
    resource = Resource(attributes={{
        "service.name": "{config.service_name}",
        "service.version": "1.0.0",
        "deployment.environment": "production"
    }})

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Create OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint="{config.endpoint}",
        insecure=True
    )

    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument frameworks
    {framework.capitalize()}Instrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    RequestsInstrumentor().instrument()

    logger.info("OpenTelemetry tracing initialized for {config.service_name}")

    return trace.get_tracer(__name__)

# Initialize tracer
tracer = setup_tracing()
'''

        return code

    def _generate_fastapi_instrumented(self, config: TracingConfig) -> str:
        """Generate instrumented FastAPI application"""
        return f'''from fastapi import FastAPI, Request
from opentelemetry import trace
from tracing import tracer
import logging

app = FastAPI(title="{config.service_name}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    """Add trace context to logs"""
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

    logger.info(
        f"Request: {{request.method}} {{request.url.path}}",
        extra={{"trace_id": trace_id, "span_id": span_id}}
    )

    response = await call_next(request)
    return response

@app.get("/")
async def root():
    with tracer.start_as_current_span("root-handler"):
        return {{"message": "Hello from {config.service_name}"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}
'''

    def _generate_flask_instrumented(self, config: TracingConfig) -> str:
        """Generate instrumented Flask application"""
        return f'''from flask import Flask
from opentelemetry import trace
from tracing import tracer

app = Flask(__name__)

@app.route('/')
def root():
    with tracer.start_as_current_span("root-handler"):
        return {{"message": "Hello from {config.service_name}"}}

@app.route('/health')
def health():
    return {{"status": "healthy"}}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
'''

    def _generate_go_tracing_setup(self, config: TracingConfig) -> str:
        """Generate Go tracing setup code"""
        return f'''package main

import (
    "context"
    "log"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
)

func setupTracing(ctx context.Context) (*sdktrace.TracerProvider, error) {{
    // Create resource
    res, err := resource.New(ctx,
        resource.WithAttributes(
            semconv.ServiceName("{config.service_name}"),
            semconv.ServiceVersion("1.0.0"),
        ),
    )
    if err != nil {{
        return nil, err
    }}

    // Create OTLP exporter
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint("{config.endpoint}"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {{
        return nil, err
    }}

    // Create tracer provider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )

    // Set global tracer provider
    otel.SetTracerProvider(tp)

    log.Println("OpenTelemetry tracing initialized")
    return tp, nil
}}
'''

    def _generate_go_instrumented_app(self, config: TracingConfig) -> str:
        """Generate instrumented Go application"""
        return f'''package main

import (
    "context"
    "log"
    "net/http"

    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/otel"
)

func main() {{
    ctx := context.Background()

    // Setup tracing
    tp, err := setupTracing(ctx)
    if err != nil {{
        log.Fatal(err)
    }}
    defer func() {{
        if err := tp.Shutdown(ctx); err != nil {{
            log.Fatal(err)
        }}
    }}()

    // Create instrumented HTTP handler
    handler := otelhttp.NewHandler(
        http.HandlerFunc(rootHandler),
        "{config.service_name}",
    )

    http.Handle("/", handler)
    http.HandleFunc("/health", healthHandler)

    log.Println("Server starting on :8000")
    log.Fatal(http.ListenAndServe(":8000", nil))
}}

func rootHandler(w http.ResponseWriter, r *http.Request) {{
    ctx := r.Context()
    tracer := otel.Tracer("{config.service_name}")

    _, span := tracer.Start(ctx, "root-handler")
    defer span.End()

    w.Write([]byte("Hello from {config.service_name}"))
}}

func healthHandler(w http.ResponseWriter, r *http.Request) {{
    w.Write([]byte("healthy"))
}}
'''

    def _generate_go_mod(self, config: TracingConfig) -> str:
        """Generate go.mod"""
        return f'''module {config.service_name}

go 1.21

require (
    go.opentelemetry.io/otel v1.21.0
    go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.21.0
    go.opentelemetry.io/otel/sdk v1.21.0
    go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.46.0
)
'''

    def _get_python_requirements(self, config: TracingConfig, framework: str) -> List[str]:
        """Get Python requirements"""
        requirements = [
            'opentelemetry-api>=1.21.0',
            'opentelemetry-sdk>=1.21.0',
            'opentelemetry-exporter-otlp>=1.21.0',
            f'opentelemetry-instrumentation-{framework}>=0.42b0',
            'opentelemetry-instrumentation-httpx>=0.42b0',
            'opentelemetry-instrumentation-requests>=0.42b0'
        ]

        if framework == "fastapi":
            requirements.extend([
                'fastapi>=0.100.0',
                'uvicorn[standard]>=0.23.0',
                'httpx>=0.24.0'
            ])
        elif framework == "flask":
            requirements.extend([
                'flask>=2.3.0',
                'requests>=2.31.0'
            ])

        return requirements

    def _generate_otel_config(self, config: TracingConfig) -> str:
        """Generate OpenTelemetry config YAML"""
        import yaml

        config_dict = {
            'service': {
                'name': config.service_name
            },
            'exporters': {
                'otlp': {
                    'endpoint': config.endpoint,
                    'insecure': True
                }
            },
            'processors': {
                'batch': {
                    'timeout': f'{config.export_interval_ms}ms'
                }
            },
            'extensions': {
                'health_check': {},
                'pprof': {},
                'zpages': {}
            }
        }

        return yaml.dump(config_dict, default_flow_style=False)

    def _generate_prometheus_config(self, services: List[str], output_dir: Path):
        """Generate Prometheus configuration"""
        import yaml

        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'otel-collector',
                    'static_configs': [{
                        'targets': ['otel-collector:8888']
                    }]
                }
            ]
        }

        # Add scrape configs for each service
        for service in services:
            prometheus_config['scrape_configs'].append({
                'job_name': service,
                'static_configs': [{
                    'targets': [f'{service}:8000']
                }]
            })

        with open(output_dir / 'prometheus.yml', 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

    def _generate_otel_collector_config(self, output_dir: Path):
        """Generate OpenTelemetry Collector configuration"""
        import yaml

        config = {
            'receivers': {
                'otlp': {
                    'protocols': {
                        'grpc': {'endpoint': '0.0.0.0:4317'},
                        'http': {'endpoint': '0.0.0.0:4318'}
                    }
                }
            },
            'processors': {
                'batch': {},
                'memory_limiter': {
                    'limit_mib': 512,
                    'spike_limit_mib': 128,
                    'check_interval': '5s'
                }
            },
            'exporters': {
                'jaeger': {
                    'endpoint': 'jaeger:14250',
                    'tls': {'insecure': True}
                },
                'prometheus': {
                    'endpoint': '0.0.0.0:8889'
                },
                'logging': {
                    'loglevel': 'info'
                }
            },
            'service': {
                'pipelines': {
                    'traces': {
                        'receivers': ['otlp'],
                        'processors': ['memory_limiter', 'batch'],
                        'exporters': ['jaeger', 'logging']
                    },
                    'metrics': {
                        'receivers': ['otlp'],
                        'processors': ['memory_limiter', 'batch'],
                        'exporters': ['prometheus', 'logging']
                    }
                }
            }
        }

        with open(output_dir / 'otel-collector-config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

    def _generate_grafana_datasources(self, output_dir: Path):
        """Generate Grafana datasources configuration"""
        import yaml

        datasources = {
            'apiVersion': 1,
            'datasources': [
                {
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'access': 'proxy',
                    'url': 'http://prometheus:9090',
                    'isDefault': True
                },
                {
                    'name': 'Jaeger',
                    'type': 'jaeger',
                    'access': 'proxy',
                    'url': 'http://jaeger:16686'
                }
            ]
        }

        with open(output_dir / 'grafana-datasources.yml', 'w') as f:
            yaml.dump(datasources, f, default_flow_style=False)
