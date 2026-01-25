#!/usr/bin/env python3
"""
On-Premise Deployment Module

Enterprise on-premise решение с полным контролем.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class DeploymentMode(Enum):
    """Режим развертывания"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    BARE_METAL = "bare_metal"
    VM = "virtual_machine"


class DatabaseType(Enum):
    """Тип базы данных"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    ORACLE = "oracle"
    MSSQL = "mssql"


@dataclass
class OnPremiseConfig:
    """Конфигурация on-premise"""
    installation_name: str
    deployment_mode: DeploymentMode
    database: DatabaseType
    high_availability: bool
    backup_enabled: bool
    monitoring_enabled: bool
    load_balancer: bool
    ssl_enabled: bool
    custom_domain: Optional[str] = None
    air_gapped: bool = False  # Без интернета

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['deployment_mode'] = self.deployment_mode.value
        data['database'] = self.database.value
        return data


class OnPremiseDeployment:
    """
    On-Premise Deployment Manager

    Управление on-premise установками:
    - Docker/Kubernetes развертывание
    - Конфигурация БД
    - High Availability setup
    - Backup & Restore
    - Monitoring интеграция
    """

    def __init__(self, storage_path: str = './onpremise'):
        """
        Инициализация

        Args:
            storage_path: Путь для конфигураций
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def generate_kubernetes_manifests(self, config: OnPremiseConfig) -> Dict[str, str]:
        """
        Генерация Kubernetes манифестов

        Args:
            config: Конфигурация

        Returns:
            Словарь манифестов
        """
        manifests = {}

        # Namespace
        manifests['namespace.yaml'] = self._generate_namespace(config)

        # Deployment
        manifests['deployment.yaml'] = self._generate_deployment(config)

        # Service
        manifests['service.yaml'] = self._generate_service(config)

        # ConfigMap
        manifests['configmap.yaml'] = self._generate_configmap(config)

        # Secrets
        manifests['secrets.yaml'] = self._generate_secrets(config)

        # Database StatefulSet
        manifests['database.yaml'] = self._generate_database(config)

        # Ingress
        if config.custom_domain:
            manifests['ingress.yaml'] = self._generate_ingress(config)

        # HPA (Horizontal Pod Autoscaler)
        manifests['hpa.yaml'] = self._generate_hpa(config)

        # PersistentVolumes
        manifests['storage.yaml'] = self._generate_storage(config)

        return manifests

    def _generate_namespace(self, config: OnPremiseConfig) -> str:
        """Генерация Namespace"""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: {config.installation_name}
  labels:
    name: {config.installation_name}
"""

    def _generate_deployment(self, config: OnPremiseConfig) -> str:
        """Генерация Deployment"""
        replicas = 3 if config.high_availability else 1

        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config.installation_name}-app
  namespace: {config.installation_name}
  labels:
    app: {config.installation_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {config.installation_name}
  template:
    metadata:
      labels:
        app: {config.installation_name}
    spec:
      containers:
      - name: app
        image: aigenerator/app:latest
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {config.installation_name}-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://{config.installation_name}-redis:6379
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: storage
          mountPath: /app/storage
        - name: config
          mountPath: /app/config
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: {config.installation_name}-storage
      - name: config
        configMap:
          name: {config.installation_name}-config
"""

    def _generate_service(self, config: OnPremiseConfig) -> str:
        """Генерация Service"""
        service_type = "LoadBalancer" if config.load_balancer else "ClusterIP"

        return f"""apiVersion: v1
kind: Service
metadata:
  name: {config.installation_name}-service
  namespace: {config.installation_name}
  labels:
    app: {config.installation_name}
spec:
  type: {service_type}
  selector:
    app: {config.installation_name}
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: https
    port: 443
    targetPort: 8080
    protocol: TCP
"""

    def _generate_configmap(self, config: OnPremiseConfig) -> str:
        """Генерация ConfigMap"""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {config.installation_name}-config
  namespace: {config.installation_name}
data:
  app.conf: |
    server {{
      host = "0.0.0.0"
      port = 8080
    }}

    database {{
      type = "{config.database.value}"
      max_connections = 100
    }}

    features {{
      ai_enabled = true
      monitoring = {str(config.monitoring_enabled).lower()}
      backup = {str(config.backup_enabled).lower()}
    }}
"""

    def _generate_secrets(self, config: OnPremiseConfig) -> str:
        """Генерация Secrets"""
        return f"""apiVersion: v1
kind: Secret
metadata:
  name: {config.installation_name}-secrets
  namespace: {config.installation_name}
type: Opaque
stringData:
  database-url: "postgresql://user:password@{config.installation_name}-db:5432/aigenerator"
  api-key: "your-api-key-here"
  jwt-secret: "your-jwt-secret-here"
"""

    def _generate_database(self, config: OnPremiseConfig) -> str:
        """Генерация Database StatefulSet"""
        db_image = {
            DatabaseType.POSTGRESQL: "postgres:14",
            DatabaseType.MYSQL: "mysql:8.0",
            DatabaseType.MONGODB: "mongo:6.0"
        }.get(config.database, "postgres:14")

        replicas = 3 if config.high_availability else 1

        return f"""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {config.installation_name}-db
  namespace: {config.installation_name}
spec:
  serviceName: {config.installation_name}-db
  replicas: {replicas}
  selector:
    matchLabels:
      app: {config.installation_name}-db
  template:
    metadata:
      labels:
        app: {config.installation_name}-db
    spec:
      containers:
      - name: database
        image: {db_image}
        ports:
        - containerPort: 5432
          name: postgresql
        env:
        - name: POSTGRES_DB
          value: aigenerator
        - name: POSTGRES_USER
          value: admin
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {config.installation_name}-secrets
              key: database-password
        volumeMounts:
        - name: db-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: db-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: {config.installation_name}-db
  namespace: {config.installation_name}
spec:
  clusterIP: None
  selector:
    app: {config.installation_name}-db
  ports:
  - port: 5432
    targetPort: 5432
"""

    def _generate_ingress(self, config: OnPremiseConfig) -> str:
        """Генерация Ingress"""
        tls_section = ""
        if config.ssl_enabled:
            tls_section = f"""
  tls:
  - hosts:
    - {config.custom_domain}
    secretName: {config.installation_name}-tls
"""

        return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {config.installation_name}-ingress
  namespace: {config.installation_name}
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:{tls_section}
  rules:
  - host: {config.custom_domain}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {config.installation_name}-service
            port:
              number: 80
"""

    def _generate_hpa(self, config: OnPremiseConfig) -> str:
        """Генерация HorizontalPodAutoscaler"""
        return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {config.installation_name}-hpa
  namespace: {config.installation_name}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {config.installation_name}-app
  minReplicas: {"3" if config.high_availability else "1"}
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""

    def _generate_storage(self, config: OnPremiseConfig) -> str:
        """Генерация PersistentVolumeClaim"""
        return f"""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {config.installation_name}-storage
  namespace: {config.installation_name}
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: standard
"""

    def generate_docker_compose(self, config: OnPremiseConfig) -> str:
        """Генерация Docker Compose"""
        db_service = self._generate_db_service(config)

        return f"""version: '3.8'

services:
  app:
    image: aigenerator/app:latest
    container_name: {config.installation_name}-app
    ports:
      - "80:8080"
      - "443:8443"
    environment:
      - DATABASE_URL=postgresql://admin:password@db:5432/aigenerator
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=production
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage
      - ./config:/app/config
    restart: unless-stopped
    networks:
      - aigenerator

  {db_service}

  redis:
    image: redis:7-alpine
    container_name: {config.installation_name}-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - aigenerator

  nginx:
    image: nginx:alpine
    container_name: {config.installation_name}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - aigenerator

volumes:
  db_data:
  redis_data:

networks:
  aigenerator:
    driver: bridge
"""

    def _generate_db_service(self, config: OnPremiseConfig) -> str:
        """Генерация database сервиса для Docker Compose"""
        if config.database == DatabaseType.POSTGRESQL:
            return """db:
    image: postgres:14
    container_name: aigenerator-db
    environment:
      - POSTGRES_DB=aigenerator
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - aigenerator"""
        elif config.database == DatabaseType.MYSQL:
            return """db:
    image: mysql:8.0
    container_name: aigenerator-db
    environment:
      - MYSQL_DATABASE=aigenerator
      - MYSQL_USER=admin
      - MYSQL_PASSWORD=password
      - MYSQL_ROOT_PASSWORD=rootpassword
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    restart: unless-stopped
    networks:
      - aigenerator"""
        else:
            return """db:
    image: mongo:6.0
    container_name: aigenerator-db
    environment:
      - MONGO_INITDB_DATABASE=aigenerator
    ports:
      - "27017:27017"
    volumes:
      - db_data:/data/db
    restart: unless-stopped
    networks:
      - aigenerator"""

    def generate_installation_script(self, config: OnPremiseConfig) -> str:
        """Генерация скрипта установки"""
        return f"""#!/bin/bash
# AI Generator On-Premise Installation Script

set -e

echo "=========================================="
echo "AI Generator On-Premise Installation"
echo "Installation: {config.installation_name}"
echo "=========================================="

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || {{ echo "Docker is required but not installed. Aborting." >&2; exit 1; }}
command -v docker-compose >/dev/null 2>&1 || {{ echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }}

# Create directories
echo "Creating directories..."
mkdir -p storage config logs backups

# Generate config files
echo "Generating configuration..."
cat > config/app.conf << EOF
# AI Generator Configuration
installation_name = "{config.installation_name}"
database = "{config.database.value}"
high_availability = {str(config.high_availability).lower()}
monitoring_enabled = {str(config.monitoring_enabled).lower()}
EOF

# Pull images
echo "Pulling Docker images..."
docker-compose pull

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for database
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec -T app python manage.py migrate

# Create admin user
echo "Creating admin user..."
docker-compose exec -T app python manage.py createsuperuser --noinput || true

# Setup backup cron job
if [ "{config.backup_enabled}" = "True" ]; then
    echo "Setting up backup cron job..."
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/aigenerator/backup.sh") | crontab -
fi

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Access your installation at:"
if [ -n "{config.custom_domain}" ]; then
    echo "  https://{config.custom_domain}"
else
    echo "  http://localhost"
fi
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "Please change the default password immediately!"
"""

    def generate_backup_script(self, config: OnPremiseConfig) -> str:
        """Генерация скрипта backup"""
        return f"""#!/bin/bash
# AI Generator Backup Script

set -e

BACKUP_DIR="/opt/aigenerator/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="aigenerator_backup_$TIMESTAMP"

echo "Starting backup: $BACKUP_NAME"

# Create backup directory
mkdir -p $BACKUP_DIR/$BACKUP_NAME

# Backup database
echo "Backing up database..."
docker-compose exec -T db pg_dump -U admin aigenerator > $BACKUP_DIR/$BACKUP_NAME/database.sql

# Backup storage
echo "Backing up storage..."
tar -czf $BACKUP_DIR/$BACKUP_NAME/storage.tar.gz ./storage

# Backup config
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/$BACKUP_NAME/config.tar.gz ./config

# Create manifest
cat > $BACKUP_DIR/$BACKUP_NAME/manifest.json << EOF
{{
  "timestamp": "$TIMESTAMP",
  "installation": "{config.installation_name}",
  "database": "{config.database.value}",
  "version": "1.0.0"
}}
EOF

# Compress everything
echo "Compressing backup..."
cd $BACKUP_DIR
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "aigenerator_backup_*.tar.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
"""

    def generate_restore_script(self, config: OnPremiseConfig) -> str:
        """Генерация скрипта restore"""
        return f"""#!/bin/bash
# AI Generator Restore Script

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1
BACKUP_DIR="/opt/aigenerator/backups"
TEMP_DIR="/tmp/aigenerator_restore"

echo "Restoring from: $BACKUP_FILE"

# Extract backup
echo "Extracting backup..."
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Find backup directory
BACKUP_NAME=$(ls $TEMP_DIR)

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
echo "Restoring database..."
docker-compose up -d db
sleep 10
cat $TEMP_DIR/$BACKUP_NAME/database.sql | docker-compose exec -T db psql -U admin aigenerator

# Restore storage
echo "Restoring storage..."
rm -rf ./storage/*
tar -xzf $TEMP_DIR/$BACKUP_NAME/storage.tar.gz

# Restore config
echo "Restoring configuration..."
tar -xzf $TEMP_DIR/$BACKUP_NAME/config.tar.gz

# Restart services
echo "Restarting services..."
docker-compose up -d

# Cleanup
rm -rf $TEMP_DIR

echo "Restore complete!"
"""

    def generate_monitoring_config(self, config: OnPremiseConfig) -> Dict[str, str]:
        """Генерация конфигурации мониторинга (Prometheus + Grafana)"""
        configs = {}

        # Prometheus config
        configs['prometheus.yml'] = f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aigenerator'
    static_configs:
      - targets: ['{config.installation_name}-app:8080']
        labels:
          app: '{config.installation_name}'

  - job_name: 'database'
    static_configs:
      - targets: ['{config.installation_name}-db:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['{config.installation_name}-redis:9121']
"""

        # Grafana dashboard
        configs['grafana_dashboard.json'] = json.dumps({
            "dashboard": {
                "title": f"{config.installation_name} Metrics",
                "panels": [
                    {
                        "title": "Request Rate",
                        "targets": [{"expr": "rate(http_requests_total[5m])"}]
                    },
                    {
                        "title": "Response Time",
                        "targets": [{"expr": "http_request_duration_seconds"}]
                    },
                    {
                        "title": "Database Connections",
                        "targets": [{"expr": "pg_stat_activity_count"}]
                    }
                ]
            }
        }, indent=2)

        return configs

    def save_installation_package(self, config: OnPremiseConfig, output_dir: str):
        """
        Сохранение полного installation package

        Args:
            config: Конфигурация
            output_dir: Директория для сохранения
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Kubernetes manifests
        if config.deployment_mode == DeploymentMode.KUBERNETES:
            k8s_dir = output_path / 'kubernetes'
            k8s_dir.mkdir(exist_ok=True)

            manifests = self.generate_kubernetes_manifests(config)
            for filename, content in manifests.items():
                with open(k8s_dir / filename, 'w') as f:
                    f.write(content)

        # Docker Compose
        if config.deployment_mode == DeploymentMode.DOCKER:
            compose = self.generate_docker_compose(config)
            with open(output_path / 'docker-compose.yml', 'w') as f:
                f.write(compose)

        # Installation scripts
        scripts_dir = output_path / 'scripts'
        scripts_dir.mkdir(exist_ok=True)

        install_script = self.generate_installation_script(config)
        with open(scripts_dir / 'install.sh', 'w') as f:
            f.write(install_script)

        backup_script = self.generate_backup_script(config)
        with open(scripts_dir / 'backup.sh', 'w') as f:
            f.write(backup_script)

        restore_script = self.generate_restore_script(config)
        with open(scripts_dir / 'restore.sh', 'w') as f:
            f.write(restore_script)

        # Make scripts executable
        import os
        for script in scripts_dir.glob('*.sh'):
            os.chmod(script, 0o755)

        # Monitoring config
        if config.monitoring_enabled:
            monitoring_dir = output_path / 'monitoring'
            monitoring_dir.mkdir(exist_ok=True)

            monitoring_configs = self.generate_monitoring_config(config)
            for filename, content in monitoring_configs.items():
                with open(monitoring_dir / filename, 'w') as f:
                    f.write(content)

        # README
        readme = self._generate_readme(config)
        with open(output_path / 'README.md', 'w') as f:
            f.write(readme)

        print(f"✅ Installation package saved to: {output_path}")

    def _generate_readme(self, config: OnPremiseConfig) -> str:
        """Генерация README для installation package"""
        return f"""# AI Generator On-Premise Installation

Installation Name: `{config.installation_name}`
Deployment Mode: `{config.deployment_mode.value}`
Database: `{config.database.value}`

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
{"- Kubernetes 1.20+" if config.deployment_mode == DeploymentMode.KUBERNETES else ""}

## Installation

1. Review configuration in `config/app.conf`
2. Run installation script:
   ```bash
   ./scripts/install.sh
   ```

## Backup & Restore

### Backup
```bash
./scripts/backup.sh
```

### Restore
```bash
./scripts/restore.sh /path/to/backup.tar.gz
```

## Monitoring

{"Monitoring is enabled. Access Grafana at http://localhost:3000" if config.monitoring_enabled else "Monitoring is disabled"}

## Support

For issues and support, contact your account manager.
"""
