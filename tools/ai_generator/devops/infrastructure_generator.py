#!/usr/bin/env python3
"""
Infrastructure as Code Generator

Автоматическая генерация Infrastructure as Code с Pulumi, Terraform, и AWS CDK.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class IaCTool(Enum):
    """Infrastructure as Code Tool"""
    PULUMI = "pulumi"
    TERRAFORM = "terraform"
    AWS_CDK = "aws_cdk"
    CROSSPLANE = "crossplane"


class CloudProvider(Enum):
    """Cloud Provider"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    KUBERNETES = "kubernetes"


class ResourceType(Enum):
    """Resource Type"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    KUBERNETES = "kubernetes"


@dataclass
class InfraResource:
    """Infrastructure Resource"""
    name: str
    type: ResourceType
    provider: CloudProvider
    properties: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class IaCConfig:
    """Infrastructure as Code Configuration"""
    tool: IaCTool
    project_name: str
    provider: CloudProvider
    language: str = "python"  # python, typescript, go
    resources: List[InfraResource] = field(default_factory=list)


class InfrastructureGenerator:
    """Infrastructure as Code Generator"""

    def __init__(self, config: IaCConfig):
        """
        Initialize IaC generator

        Args:
            config: IaC configuration
        """
        self.config = config

    def add_resource(self, resource: InfraResource):
        """
        Add infrastructure resource

        Args:
            resource: Infrastructure resource
        """
        self.config.resources.append(resource)
        print(f"✅ Added resource: {resource.name} ({resource.type.value})")

    def generate(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate IaC code

        Args:
            output_dir: Output directory

        Returns:
            Generated files
        """
        print(f"🏗️  Generating Infrastructure as Code ({self.config.tool.value})...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        if self.config.tool == IaCTool.PULUMI:
            files.update(self._generate_pulumi_code(output_dir))
        elif self.config.tool == IaCTool.TERRAFORM:
            files.update(self._generate_terraform_code(output_dir))
        elif self.config.tool == IaCTool.AWS_CDK:
            files.update(self._generate_cdk_code(output_dir))

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} IaC files")
        return files

    def _generate_pulumi_code(self, output_dir: Path) -> Dict[str, str]:
        """Generate Pulumi code"""
        files = {}

        if self.config.language == "python":
            files['__main__.py'] = self._generate_pulumi_python()
            files['requirements.txt'] = self._generate_pulumi_requirements()
        elif self.config.language == "typescript":
            files['index.ts'] = self._generate_pulumi_typescript()
            files['package.json'] = self._generate_pulumi_package_json()

        files['Pulumi.yaml'] = self._generate_pulumi_yaml()
        files['Pulumi.dev.yaml'] = self._generate_pulumi_stack_config()
        files['README.md'] = self._generate_pulumi_readme()

        return files

    def _generate_pulumi_python(self) -> str:
        """Generate Pulumi Python code"""
        imports = ['import pulumi']

        if self.config.provider == CloudProvider.AWS:
            imports.append('import pulumi_aws as aws')
        elif self.config.provider == CloudProvider.GCP:
            imports.append('import pulumi_gcp as gcp')
        elif self.config.provider == CloudProvider.AZURE:
            imports.append('import pulumi_azure_native as azure')
        elif self.config.provider == CloudProvider.KUBERNETES:
            imports.append('import pulumi_kubernetes as k8s')

        resources_code = []

        for resource in self.config.resources:
            if resource.type == ResourceType.COMPUTE:
                resources_code.append(self._generate_pulumi_compute(resource))
            elif resource.type == ResourceType.STORAGE:
                resources_code.append(self._generate_pulumi_storage(resource))
            elif resource.type == ResourceType.NETWORK:
                resources_code.append(self._generate_pulumi_network(resource))
            elif resource.type == ResourceType.DATABASE:
                resources_code.append(self._generate_pulumi_database(resource))

        # Exports
        exports = []
        for resource in self.config.resources:
            exports.append(f'pulumi.export("{resource.name}_id", {resource.name}.id)')

        return f"""{chr(10).join(imports)}

# Infrastructure Resources

{chr(10).join(resources_code)}

# Exports
{chr(10).join(exports)}
"""

    def _generate_pulumi_compute(self, resource: InfraResource) -> str:
        """Generate Pulumi compute resource"""
        if self.config.provider == CloudProvider.AWS:
            instance_type = resource.properties.get('instance_type', 't3.micro')
            ami = resource.properties.get('ami', 'ami-0c55b159cbfafe1f0')

            return f"""
# EC2 Instance: {resource.name}
{resource.name} = aws.ec2.Instance(
    "{resource.name}",
    instance_type="{instance_type}",
    ami="{ami}",
    tags={{
        "Name": "{resource.name}",
        "Environment": "production"
    }}
)
"""
        elif self.config.provider == CloudProvider.KUBERNETES:
            return f"""
# Kubernetes Deployment: {resource.name}
{resource.name} = k8s.apps.v1.Deployment(
    "{resource.name}",
    spec={{
        "replicas": 3,
        "selector": {{"match_labels": {{"app": "{resource.name}"}}}},
        "template": {{
            "metadata": {{"labels": {{"app": "{resource.name}"}}}},
            "spec": {{
                "containers": [{{
                    "name": "{resource.name}",
                    "image": "nginx:latest",
                    "ports": [{{"container_port": 80}}]
                }}]
            }}
        }}
    }}
)
"""
        return ""

    def _generate_pulumi_storage(self, resource: InfraResource) -> str:
        """Generate Pulumi storage resource"""
        if self.config.provider == CloudProvider.AWS:
            return f"""
# S3 Bucket: {resource.name}
{resource.name} = aws.s3.Bucket(
    "{resource.name}",
    bucket="{resource.name}-bucket",
    acl="private",
    versioning={{
        "enabled": True
    }},
    server_side_encryption_configuration={{
        "rule": {{
            "apply_server_side_encryption_by_default": {{
                "sse_algorithm": "AES256"
            }}
        }}
    }},
    tags={{
        "Name": "{resource.name}",
        "Environment": "production"
    }}
)
"""
        return ""

    def _generate_pulumi_network(self, resource: InfraResource) -> str:
        """Generate Pulumi network resource"""
        if self.config.provider == CloudProvider.AWS:
            cidr = resource.properties.get('cidr', '10.0.0.0/16')

            return f"""
# VPC: {resource.name}
{resource.name} = aws.ec2.Vpc(
    "{resource.name}",
    cidr_block="{cidr}",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={{
        "Name": "{resource.name}",
        "Environment": "production"
    }}
)

# Internet Gateway
{resource.name}_igw = aws.ec2.InternetGateway(
    "{resource.name}-igw",
    vpc_id={resource.name}.id,
    tags={{
        "Name": "{resource.name}-igw"
    }}
)

# Public Subnet
{resource.name}_subnet = aws.ec2.Subnet(
    "{resource.name}-subnet",
    vpc_id={resource.name}.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
    tags={{
        "Name": "{resource.name}-subnet"
    }}
)
"""
        return ""

    def _generate_pulumi_database(self, resource: InfraResource) -> str:
        """Generate Pulumi database resource"""
        if self.config.provider == CloudProvider.AWS:
            engine = resource.properties.get('engine', 'postgres')
            instance_class = resource.properties.get('instance_class', 'db.t3.micro')

            return f"""
# RDS Instance: {resource.name}
{resource.name} = aws.rds.Instance(
    "{resource.name}",
    allocated_storage=20,
    engine="{engine}",
    engine_version="14.7",
    instance_class="{instance_class}",
    db_name="{resource.name.replace('-', '_')}",
    username="admin",
    password=pulumi.Config().require_secret("db_password"),
    skip_final_snapshot=True,
    publicly_accessible=False,
    tags={{
        "Name": "{resource.name}",
        "Environment": "production"
    }}
)
"""
        return ""

    def _generate_pulumi_requirements(self) -> str:
        """Generate Pulumi requirements.txt"""
        requirements = ['pulumi>=3.0.0']

        if self.config.provider == CloudProvider.AWS:
            requirements.append('pulumi-aws>=6.0.0')
        elif self.config.provider == CloudProvider.GCP:
            requirements.append('pulumi-gcp>=7.0.0')
        elif self.config.provider == CloudProvider.AZURE:
            requirements.append('pulumi-azure-native>=2.0.0')
        elif self.config.provider == CloudProvider.KUBERNETES:
            requirements.append('pulumi-kubernetes>=4.0.0')

        return '\n'.join(requirements) + '\n'

    def _generate_pulumi_typescript(self) -> str:
        """Generate Pulumi TypeScript code"""
        imports = ['import * as pulumi from "@pulumi/pulumi";']

        if self.config.provider == CloudProvider.AWS:
            imports.append('import * as aws from "@pulumi/aws";')

        return f"""{chr(10).join(imports)}

// Infrastructure Resources

// EC2 Instance
const instance = new aws.ec2.Instance("web-server", {{
    instanceType: "t3.micro",
    ami: "ami-0c55b159cbfafe1f0",
    tags: {{
        Name: "web-server",
        Environment: "production"
    }}
}});

// Exports
export const instanceId = instance.id;
export const instancePublicIp = instance.publicIp;
"""

    def _generate_pulumi_package_json(self) -> str:
        """Generate Pulumi package.json"""
        dependencies = {
            "@pulumi/pulumi": "^3.0.0"
        }

        if self.config.provider == CloudProvider.AWS:
            dependencies["@pulumi/aws"] = "^6.0.0"

        return json.dumps({
            "name": self.config.project_name,
            "version": "1.0.0",
            "main": "index.ts",
            "devDependencies": {
                "@types/node": "^20.0.0",
                "typescript": "^5.0.0"
            },
            "dependencies": dependencies
        }, indent=2)

    def _generate_pulumi_yaml(self) -> str:
        """Generate Pulumi.yaml"""
        config = {
            'name': self.config.project_name,
            'runtime': self.config.language,
            'description': f'Infrastructure for {self.config.project_name}'
        }

        if self.config.language == 'python':
            config['runtime'] = {
                'name': 'python',
                'options': {
                    'virtualenv': 'venv'
                }
            }

        import yaml
        return yaml.dump(config, default_flow_style=False)

    def _generate_pulumi_stack_config(self) -> str:
        """Generate Pulumi stack configuration"""
        config = {
            'config': {
                f'{self.config.provider.value}:region': 'us-east-1'
            }
        }

        import yaml
        return yaml.dump(config, default_flow_style=False)

    def _generate_pulumi_readme(self) -> str:
        """Generate Pulumi README"""
        return f"""# {self.config.project_name} Infrastructure

Infrastructure as Code using Pulumi and {self.config.provider.value.upper()}.

## Prerequisites

- Pulumi CLI
- {self.config.provider.value.upper()} credentials
- Python 3.8+ (for Python runtime)

## Setup

```bash
# Install dependencies
{'pip install -r requirements.txt' if self.config.language == 'python' else 'npm install'}

# Configure Pulumi
pulumi login
pulumi stack init dev

# Set configuration
pulumi config set {self.config.provider.value}:region us-east-1
pulumi config set --secret db_password YOUR_PASSWORD
```

## Deploy

```bash
# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# View outputs
pulumi stack output
```

## Destroy

```bash
pulumi destroy
```

## Resources

{chr(10).join([f"- **{r.name}**: {r.type.value} ({r.provider.value})" for r in self.config.resources])}
"""

    def _generate_terraform_code(self, output_dir: Path) -> Dict[str, str]:
        """Generate Terraform code"""
        files = {}

        files['main.tf'] = self._generate_terraform_main()
        files['variables.tf'] = self._generate_terraform_variables()
        files['outputs.tf'] = self._generate_terraform_outputs()
        files['terraform.tfvars'] = self._generate_terraform_tfvars()
        files['README.md'] = self._generate_terraform_readme()

        return files

    def _generate_terraform_main(self) -> str:
        """Generate Terraform main.tf"""
        provider_config = ''

        if self.config.provider == CloudProvider.AWS:
            provider_config = """
provider "aws" {
  region = var.aws_region
}
"""

        resources = []

        for resource in self.config.resources:
            if resource.type == ResourceType.COMPUTE and self.config.provider == CloudProvider.AWS:
                resources.append(f"""
resource "aws_instance" "{resource.name}" {{
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {{
    Name        = "{resource.name}"
    Environment = "production"
  }}
}}
""")

        return f"""terraform {{
  required_version = ">= 1.0"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

{provider_config}

{chr(10).join(resources)}
"""

    def _generate_terraform_variables(self) -> str:
        """Generate Terraform variables.tf"""
        return """variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-0c55b159cbfafe1f0"
}
"""

    def _generate_terraform_outputs(self) -> str:
        """Generate Terraform outputs.tf"""
        outputs = []

        for resource in self.config.resources:
            if resource.type == ResourceType.COMPUTE:
                outputs.append(f"""
output "{resource.name}_id" {{
  description = "ID of {resource.name}"
  value       = aws_instance.{resource.name}.id
}}

output "{resource.name}_public_ip" {{
  description = "Public IP of {resource.name}"
  value       = aws_instance.{resource.name}.public_ip
}}
""")

        return '\n'.join(outputs)

    def _generate_terraform_tfvars(self) -> str:
        """Generate Terraform terraform.tfvars"""
        return """aws_region    = "us-east-1"
instance_type = "t3.micro"
"""

    def _generate_terraform_readme(self) -> str:
        """Generate Terraform README"""
        return f"""# {self.config.project_name} Infrastructure

Infrastructure as Code using Terraform and {self.config.provider.value.upper()}.

## Prerequisites

- Terraform >= 1.0
- {self.config.provider.value.upper()} credentials

## Usage

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy
```
"""

    def _generate_cdk_code(self, output_dir: Path) -> Dict[str, str]:
        """Generate AWS CDK code"""
        files = {}

        files['app.py'] = self._generate_cdk_app()
        files['requirements.txt'] = self._generate_cdk_requirements()
        files['cdk.json'] = self._generate_cdk_json()
        files['README.md'] = self._generate_cdk_readme()

        return files

    def _generate_cdk_app(self) -> str:
        """Generate AWS CDK app.py"""
        return f"""#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
)
from constructs import Construct

class InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "VPC",
            max_azs=2,
            nat_gateways=1
        )

        # S3 Bucket
        bucket = s3.Bucket(self, "Bucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

app = cdk.App()
InfrastructureStack(app, "{self.config.project_name}-stack")
app.synth()
"""

    def _generate_cdk_requirements(self) -> str:
        """Generate AWS CDK requirements.txt"""
        return """aws-cdk-lib>=2.0.0
constructs>=10.0.0
"""

    def _generate_cdk_json(self) -> str:
        """Generate CDK cdk.json"""
        return json.dumps({
            "app": "python3 app.py",
            "context": {
                "@aws-cdk/core:enableStackNameDuplicates": True
            }
        }, indent=2)

    def _generate_cdk_readme(self) -> str:
        """Generate AWS CDK README"""
        return f"""# {self.config.project_name} Infrastructure

Infrastructure as Code using AWS CDK.

## Setup

```bash
pip install -r requirements.txt
cdk bootstrap
```

## Deploy

```bash
cdk deploy
```

## Destroy

```bash
cdk destroy
```
"""

    def create_kubernetes_infrastructure(
        self,
        cluster_name: str
    ) -> InfraResource:
        """
        Create Kubernetes infrastructure resource

        Args:
            cluster_name: Cluster name

        Returns:
            Infrastructure resource
        """
        resource = InfraResource(
            name=cluster_name,
            type=ResourceType.KUBERNETES,
            provider=self.config.provider,
            properties={
                'node_count': 3,
                'node_type': 't3.medium'
            }
        )

        self.add_resource(resource)
        return resource
