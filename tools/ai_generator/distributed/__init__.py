"""
Advanced Distributed Systems Package

Microservices architecture, gRPC, service mesh, resilience patterns, и distributed tracing.
"""

from .microservices_generator import (
    MicroservicesGenerator,
    MicroserviceSpec,
    ServiceDependency,
    ResourceRequirements,
    HealthCheck,
    CommunicationType,
    DeploymentStrategy
)

from .grpc_generator import (
    GRPCGenerator,
    ProtoFile,
    ProtoMessage,
    ProtoField,
    ProtoService,
    ProtoRPC,
    FieldType,
    RPCType
)

from .service_mesh import (
    ServiceMesh,
    VirtualService,
    VirtualServiceRoute,
    DestinationRule,
    LoadBalancerType,
    Gateway,
    PeerAuthentication,
    AuthMode
)

from .resilience_patterns import (
    CircuitBreaker,
    CircuitState,
    RetryPolicy,
    Bulkhead,
    RateLimiter,
    ResilienceConfig,
    CircuitBreakerConfig,
    RetryConfig,
    BulkheadConfig,
    RateLimiterConfig
)

from .distributed_tracing import (
    DistributedTracing,
    TracingConfig,
    TracingBackend,
    SpanKind,
    SpanContext,
    TraceExporter
)

__all__ = [
    # Microservices Generator
    'MicroservicesGenerator',
    'MicroserviceSpec',
    'ServiceDependency',
    'ResourceRequirements',
    'HealthCheck',
    'CommunicationType',
    'DeploymentStrategy',

    # gRPC Generator
    'GRPCGenerator',
    'ProtoFile',
    'ProtoMessage',
    'ProtoField',
    'ProtoService',
    'ProtoRPC',
    'FieldType',
    'RPCType',

    # Service Mesh
    'ServiceMesh',
    'VirtualService',
    'VirtualServiceRoute',
    'DestinationRule',
    'LoadBalancerType',
    'Gateway',
    'PeerAuthentication',
    'AuthMode',

    # Resilience Patterns
    'CircuitBreaker',
    'CircuitState',
    'RetryPolicy',
    'Bulkhead',
    'RateLimiter',
    'ResilienceConfig',
    'CircuitBreakerConfig',
    'RetryConfig',
    'BulkheadConfig',
    'RateLimiterConfig',

    # Distributed Tracing
    'DistributedTracing',
    'TracingConfig',
    'TracingBackend',
    'SpanKind',
    'SpanContext',
    'TraceExporter'
]

__version__ = '1.0.0'
