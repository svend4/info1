#!/usr/bin/env python3
"""
Microservices Architecture Generator

Генерация microservices architecture с service communication, API gateway, и service discovery.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class CommunicationType(Enum):
    """Service Communication Types"""
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    MESSAGE_QUEUE = "message_queue"
    EVENT_DRIVEN = "event_driven"


class ServiceType(Enum):
    """Microservice Types"""
    API_GATEWAY = "api_gateway"
    BUSINESS_SERVICE = "business_service"
    DATA_SERVICE = "data_service"
    INTEGRATION_SERVICE = "integration_service"
    UTILITY_SERVICE = "utility_service"


class DatabaseType(Enum):
    """Database Types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    ELASTICSEARCH = "elasticsearch"


@dataclass
class ServiceEndpoint:
    """Service API Endpoint"""
    path: str
    method: str
    description: str
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None


@dataclass
class ServiceDependency:
    """Service Dependency"""
    service_name: str
    communication_type: CommunicationType
    endpoints: List[str] = field(default_factory=list)


@dataclass
class MicroserviceSpec:
    """Microservice Specification"""
    name: str
    service_type: ServiceType
    description: str
    port: int
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[ServiceDependency] = field(default_factory=list)
    database: Optional[DatabaseType] = None
    environment_vars: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, str] = field(default_factory=dict)


@dataclass
class MicroservicesArchitecture:
    """Complete Microservices Architecture"""
    name: str
    services: List[MicroserviceSpec]
    api_gateway: Optional[MicroserviceSpec] = None
    message_broker: Optional[str] = None  # "rabbitmq", "kafka"
    service_mesh: bool = False
    observability: bool = True


class MicroservicesGenerator:
    """Microservices Architecture Generator"""

    def __init__(self):
        """Инициализация microservices generator"""
        self.architectures: Dict[str, MicroservicesArchitecture] = {}

    def create_architecture(self,
                           name: str,
                           services: List[MicroserviceSpec],
                           use_api_gateway: bool = True,
                           use_service_mesh: bool = False) -> MicroservicesArchitecture:
        """
        Create microservices architecture

        Args:
            name: Architecture name
            services: List of microservices
            use_api_gateway: Include API gateway
            use_service_mesh: Use service mesh (Istio)

        Returns:
            Microservices architecture
        """
        print(f"🏗️  Creating microservices architecture: {name}")

        # Create API Gateway if needed
        api_gateway = None
        if use_api_gateway:
            api_gateway = self._generate_api_gateway(services)

        architecture = MicroservicesArchitecture(
            name=name,
            services=services,
            api_gateway=api_gateway,
            service_mesh=use_service_mesh,
            observability=True
        )

        self.architectures[name] = architecture

        print(f"✅ Created architecture with {len(services)} services")
        return architecture

    def generate_service_code(self,
                             service: MicroserviceSpec,
                             output_dir: Path,
                             framework: str = "fastapi") -> Dict[str, str]:
        """
        Generate code for microservice

        Args:
            service: Microservice specification
            output_dir: Output directory
            framework: Framework to use (fastapi, express, spring-boot)

        Returns:
            Generated files
        """
        print(f"📦 Generating service: {service.name}")

        output_dir.mkdir(parents=True, exist_ok=True)

        if framework == "fastapi":
            files = self._generate_fastapi_service(service, output_dir)
        elif framework == "express":
            files = self._generate_express_service(service, output_dir)
        elif framework == "spring-boot":
            files = self._generate_spring_service(service, output_dir)
        else:
            files = self._generate_fastapi_service(service, output_dir)

        # Generate Docker files
        files.update(self._generate_docker_files(service, output_dir, framework))

        # Generate Kubernetes manifests
        files.update(self._generate_k8s_manifests(service, output_dir))

        print(f"✅ Generated {len(files)} files for {service.name}")
        return files

    def generate_docker_compose(self,
                               architecture: MicroservicesArchitecture,
                               output_path: Path):
        """
        Generate docker-compose.yml for architecture

        Args:
            architecture: Microservices architecture
            output_path: Output file path
        """
        compose = {
            'version': '3.8',
            'services': {},
            'networks': {
                'microservices-network': {
                    'driver': 'bridge'
                }
            }
        }

        # Add each service
        for service in architecture.services:
            compose['services'][service.name] = {
                'build': f'./{service.name}',
                'ports': [f'{service.port}:{service.port}'],
                'environment': service.environment_vars,
                'networks': ['microservices-network'],
                'depends_on': [dep.service_name for dep in service.dependencies]
            }

            # Add database if needed
            if service.database:
                db_name = f"{service.name}-db"
                compose['services'][db_name] = self._generate_db_service(
                    service.database,
                    db_name
                )

        # Add API Gateway
        if architecture.api_gateway:
            compose['services']['api-gateway'] = {
                'build': './api-gateway',
                'ports': [f'{architecture.api_gateway.port}:8000'],
                'environment': {
                    'SERVICES': ','.join([s.name for s in architecture.services])
                },
                'networks': ['microservices-network']
            }

        # Add monitoring
        if architecture.observability:
            compose['services']['prometheus'] = {
                'image': 'prom/prometheus:latest',
                'ports': ['9090:9090'],
                'volumes': ['./prometheus.yml:/etc/prometheus/prometheus.yml'],
                'networks': ['microservices-network']
            }

            compose['services']['grafana'] = {
                'image': 'grafana/grafana:latest',
                'ports': ['3000:3000'],
                'networks': ['microservices-network']
            }

        with open(output_path, 'w') as f:
            import yaml
            yaml.dump(compose, f, default_flow_style=False)

        print(f"✅ Generated docker-compose.yml")

    def _generate_api_gateway(self, services: List[MicroserviceSpec]) -> MicroserviceSpec:
        """Generate API Gateway configuration"""
        gateway = MicroserviceSpec(
            name="api-gateway",
            service_type=ServiceType.API_GATEWAY,
            description="API Gateway for microservices",
            port=8000,
            endpoints=[],
            dependencies=[
                ServiceDependency(
                    service_name=s.name,
                    communication_type=CommunicationType.REST
                ) for s in services
            ]
        )

        # Aggregate all endpoints
        for service in services:
            for endpoint in service.endpoints:
                gateway_endpoint = ServiceEndpoint(
                    path=f"/{service.name}{endpoint.path}",
                    method=endpoint.method,
                    description=f"Proxy to {service.name}"
                )
                gateway.endpoints.append(gateway_endpoint)

        return gateway

    def _generate_fastapi_service(self,
                                  service: MicroserviceSpec,
                                  output_dir: Path) -> Dict[str, str]:
        """Generate FastAPI microservice"""
        files = {}

        # Main application
        main_py = f'''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging

app = FastAPI(
    title="{service.name}",
    description="{service.description}",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "service": "{service.name}"}}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check dependencies
    return {{"status": "ready"}}

'''

        # Generate endpoints
        for endpoint in service.endpoints:
            main_py += f'''
@app.{endpoint.method.lower()}("{endpoint.path}")
async def {self._to_func_name(endpoint.path)}():
    """
    {endpoint.description}
    """
    logger.info("Processing request: {endpoint.path}")
    # TODO: Implement logic
    return {{"message": "Success"}}

'''

        files['main.py'] = main_py

        # Requirements
        requirements = [
            'fastapi>=0.100.0',
            'uvicorn[standard]>=0.23.0',
            'pydantic>=2.0.0',
            'prometheus-fastapi-instrumentator>=6.0.0',
            'httpx>=0.24.0',
            'python-json-logger>=2.0.0'
        ]

        if service.database == DatabaseType.POSTGRESQL:
            requirements.extend(['sqlalchemy>=2.0.0', 'psycopg2-binary>=2.9.0'])
        elif service.database == DatabaseType.MONGODB:
            requirements.append('motor>=3.0.0')
        elif service.database == DatabaseType.REDIS:
            requirements.append('redis>=4.5.0')

        files['requirements.txt'] = '\n'.join(requirements)

        # Write files
        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        return files

    def _generate_express_service(self,
                                  service: MicroserviceSpec,
                                  output_dir: Path) -> Dict[str, str]:
        """Generate Express.js microservice"""
        files = {}

        # Main application
        app_ts = f'''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import promClient from 'prom-client';

const app = express();
const PORT = process.env.PORT || {service.port};

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Prometheus metrics
const register = new promClient.Registry();
promClient.collectDefaultMetrics({{ register }});

app.get('/metrics', async (req, res) => {{
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
}});

// Health checks
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', service: '{service.name}' }});
}});

app.get('/ready', (req, res) => {{
  res.json({{ status: 'ready' }});
}});

'''

        for endpoint in service.endpoints:
            app_ts += f'''
app.{endpoint.method.lower()}('{endpoint.path}', async (req, res) => {{
  // {endpoint.description}
  res.json({{ message: 'Success' }});
}});

'''

        app_ts += f'''
app.listen(PORT, () => {{
  console.log(`{service.name} listening on port ${{PORT}}`);
}});

export default app;
'''

        files['app.ts'] = app_ts

        # Package.json
        package_json = {
            "name": service.name,
            "version": "1.0.0",
            "main": "dist/app.js",
            "scripts": {
                "build": "tsc",
                "start": "node dist/app.js",
                "dev": "ts-node-dev --respawn app.ts"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.5",
                "helmet": "^7.0.0",
                "prom-client": "^14.2.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/express": "^4.17.17",
                "@types/cors": "^2.8.13",
                "ts-node-dev": "^2.0.0"
            }
        }

        files['package.json'] = json.dumps(package_json, indent=2)

        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        return files

    def _generate_spring_service(self,
                                service: MicroserviceSpec,
                                output_dir: Path) -> Dict[str, str]:
        """Generate Spring Boot microservice"""
        files = {}

        # Main application class
        main_java = f'''package com.example.{service.name.replace("-", "")};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
public class Application {{

    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}

    @GetMapping("/health")
    public Map<String, String> health() {{
        return Map.of("status", "healthy", "service", "{service.name}");
    }}

    @GetMapping("/ready")
    public Map<String, String> ready() {{
        return Map.of("status", "ready");
    }}
}}
'''

        files['Application.java'] = main_java

        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        return files

    def _generate_docker_files(self,
                              service: MicroserviceSpec,
                              output_dir: Path,
                              framework: str) -> Dict[str, str]:
        """Generate Dockerfile and .dockerignore"""
        files = {}

        if framework == "fastapi":
            dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {service.port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{service.port}"]
'''
        elif framework == "express":
            dockerfile = f'''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE {service.port}

CMD ["npm", "start"]
'''
        else:
            dockerfile = f'''FROM openjdk:17-slim

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE {service.port}

CMD ["java", "-jar", "app.jar"]
'''

        files['Dockerfile'] = dockerfile

        dockerignore = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
node_modules/
.git/
.gitignore
.dockerignore
Dockerfile
docker-compose.yml
*.md
.env
.vscode/
.idea/
'''

        files['.dockerignore'] = dockerignore

        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        return files

    def _generate_k8s_manifests(self,
                               service: MicroserviceSpec,
                               output_dir: Path) -> Dict[str, str]:
        """Generate Kubernetes manifests"""
        files = {}

        # Deployment
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': service.name,
                'labels': {
                    'app': service.name,
                    'version': 'v1'
                }
            },
            'spec': {
                'replicas': 2,
                'selector': {
                    'matchLabels': {
                        'app': service.name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': service.name,
                            'version': 'v1'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': service.name,
                            'image': f'{service.name}:latest',
                            'ports': [{
                                'containerPort': service.port
                            }],
                            'env': [
                                {'name': k, 'value': v}
                                for k, v in service.environment_vars.items()
                            ],
                            'resources': service.resource_limits or {
                                'requests': {
                                    'memory': '128Mi',
                                    'cpu': '100m'
                                },
                                'limits': {
                                    'memory': '256Mi',
                                    'cpu': '200m'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': service.port
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': service.port
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }

        # Service
        svc = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': service.name,
                'labels': {
                    'app': service.name
                }
            },
            'spec': {
                'type': 'ClusterIP',
                'ports': [{
                    'port': service.port,
                    'targetPort': service.port,
                    'protocol': 'TCP'
                }],
                'selector': {
                    'app': service.name
                }
            }
        }

        k8s_dir = output_dir / 'k8s'
        k8s_dir.mkdir(exist_ok=True)

        import yaml

        with open(k8s_dir / 'deployment.yaml', 'w') as f:
            yaml.dump(deployment, f, default_flow_style=False)
        files['k8s/deployment.yaml'] = yaml.dump(deployment, default_flow_style=False)

        with open(k8s_dir / 'service.yaml', 'w') as f:
            yaml.dump(svc, f, default_flow_style=False)
        files['k8s/service.yaml'] = yaml.dump(svc, default_flow_style=False)

        return files

    def _generate_db_service(self, db_type: DatabaseType, name: str) -> Dict[str, Any]:
        """Generate database service configuration"""
        if db_type == DatabaseType.POSTGRESQL:
            return {
                'image': 'postgres:15-alpine',
                'environment': {
                    'POSTGRES_DB': 'app',
                    'POSTGRES_USER': 'postgres',
                    'POSTGRES_PASSWORD': 'password'
                },
                'volumes': [f'{name}-data:/var/lib/postgresql/data'],
                'ports': ['5432:5432']
            }
        elif db_type == DatabaseType.MONGODB:
            return {
                'image': 'mongo:6-jammy',
                'environment': {
                    'MONGO_INITDB_ROOT_USERNAME': 'admin',
                    'MONGO_INITDB_ROOT_PASSWORD': 'password'
                },
                'volumes': [f'{name}-data:/data/db'],
                'ports': ['27017:27017']
            }
        elif db_type == DatabaseType.REDIS:
            return {
                'image': 'redis:7-alpine',
                'ports': ['6379:6379']
            }
        else:
            return {}

    def _to_func_name(self, path: str) -> str:
        """Convert path to function name"""
        # /users/{id} -> get_users_by_id
        name = path.replace('/', '_').replace('{', '').replace('}', '').strip('_')
        return name or 'root'
