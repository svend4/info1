#!/usr/bin/env python3
"""
DevOps Excellence Examples - GitOps, IaC, Observability, Policy as Code
"""

from pathlib import Path
from tools.ai_generator.devops import (
    GitOpsGenerator, GitOpsTool,
    InfrastructureGenerator, IaCTool, CloudProvider,
    ObservabilityGenerator,
    PolicyAsCodeGenerator, PolicyEngine
)


def example_gitops_argocd():
    """Generate ArgoCD GitOps configuration"""
    print("=" * 60)
    print("GitOps Configuration (ArgoCD)")
    print("=" * 60)

    generator = GitOpsGenerator(tool=GitOpsTool.ARGOCD)

    generator.add_application(
        name="frontend",
        path="./k8s/frontend",
        namespace="production"
    )

    generator.add_application(
        name="backend-api",
        path="./k8s/api",
        namespace="production"
    )

    files = generator.generate(Path("./output/gitops"))

    print(f"✅ Generated ArgoCD configuration")
    print(f"   Applications: 2")
    print(f"   Files: {len(files)}")
    print()


def example_infrastructure_terraform():
    """Generate Terraform infrastructure"""
    print("=" * 60)
    print("Infrastructure as Code (Terraform)")
    print("=" * 60)

    generator = InfrastructureGenerator(
        tool=IaCTool.TERRAFORM,
        provider=CloudProvider.AWS
    )

    generator.add_resource("vpc", "main_vpc", {"cidr": "10.0.0.0/16"})
    generator.add_resource("subnet", "public_subnet", {"cidr": "10.0.1.0/24"})
    generator.add_resource("ec2", "app_server", {"instance_type": "t3.medium"})
    generator.add_resource("rds", "database", {"instance_class": "db.t3.micro"})

    files = generator.generate(Path("./output/terraform"))

    print(f"✅ Generated Terraform configuration")
    print(f"   Provider: AWS")
    print(f"   Resources: 4")
    print(f"   Files: {len(files)}")
    print()


def example_observability_stack():
    """Generate observability stack"""
    print("=" * 60)
    print("Observability Stack")
    print("=" * 60)

    generator = ObservabilityGenerator()

    files = generator.generate_stack(
        components=["prometheus", "grafana", "loki", "jaeger"],
        deployment="kubernetes",
        output_dir=Path("./output/observability")
    )

    print(f"✅ Generated observability stack")
    print(f"   Components: Prometheus, Grafana, Loki, Jaeger")
    print(f"   Deployment: Kubernetes")
    print(f"   Files: {len(files)}")
    print()


def example_policy_as_code():
    """Generate OPA policies"""
    print("=" * 60)
    print("Policy as Code (OPA)")
    print("=" * 60)

    generator = PolicyAsCodeGenerator(engine=PolicyEngine.OPA)

    # Create common security policies
    policies = generator.create_security_policies()

    files = generator.generate(Path("./output/policies"))

    print(f"✅ Generated OPA policies")
    print(f"   Engine: Open Policy Agent")
    print(f"   Policies: {len(policies)}")
    print(f"   Files: {len(files)}")
    print()


if __name__ == "__main__":
    print("\n🚀 DevOps Excellence Examples\n")
    example_gitops_argocd()
    example_infrastructure_terraform()
    example_observability_stack()
    example_policy_as_code()
    print("✅ All DevOps examples completed!\n")
