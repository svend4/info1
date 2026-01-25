#!/usr/bin/env python3
"""
Distributed Systems Examples - Microservices, gRPC, Service Mesh, Resilience, Event Sourcing
"""

from pathlib import Path
from tools.ai_generator.distributed import (
    MicroserviceGenerator, ServiceFramework,
    GRPCGenerator,
    ServiceMeshConfigurator, MeshProvider,
    ResiliencePatternGenerator, PatternType,
    EventSourcingGenerator
)


def example_microservice_generation():
    """Generate microservice with FastAPI"""
    print("=" * 60)
    print("Microservice Generation")
    print("=" * 60)

    generator = MicroserviceGenerator(framework=ServiceFramework.FASTAPI)

    files = generator.generate(
        service_name="payment-service",
        database="postgresql",
        enable_cache=True,
        enable_messaging=True,
        output_dir=Path("./output/payment-service")
    )

    print(f"✅ Generated payment-service")
    print(f"   Framework: FastAPI")
    print(f"   Database: PostgreSQL")
    print(f"   Files: {len(files)}")
    print()


def example_grpc_service():
    """Generate gRPC service definitions"""
    print("=" * 60)
    print("gRPC Service Generation")
    print("=" * 60)

    generator = GRPCGenerator()

    files = generator.generate_service(
        service_name="UserService",
        methods=["GetUser", "CreateUser", "UpdateUser", "DeleteUser"],
        output_dir=Path("./output/grpc")
    )

    print(f"✅ Generated gRPC service")
    print(f"   Service: UserService")
    print(f"   Methods: 4")
    print(f"   Files: proto, server, client")
    print()


def example_service_mesh():
    """Configure Istio service mesh"""
    print("=" * 60)
    print("Service Mesh Configuration")
    print("=" * 60)

    configurator = ServiceMeshConfigurator(provider=MeshProvider.ISTIO)

    files = configurator.configure(
        services=["frontend", "api", "database"],
        enable_mtls=True,
        enable_tracing=True,
        output_dir=Path("./output/istio")
    )

    print(f"✅ Configured Istio service mesh")
    print(f"   Services: 3")
    print(f"   mTLS: Enabled")
    print(f"   Tracing: Enabled")
    print()


def example_resilience_patterns():
    """Generate circuit breaker pattern"""
    print("=" * 60)
    print("Resilience Patterns")
    print("=" * 60)

    generator = ResiliencePatternGenerator()

    code = generator.generate_pattern(
        pattern=PatternType.CIRCUIT_BREAKER,
        language="python",
        service_name="external-api"
    )

    print(f"✅ Generated circuit breaker")
    print(f"   Pattern: Circuit Breaker")
    print(f"   Language: Python")
    print(f"   Features: retry, timeout, fallback")
    print()


def example_event_sourcing():
    """Generate event sourcing architecture"""
    print("=" * 60)
    print("Event Sourcing with CQRS")
    print("=" * 60)

    generator = EventSourcingGenerator()

    files = generator.generate(
        aggregate_name="Order",
        events=["OrderCreated", "OrderPaid", "OrderShipped", "OrderDelivered"],
        output_dir=Path("./output/event-sourcing")
    )

    print(f"✅ Generated event sourcing architecture")
    print(f"   Aggregate: Order")
    print(f"   Events: 4")
    print(f"   Pattern: CQRS + Event Store")
    print()


if __name__ == "__main__":
    print("\n🌐 Distributed Systems Examples\n")
    example_microservice_generation()
    example_grpc_service()
    example_service_mesh()
    example_resilience_patterns()
    example_event_sourcing()
    print("✅ All distributed systems examples completed!\n")
