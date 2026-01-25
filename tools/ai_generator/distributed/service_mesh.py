#!/usr/bin/env python3
"""
Service Mesh Generator (Istio)

Генерация Istio service mesh конфигураций для traffic management, security, и observability.
"""

import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class TrafficPolicy(Enum):
    """Traffic Management Policy Types"""
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_REQUEST = "LEAST_REQUEST"
    RANDOM = "RANDOM"
    PASSTHROUGH = "PASSTHROUGH"


class TLSMode(Enum):
    """mTLS Mode"""
    STRICT = "STRICT"
    PERMISSIVE = "PERMISSIVE"
    DISABLE = "DISABLE"


@dataclass
class VirtualServiceRoute:
    """Virtual Service Route"""
    destination: str
    subset: str
    weight: int = 100
    timeout: str = "30s"
    retries: int = 3


@dataclass
class DestinationRule:
    """Destination Rule Configuration"""
    host: str
    traffic_policy: TrafficPolicy = TrafficPolicy.ROUND_ROBIN
    subsets: Dict[str, Dict[str, str]] = field(default_factory=dict)
    circuit_breaker: Optional[Dict[str, Any]] = None


@dataclass
class Gateway:
    """Istio Gateway Configuration"""
    name: str
    hosts: List[str]
    port: int = 80
    protocol: str = "HTTP"


class ServiceMeshGenerator:
    """Service Mesh (Istio) Generator"""

    def __init__(self):
        """Инициализация service mesh generator"""
        self.virtual_services: Dict[str, Any] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.gateways: Dict[str, Gateway] = {}

    def create_virtual_service(self,
                               name: str,
                               hosts: List[str],
                               routes: List[VirtualServiceRoute],
                               gateway: Optional[str] = None) -> Dict[str, Any]:
        """
        Create Istio Virtual Service

        Args:
            name: Virtual service name
            hosts: Host names
            routes: Route configurations
            gateway: Gateway name

        Returns:
            Virtual service configuration
        """
        print(f"🌐 Creating Virtual Service: {name}")

        vs = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'VirtualService',
            'metadata': {
                'name': name
            },
            'spec': {
                'hosts': hosts,
                'http': []
            }
        }

        if gateway:
            vs['spec']['gateways'] = [gateway]

        # Add routes
        for route in routes:
            http_route = {
                'route': [{
                    'destination': {
                        'host': route.destination,
                        'subset': route.subset
                    },
                    'weight': route.weight
                }],
                'timeout': route.timeout,
                'retries': {
                    'attempts': route.retries,
                    'perTryTimeout': '2s'
                }
            }
            vs['spec']['http'].append(http_route)

        self.virtual_services[name] = vs

        print(f"✅ Created Virtual Service with {len(routes)} routes")
        return vs

    def create_destination_rule(self,
                                name: str,
                                host: str,
                                subsets: Dict[str, Dict[str, str]],
                                traffic_policy: TrafficPolicy = TrafficPolicy.ROUND_ROBIN,
                                enable_circuit_breaker: bool = True) -> Dict[str, Any]:
        """
        Create Istio Destination Rule

        Args:
            name: Destination rule name
            host: Service host
            subsets: Traffic subsets (version, canary, etc.)
            traffic_policy: Load balancing policy
            enable_circuit_breaker: Enable circuit breaker

        Returns:
            Destination rule configuration
        """
        print(f"🎯 Creating Destination Rule: {name}")

        dr = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'DestinationRule',
            'metadata': {
                'name': name
            },
            'spec': {
                'host': host,
                'trafficPolicy': {
                    'loadBalancer': {
                        'simple': traffic_policy.value
                    }
                },
                'subsets': []
            }
        }

        # Add subsets
        for subset_name, labels in subsets.items():
            subset = {
                'name': subset_name,
                'labels': labels
            }
            dr['spec']['subsets'].append(subset)

        # Add circuit breaker
        if enable_circuit_breaker:
            dr['spec']['trafficPolicy']['connectionPool'] = {
                'tcp': {
                    'maxConnections': 100
                },
                'http': {
                    'http1MaxPendingRequests': 10,
                    'http2MaxRequests': 100,
                    'maxRequestsPerConnection': 2
                }
            }

            dr['spec']['trafficPolicy']['outlierDetection'] = {
                'consecutiveErrors': 5,
                'interval': '30s',
                'baseEjectionTime': '30s',
                'maxEjectionPercent': 50,
                'minHealthPercent': 50
            }

        dest_rule = DestinationRule(
            host=host,
            traffic_policy=traffic_policy,
            subsets=subsets,
            circuit_breaker=dr['spec']['trafficPolicy'] if enable_circuit_breaker else None
        )

        self.destination_rules[name] = dest_rule

        print(f"✅ Created Destination Rule with {len(subsets)} subsets")
        return dr

    def create_gateway(self,
                      name: str,
                      hosts: List[str],
                      port: int = 80,
                      protocol: str = "HTTP") -> Dict[str, Any]:
        """
        Create Istio Gateway

        Args:
            name: Gateway name
            hosts: Host names
            port: Port number
            protocol: Protocol (HTTP, HTTPS, TCP)

        Returns:
            Gateway configuration
        """
        print(f"🚪 Creating Gateway: {name}")

        gw = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'Gateway',
            'metadata': {
                'name': name
            },
            'spec': {
                'selector': {
                    'istio': 'ingressgateway'
                },
                'servers': [{
                    'port': {
                        'number': port,
                        'name': protocol.lower(),
                        'protocol': protocol
                    },
                    'hosts': hosts
                }]
            }
        }

        gateway = Gateway(
            name=name,
            hosts=hosts,
            port=port,
            protocol=protocol
        )

        self.gateways[name] = gateway

        print(f"✅ Created Gateway for {len(hosts)} hosts")
        return gw

    def create_peer_authentication(self,
                                   name: str,
                                   namespace: str,
                                   mtls_mode: TLSMode = TLSMode.STRICT) -> Dict[str, Any]:
        """
        Create Peer Authentication (mTLS)

        Args:
            name: Policy name
            namespace: Namespace
            mtls_mode: mTLS mode

        Returns:
            Peer authentication configuration
        """
        print(f"🔒 Creating Peer Authentication: {name}")

        pa = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'PeerAuthentication',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'mtls': {
                    'mode': mtls_mode.value
                }
            }
        }

        print(f"✅ Created Peer Authentication with {mtls_mode.value} mode")
        return pa

    def create_authorization_policy(self,
                                    name: str,
                                    namespace: str,
                                    allowed_services: List[str]) -> Dict[str, Any]:
        """
        Create Authorization Policy

        Args:
            name: Policy name
            namespace: Namespace
            allowed_services: List of allowed service accounts

        Returns:
            Authorization policy configuration
        """
        print(f"🛡️  Creating Authorization Policy: {name}")

        ap = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'AuthorizationPolicy',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'action': 'ALLOW',
                'rules': []
            }
        }

        # Add rules for each allowed service
        for service in allowed_services:
            rule = {
                'from': [{
                    'source': {
                        'principals': [f'cluster.local/ns/{namespace}/sa/{service}']
                    }
                }]
            }
            ap['spec']['rules'].append(rule)

        print(f"✅ Created Authorization Policy for {len(allowed_services)} services")
        return ap

    def create_service_entry(self,
                            name: str,
                            hosts: List[str],
                            ports: List[Dict[str, Any]],
                            location: str = "MESH_EXTERNAL") -> Dict[str, Any]:
        """
        Create Service Entry (for external services)

        Args:
            name: Service entry name
            hosts: External hosts
            ports: Port configurations
            location: MESH_INTERNAL or MESH_EXTERNAL

        Returns:
            Service entry configuration
        """
        print(f"🌍 Creating Service Entry: {name}")

        se = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'ServiceEntry',
            'metadata': {
                'name': name
            },
            'spec': {
                'hosts': hosts,
                'ports': ports,
                'location': location,
                'resolution': 'DNS'
            }
        }

        print(f"✅ Created Service Entry for {len(hosts)} external hosts")
        return se

    def create_canary_deployment(self,
                                 service_name: str,
                                 stable_version: str,
                                 canary_version: str,
                                 canary_weight: int = 10) -> Dict[str, List[Dict]]:
        """
        Create canary deployment configuration

        Args:
            service_name: Service name
            stable_version: Stable version label
            canary_version: Canary version label
            canary_weight: Traffic weight for canary (0-100)

        Returns:
            Virtual service and destination rule
        """
        print(f"🐤 Creating Canary Deployment: {service_name}")

        # Destination Rule with subsets
        dr = self.create_destination_rule(
            name=f"{service_name}-dr",
            host=service_name,
            subsets={
                'stable': {'version': stable_version},
                'canary': {'version': canary_version}
            }
        )

        # Virtual Service with weighted routing
        routes = [
            VirtualServiceRoute(
                destination=service_name,
                subset='stable',
                weight=100 - canary_weight
            ),
            VirtualServiceRoute(
                destination=service_name,
                subset='canary',
                weight=canary_weight
            )
        ]

        vs = self.create_virtual_service(
            name=f"{service_name}-vs",
            hosts=[service_name],
            routes=routes
        )

        print(f"✅ Canary: {100-canary_weight}% stable, {canary_weight}% canary")
        return {
            'virtual_service': [vs],
            'destination_rule': [dr]
        }

    def create_retry_policy(self,
                           max_retries: int = 3,
                           timeout: str = "30s",
                           retry_on: List[str] = None) -> Dict[str, Any]:
        """
        Create retry policy

        Args:
            max_retries: Maximum retry attempts
            timeout: Request timeout
            retry_on: Conditions to retry on

        Returns:
            Retry policy configuration
        """
        if retry_on is None:
            retry_on = ['5xx', 'reset', 'connect-failure', 'refused-stream']

        return {
            'attempts': max_retries,
            'perTryTimeout': timeout,
            'retryOn': ','.join(retry_on)
        }

    def create_timeout_policy(self,
                             timeout: str = "30s",
                             idle_timeout: str = "15m") -> Dict[str, Any]:
        """
        Create timeout policy

        Args:
            timeout: Request timeout
            idle_timeout: Idle connection timeout

        Returns:
            Timeout policy configuration
        """
        return {
            'timeout': timeout,
            'idle_timeout': idle_timeout
        }

    def export_manifests(self, output_dir: Path):
        """
        Export all Istio manifests to files

        Args:
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export virtual services
        if self.virtual_services:
            vs_file = output_dir / 'virtual-services.yaml'
            with open(vs_file, 'w') as f:
                yaml.dump_all(self.virtual_services.values(), f, default_flow_style=False)
            print(f"✅ Exported {len(self.virtual_services)} Virtual Services")

        # Export destination rules (convert dataclass to dict)
        if self.destination_rules:
            dr_configs = []
            for name, dr in self.destination_rules.items():
                dr_config = {
                    'apiVersion': 'networking.istio.io/v1beta1',
                    'kind': 'DestinationRule',
                    'metadata': {'name': name},
                    'spec': {
                        'host': dr.host,
                        'trafficPolicy': {
                            'loadBalancer': {'simple': dr.traffic_policy.value}
                        },
                        'subsets': [
                            {'name': k, 'labels': v}
                            for k, v in dr.subsets.items()
                        ]
                    }
                }

                if dr.circuit_breaker:
                    dr_config['spec']['trafficPolicy'].update(dr.circuit_breaker)

                dr_configs.append(dr_config)

            dr_file = output_dir / 'destination-rules.yaml'
            with open(dr_file, 'w') as f:
                yaml.dump_all(dr_configs, f, default_flow_style=False)
            print(f"✅ Exported {len(self.destination_rules)} Destination Rules")

        # Export gateways (convert dataclass to dict)
        if self.gateways:
            gw_configs = []
            for name, gw in self.gateways.items():
                gw_config = {
                    'apiVersion': 'networking.istio.io/v1beta1',
                    'kind': 'Gateway',
                    'metadata': {'name': name},
                    'spec': {
                        'selector': {'istio': 'ingressgateway'},
                        'servers': [{
                            'port': {
                                'number': gw.port,
                                'name': gw.protocol.lower(),
                                'protocol': gw.protocol
                            },
                            'hosts': gw.hosts
                        }]
                    }
                }
                gw_configs.append(gw_config)

            gw_file = output_dir / 'gateways.yaml'
            with open(gw_file, 'w') as f:
                yaml.dump_all(gw_configs, f, default_flow_style=False)
            print(f"✅ Exported {len(self.gateways)} Gateways")

        print(f"📁 All manifests exported to {output_dir}")

    def generate_observability_config(self, namespace: str = "default") -> Dict[str, Any]:
        """
        Generate observability configuration (Telemetry)

        Args:
            namespace: Namespace

        Returns:
            Telemetry configuration
        """
        telemetry = {
            'apiVersion': 'telemetry.istio.io/v1alpha1',
            'kind': 'Telemetry',
            'metadata': {
                'name': 'mesh-telemetry',
                'namespace': namespace
            },
            'spec': {
                'metrics': [{
                    'providers': [{'name': 'prometheus'}]
                }],
                'tracing': [{
                    'providers': [{'name': 'jaeger'}],
                    'randomSamplingPercentage': 100.0
                }],
                'accessLogging': [{
                    'providers': [{'name': 'envoy'}]
                }]
            }
        }

        return telemetry
