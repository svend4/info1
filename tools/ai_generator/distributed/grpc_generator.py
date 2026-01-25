#!/usr/bin/env python3
"""
gRPC Service Generator

Генерация gRPC services для high-performance service-to-service communication.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class FieldType(Enum):
    """Protocol Buffer Field Types"""
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    BOOL = "bool"
    FLOAT = "float"
    DOUBLE = "double"
    BYTES = "bytes"
    TIMESTAMP = "google.protobuf.Timestamp"
    REPEATED = "repeated"
    MESSAGE = "message"


@dataclass
class ProtoField:
    """Protocol Buffer Field"""
    name: str
    field_type: FieldType
    field_number: int
    repeated: bool = False
    optional: bool = False
    message_type: Optional[str] = None


@dataclass
class ProtoMessage:
    """Protocol Buffer Message"""
    name: str
    fields: List[ProtoField] = field(default_factory=list)
    description: str = ""


@dataclass
class ProtoRPC:
    """gRPC RPC Method"""
    name: str
    request_type: str
    response_type: str
    description: str = ""
    streaming_request: bool = False
    streaming_response: bool = False


@dataclass
class ProtoService:
    """gRPC Service Definition"""
    name: str
    rpcs: List[ProtoRPC] = field(default_factory=list)
    description: str = ""


@dataclass
class ProtoFile:
    """Complete Protocol Buffer File"""
    package: str
    messages: List[ProtoMessage] = field(default_factory=list)
    services: List[ProtoService] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class GRPCGenerator:
    """gRPC Service Generator"""

    def __init__(self):
        """Инициализация gRPC generator"""
        self.proto_files: Dict[str, ProtoFile] = {}

    def create_proto_file(self,
                         package: str,
                         services: List[ProtoService],
                         messages: List[ProtoMessage]) -> ProtoFile:
        """
        Create protocol buffer file

        Args:
            package: Package name
            services: List of gRPC services
            messages: List of message types

        Returns:
            Protocol buffer file
        """
        print(f"📝 Creating proto file: {package}")

        proto_file = ProtoFile(
            package=package,
            services=services,
            messages=messages,
            imports=['google/protobuf/timestamp.proto']
        )

        self.proto_files[package] = proto_file

        print(f"✅ Created proto with {len(services)} services, {len(messages)} messages")
        return proto_file

    def generate_proto(self, proto_file: ProtoFile, output_path: Path):
        """
        Generate .proto file

        Args:
            proto_file: Protocol buffer file
            output_path: Output file path
        """
        proto_content = self._generate_proto_content(proto_file)

        with open(output_path, 'w') as f:
            f.write(proto_content)

        print(f"✅ Generated {output_path}")

    def generate_python_server(self,
                               proto_file: ProtoFile,
                               output_dir: Path) -> Dict[str, str]:
        """
        Generate Python gRPC server

        Args:
            proto_file: Protocol buffer file
            output_dir: Output directory

        Returns:
            Generated files
        """
        print(f"🐍 Generating Python gRPC server...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate server implementation
        for service in proto_file.services:
            server_py = self._generate_python_servicer(service, proto_file.package)
            files[f'{service.name.lower()}_server.py'] = server_py

        # Generate main server
        main_server = self._generate_python_main_server(proto_file)
        files['server.py'] = main_server

        # Generate client
        client_py = self._generate_python_client(proto_file)
        files['client.py'] = client_py

        # Generate requirements
        requirements = [
            'grpcio>=1.60.0',
            'grpcio-tools>=1.60.0',
            'protobuf>=4.25.0',
            'grpcio-reflection>=1.60.0',
            'grpcio-health-checking>=1.60.0'
        ]
        files['requirements.txt'] = '\n'.join(requirements)

        # Write files
        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} Python files")
        return files

    def generate_go_server(self,
                          proto_file: ProtoFile,
                          output_dir: Path) -> Dict[str, str]:
        """
        Generate Go gRPC server

        Args:
            proto_file: Protocol buffer file
            output_dir: Output directory

        Returns:
            Generated files
        """
        print(f"🔷 Generating Go gRPC server...")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate server
        for service in proto_file.services:
            server_go = self._generate_go_server(service, proto_file.package)
            files[f'{service.name.lower()}_server.go'] = server_go

        # Generate main
        main_go = self._generate_go_main(proto_file)
        files['main.go'] = main_go

        # Generate go.mod
        go_mod = f'''module {proto_file.package}

go 1.21

require (
    google.golang.org/grpc v1.60.0
    google.golang.org/protobuf v1.32.0
)
'''
        files['go.mod'] = go_mod

        # Write files
        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} Go files")
        return files

    def generate_client_sdk(self,
                           proto_file: ProtoFile,
                           language: str,
                           output_dir: Path) -> Dict[str, str]:
        """
        Generate client SDK

        Args:
            proto_file: Protocol buffer file
            language: Target language (python, go, typescript, java)
            output_dir: Output directory

        Returns:
            Generated files
        """
        if language == "python":
            return self._generate_python_client_sdk(proto_file, output_dir)
        elif language == "go":
            return self._generate_go_client_sdk(proto_file, output_dir)
        elif language == "typescript":
            return self._generate_typescript_client_sdk(proto_file, output_dir)
        else:
            return {}

    def _generate_proto_content(self, proto_file: ProtoFile) -> str:
        """Generate .proto file content"""
        proto = f'''syntax = "proto3";

package {proto_file.package};

'''

        # Add imports
        for imp in proto_file.imports:
            proto += f'import "{imp}";\n'

        proto += '\n'

        # Add messages
        for message in proto_file.messages:
            proto += f'// {message.description}\n' if message.description else ''
            proto += f'message {message.name} {{\n'

            for field in message.fields:
                field_str = self._format_proto_field(field)
                proto += f'  {field_str}\n'

            proto += '}\n\n'

        # Add services
        for service in proto_file.services:
            proto += f'// {service.description}\n' if service.description else ''
            proto += f'service {service.name} {{\n'

            for rpc in service.rpcs:
                request_stream = 'stream ' if rpc.streaming_request else ''
                response_stream = 'stream ' if rpc.streaming_response else ''

                proto += f'  // {rpc.description}\n' if rpc.description else ''
                proto += f'  rpc {rpc.name}({request_stream}{rpc.request_type}) returns ({response_stream}{rpc.response_type});\n'

            proto += '}\n\n'

        return proto

    def _format_proto_field(self, field: ProtoField) -> str:
        """Format protocol buffer field"""
        field_prefix = ''

        if field.repeated:
            field_prefix = 'repeated '
        elif field.optional:
            field_prefix = 'optional '

        if field.field_type == FieldType.MESSAGE:
            field_type = field.message_type
        else:
            field_type = field.field_type.value

        return f'{field_prefix}{field_type} {field.name} = {field.field_number};'

    def _generate_python_servicer(self, service: ProtoService, package: str) -> str:
        """Generate Python servicer implementation"""
        code = f'''import grpc
from concurrent import futures
import logging

import {package}_pb2
import {package}_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {service.name}Servicer({package}_pb2_grpc.{service.name}Servicer):
    """
    {service.description}
    """

'''

        for rpc in service.rpcs:
            if rpc.streaming_response:
                code += f'''    def {rpc.name}(self, request, context):
        """
        {rpc.description}
        """
        logger.info(f"{rpc.name} called")

        # TODO: Implement streaming response
        for i in range(10):
            response = {package}_pb2.{rpc.response_type}()
            yield response

'''
            else:
                code += f'''    def {rpc.name}(self, request, context):
        """
        {rpc.description}
        """
        logger.info(f"{rpc.name} called")

        # TODO: Implement logic
        response = {package}_pb2.{rpc.response_type}()
        return response

'''

        return code

    def _generate_python_main_server(self, proto_file: ProtoFile) -> str:
        """Generate Python main server"""
        code = f'''import grpc
from concurrent import futures
import logging
import signal
import sys

import {proto_file.package}_pb2_grpc
'''

        for service in proto_file.services:
            code += f'from {service.name.lower()}_server import {service.name}Servicer\n'

        code += '''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

'''

        for service in proto_file.services:
            code += f'''    {proto_file.package}_pb2_grpc.add_{service.name}Servicer_to_server(
        {service.name}Servicer(), server
    )
'''

        code += '''
    server.add_insecure_port('[::]:50051')
    server.start()

    logger.info("gRPC server started on port 50051")

    def handle_sigterm(*args):
        logger.info("Received shutdown signal")
        server.stop(grace=10)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    server.wait_for_termination()

if __name__ == '__main__':
    serve()
'''

        return code

    def _generate_python_client(self, proto_file: ProtoFile) -> str:
        """Generate Python client"""
        code = f'''import grpc
import logging

import {proto_file.package}_pb2
import {proto_file.package}_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {proto_file.package.capitalize()}Client:
    """
    gRPC client for {proto_file.package}
    """

    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{{host}}:{{port}}')
'''

        for service in proto_file.services:
            code += f'        self.{service.name.lower()}_stub = {proto_file.package}_pb2_grpc.{service.name}Stub(self.channel)\n'

        code += '\n'

        # Generate method for each RPC
        for service in proto_file.services:
            for rpc in service.rpcs:
                code += f'''    def {rpc.name.lower()}(self, **kwargs):
        """
        {rpc.description}
        """
        request = {proto_file.package}_pb2.{rpc.request_type}(**kwargs)

        try:
            response = self.{service.name.lower()}_stub.{rpc.name}(request)
            return response
        except grpc.RpcError as e:
            logger.error(f"RPC failed: {{e.code()}} - {{e.details()}}")
            raise

'''

        code += '''    def close(self):
        """Close the gRPC channel"""
        self.channel.close()
'''

        return code

    def _generate_go_server(self, service: ProtoService, package: str) -> str:
        """Generate Go server implementation"""
        code = f'''package main

import (
    "context"
    "log"

    pb "{package}/proto"
)

type {service.name.lower()}Server struct {{
    pb.Unimplemented{service.name}Server
}}

'''

        for rpc in service.rpcs:
            code += f'''func (s *{service.name.lower()}Server) {rpc.name}(ctx context.Context, req *pb.{rpc.request_type}) (*pb.{rpc.response_type}, error) {{
    log.Printf("{rpc.name} called")

    // TODO: Implement logic
    return &pb.{rpc.response_type}{{}}, nil
}}

'''

        return code

    def _generate_go_main(self, proto_file: ProtoFile) -> str:
        """Generate Go main.go"""
        code = f'''package main

import (
    "log"
    "net"

    "google.golang.org/grpc"
    pb "{proto_file.package}/proto"
)

func main() {{
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {{
        log.Fatalf("Failed to listen: %v", err)
    }}

    s := grpc.NewServer()
'''

        for service in proto_file.services:
            code += f'    pb.Register{service.name}Server(s, &{service.name.lower()}Server{{}})\n'

        code += '''
    log.Println("gRPC server started on port 50051")
    if err := s.Serve(lis); err != nil {
        log.Fatalf("Failed to serve: %v", err)
    }
}
'''

        return code

    def _generate_python_client_sdk(self, proto_file: ProtoFile, output_dir: Path) -> Dict[str, str]:
        """Generate Python client SDK"""
        return self.generate_python_server(proto_file, output_dir)

    def _generate_go_client_sdk(self, proto_file: ProtoFile, output_dir: Path) -> Dict[str, str]:
        """Generate Go client SDK"""
        return self.generate_go_server(proto_file, output_dir)

    def _generate_typescript_client_sdk(self, proto_file: ProtoFile, output_dir: Path) -> Dict[str, str]:
        """Generate TypeScript client SDK"""
        files = {}

        client_ts = f'''import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const PROTO_PATH = './{proto_file.package}.proto';

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {{
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
}});

const proto = grpc.loadPackageDefinition(packageDefinition).{proto_file.package};

export class {proto_file.package.capitalize()}Client {{
  private client: any;

  constructor(host: string = 'localhost', port: number = 50051) {{
    this.client = new proto.{proto_file.services[0].name}(
      `${{host}}:${{port}}`,
      grpc.credentials.createInsecure()
    );
  }}
'''

        for service in proto_file.services:
            for rpc in service.rpcs:
                client_ts += f'''
  {rpc.name.lower()}(request: any): Promise<any> {{
    return new Promise((resolve, reject) => {{
      this.client.{rpc.name}(request, (err: any, response: any) => {{
        if (err) reject(err);
        else resolve(response);
      }});
    }});
  }}
'''

        client_ts += '''}
'''

        files['client.ts'] = client_ts

        return files
