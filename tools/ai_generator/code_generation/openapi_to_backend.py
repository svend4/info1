#!/usr/bin/env python3
"""
OpenAPI to Backend Code Generator

Генерация backend code из OpenAPI/Swagger спецификаций (FastAPI, Express, Spring Boot).
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class BackendFramework(Enum):
    """Backend Framework Types"""
    FASTAPI = "fastapi"
    FLASK = "flask"
    EXPRESS = "express"
    NESTJS = "nestjs"
    SPRING_BOOT = "spring-boot"
    DJANGO = "django"
    GIN = "gin"  # Go


class HTTPMethod(Enum):
    """HTTP Methods"""
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


@dataclass
class APIEndpoint:
    """API Endpoint Definition"""
    path: str
    method: HTTPMethod
    operation_id: str
    summary: str
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    security: List[Dict[str, List[str]]] = field(default_factory=list)


@dataclass
class APISchema:
    """API Data Schema"""
    name: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class GeneratedBackend:
    """Generated Backend Code"""
    framework: BackendFramework
    routes: str
    models: str
    controllers: str = ""
    services: str = ""
    tests: str = ""
    requirements: List[str] = field(default_factory=list)
    project_structure: Dict[str, str] = field(default_factory=dict)


class OpenAPIToBackendGenerator:
    """OpenAPI to Backend Code Generator"""

    def __init__(self):
        """Инициализация OpenAPI generator"""
        self.endpoints: List[APIEndpoint] = []
        self.schemas: List[APISchema] = []
        self.security_schemes: Dict[str, Any] = {}

    def generate_from_spec(self,
                          openapi_spec: Dict[str, Any],
                          framework: BackendFramework) -> GeneratedBackend:
        """
        Generate backend code from OpenAPI spec

        Args:
            openapi_spec: OpenAPI/Swagger specification
            framework: Target backend framework

        Returns:
            Generated backend code
        """
        print(f"🔧 Generating {framework.value} backend from OpenAPI spec...")

        # Parse OpenAPI spec
        self._parse_openapi_spec(openapi_spec)

        # Generate code based on framework
        if framework == BackendFramework.FASTAPI:
            return self._generate_fastapi()
        elif framework == BackendFramework.EXPRESS:
            return self._generate_express()
        elif framework == BackendFramework.SPRING_BOOT:
            return self._generate_spring_boot()
        elif framework == BackendFramework.DJANGO:
            return self._generate_django()
        else:
            return self._generate_fastapi()

    def load_openapi_file(self, file_path: Path) -> Dict[str, Any]:
        """Load OpenAPI spec from file"""
        with open(file_path) as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def _parse_openapi_spec(self, spec: Dict[str, Any]):
        """Parse OpenAPI specification"""
        # Extract API info
        self.api_info = spec.get('info', {})

        # Parse paths (endpoints)
        paths = spec.get('paths', {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    endpoint = self._parse_endpoint(path, method, operation)
                    self.endpoints.append(endpoint)

        # Parse schemas
        components = spec.get('components', {})
        schemas = components.get('schemas', {})
        for schema_name, schema_def in schemas.items():
            schema = self._parse_schema(schema_name, schema_def)
            self.schemas.append(schema)

        # Parse security schemes
        self.security_schemes = components.get('securitySchemes', {})

    def _parse_endpoint(self, path: str, method: str, operation: Dict) -> APIEndpoint:
        """Parse API endpoint"""
        return APIEndpoint(
            path=path,
            method=HTTPMethod(method),
            operation_id=operation.get('operationId', f"{method}_{path.replace('/', '_')}"),
            summary=operation.get('summary', ''),
            description=operation.get('description', ''),
            parameters=operation.get('parameters', []),
            request_body=operation.get('requestBody'),
            responses=operation.get('responses', {}),
            tags=operation.get('tags', []),
            security=operation.get('security', [])
        )

    def _parse_schema(self, name: str, schema_def: Dict) -> APISchema:
        """Parse data schema"""
        return APISchema(
            name=name,
            type=schema_def.get('type', 'object'),
            properties=schema_def.get('properties', {}),
            required=schema_def.get('required', []),
            description=schema_def.get('description', '')
        )

    def _generate_fastapi(self) -> GeneratedBackend:
        """Generate FastAPI application"""
        # Generate models (Pydantic)
        models = self._generate_fastapi_models()

        # Generate routes
        routes = self._generate_fastapi_routes()

        # Generate main app
        main_app = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .models import *

app = FastAPI(
    title="''' + self.api_info.get('title', 'API') + '''",
    description="''' + self.api_info.get('description', '') + '''",
    version="''' + self.api_info.get('version', '1.0.0') + '''"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
'''

        requirements = [
            'fastapi>=0.100.0',
            'uvicorn[standard]>=0.23.0',
            'pydantic>=2.0.0',
            'pydantic-settings>=2.0.0'
        ]

        return GeneratedBackend(
            framework=BackendFramework.FASTAPI,
            routes=routes,
            models=models,
            controllers=main_app,
            requirements=requirements,
            project_structure={
                'app/main.py': main_app,
                'app/routes.py': routes,
                'app/models.py': models
            }
        )

    def _generate_fastapi_models(self) -> str:
        """Generate Pydantic models"""
        code = '''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

'''

        for schema in self.schemas:
            code += f'''
class {schema.name}(BaseModel):
    """
    {schema.description}
    """
'''
            for prop_name, prop_def in schema.properties.items():
                prop_type = self._python_type(prop_def)
                is_required = prop_name in schema.required

                if is_required:
                    code += f'    {prop_name}: {prop_type}\n'
                else:
                    code += f'    {prop_name}: Optional[{prop_type}] = None\n'

            code += '\n'

        return code

    def _generate_fastapi_routes(self) -> str:
        """Generate FastAPI routes"""
        code = '''from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from .models import *

router = APIRouter()

'''

        for endpoint in self.endpoints:
            # Generate route decorator
            code += f"@router.{endpoint.method.value}('{endpoint.path}'"

            # Add response model if specified
            response_schema = self._get_response_schema(endpoint)
            if response_schema:
                code += f", response_model={response_schema}"

            code += ")\n"

            # Generate function
            func_name = endpoint.operation_id or self._generate_func_name(endpoint)
            params = self._generate_fastapi_params(endpoint)

            code += f"async def {func_name}({params}):\n"
            code += f'    """\n    {endpoint.summary}\n'
            if endpoint.description:
                code += f'    \n    {endpoint.description}\n'
            code += '    """\n'

            # Generate function body
            if endpoint.method == HTTPMethod.GET:
                code += '    # TODO: Implement GET logic\n'
                code += '    return {"message": "Not implemented"}\n'
            elif endpoint.method == HTTPMethod.POST:
                code += '    # TODO: Implement POST logic\n'
                code += '    return {"message": "Created successfully"}\n'
            elif endpoint.method == HTTPMethod.PUT:
                code += '    # TODO: Implement PUT logic\n'
                code += '    return {"message": "Updated successfully"}\n'
            elif endpoint.method == HTTPMethod.DELETE:
                code += '    # TODO: Implement DELETE logic\n'
                code += '    return {"message": "Deleted successfully"}\n'

            code += '\n'

        return code

    def _generate_express(self) -> GeneratedBackend:
        """Generate Express.js application"""
        # Generate models (Mongoose/TypeORM)
        models = self._generate_express_models()

        # Generate routes
        routes = self._generate_express_routes()

        # Generate main app
        main_app = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';

import routes from './routes';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', routes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export default app;
'''

        requirements = [
            'express@^4.18.0',
            'cors@^2.8.5',
            'helmet@^7.0.0',
            'dotenv@^16.0.0',
            '@types/express@^4.17.17',
            '@types/cors@^2.8.13',
            'typescript@^5.0.0'
        ]

        return GeneratedBackend(
            framework=BackendFramework.EXPRESS,
            routes=routes,
            models=models,
            controllers=main_app,
            requirements=requirements,
            project_structure={
                'src/app.ts': main_app,
                'src/routes.ts': routes,
                'src/models.ts': models
            }
        )

    def _generate_express_models(self) -> str:
        """Generate TypeScript models"""
        code = '''export interface Model {
  // Base model interface
}

'''

        for schema in self.schemas:
            code += f'''export interface {schema.name} {{
'''
            for prop_name, prop_def in schema.properties.items():
                ts_type = self._typescript_type(prop_def)
                is_optional = prop_name not in schema.required

                code += f'  {prop_name}{"?" if is_optional else ""}: {ts_type};\n'

            code += '}\n\n'

        return code

    def _generate_express_routes(self) -> str:
        """Generate Express routes"""
        code = '''import { Router, Request, Response } from 'express';

const router = Router();

'''

        for endpoint in self.endpoints:
            func_name = endpoint.operation_id or self._generate_func_name(endpoint)

            code += f"router.{endpoint.method.value}('{endpoint.path}', async (req: Request, res: Response) => {{\n"
            code += f'  // {endpoint.summary}\n'
            code += '  try {\n'
            code += '    // TODO: Implement logic\n'
            code += '    res.json({ message: "Not implemented" });\n'
            code += '  } catch (error) {\n'
            code += '    res.status(500).json({ error: "Internal server error" });\n'
            code += '  }\n'
            code += '});\n\n'

        code += 'export default router;\n'

        return code

    def _generate_spring_boot(self) -> GeneratedBackend:
        """Generate Spring Boot application"""
        models = self._generate_spring_models()
        controllers = self._generate_spring_controllers()

        requirements = [
            'spring-boot-starter-web',
            'spring-boot-starter-data-jpa',
            'spring-boot-starter-validation',
            'lombok'
        ]

        return GeneratedBackend(
            framework=BackendFramework.SPRING_BOOT,
            routes=controllers,
            models=models,
            requirements=requirements
        )

    def _generate_spring_models(self) -> str:
        """Generate Spring/JPA entities"""
        code = '''package com.example.api.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import javax.persistence.*;
import javax.validation.constraints.*;
import java.time.LocalDateTime;

'''

        for schema in self.schemas:
            code += f'''
@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "{schema.name.lower()}s")
public class {schema.name} {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

'''
            for prop_name, prop_def in schema.properties.items():
                java_type = self._java_type(prop_def)
                is_required = prop_name in schema.required

                if is_required:
                    code += '    @NotNull\n'

                code += f'    private {java_type} {prop_name};\n'

            code += '}\n'

        return code

    def _generate_spring_controllers(self) -> str:
        """Generate Spring REST controllers"""
        code = '''package com.example.api.controller;

import com.example.api.model.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api")
public class ApiController {

'''

        for endpoint in self.endpoints:
            func_name = self._camel_case(endpoint.operation_id or self._generate_func_name(endpoint))

            # Spring annotation
            annotation = f'@{endpoint.method.value.capitalize()}Mapping("{endpoint.path}")'
            code += f'    {annotation}\n'

            # Method signature
            code += f'    public ResponseEntity<?> {func_name}() {{\n'
            code += f'        // {endpoint.summary}\n'
            code += '        // TODO: Implement logic\n'
            code += '        return ResponseEntity.ok("Not implemented");\n'
            code += '    }\n\n'

        code += '}\n'

        return code

    def _generate_django(self) -> GeneratedBackend:
        """Generate Django application"""
        models = '''from django.db import models

# Django models here
'''

        views = '''from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Django views here
'''

        return GeneratedBackend(
            framework=BackendFramework.DJANGO,
            routes=views,
            models=models,
            requirements=['django>=4.2', 'djangorestframework>=3.14']
        )

    def _generate_fastapi_params(self, endpoint: APIEndpoint) -> str:
        """Generate FastAPI function parameters"""
        params = []

        # Path parameters
        for param in endpoint.parameters:
            if param.get('in') == 'path':
                param_type = self._python_type(param.get('schema', {}))
                params.append(f"{param['name']}: {param_type}")

        # Query parameters
        for param in endpoint.parameters:
            if param.get('in') == 'query':
                param_type = self._python_type(param.get('schema', {}))
                if param.get('required', False):
                    params.append(f"{param['name']}: {param_type}")
                else:
                    params.append(f"{param['name']}: Optional[{param_type}] = None")

        # Request body
        if endpoint.request_body:
            content = endpoint.request_body.get('content', {})
            if 'application/json' in content:
                schema_ref = content['application/json'].get('schema', {}).get('$ref', '')
                if schema_ref:
                    model_name = schema_ref.split('/')[-1]
                    params.append(f"body: {model_name}")

        return ', '.join(params) if params else ''

    def _get_response_schema(self, endpoint: APIEndpoint) -> Optional[str]:
        """Get response model from endpoint"""
        response_200 = endpoint.responses.get('200', {})
        content = response_200.get('content', {})

        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            if '$ref' in schema:
                return schema['$ref'].split('/')[-1]

        return None

    def _python_type(self, schema: Dict) -> str:
        """Convert OpenAPI type to Python type"""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict'
        }

        schema_type = schema.get('type', 'string')
        return type_map.get(schema_type, 'str')

    def _typescript_type(self, schema: Dict) -> str:
        """Convert OpenAPI type to TypeScript type"""
        type_map = {
            'string': 'string',
            'integer': 'number',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'Array<any>',
            'object': 'object'
        }

        schema_type = schema.get('type', 'string')
        return type_map.get(schema_type, 'string')

    def _java_type(self, schema: Dict) -> str:
        """Convert OpenAPI type to Java type"""
        type_map = {
            'string': 'String',
            'integer': 'Integer',
            'number': 'Double',
            'boolean': 'Boolean',
            'array': 'List',
            'object': 'Object'
        }

        schema_type = schema.get('type', 'string')
        return type_map.get(schema_type, 'String')

    def _generate_func_name(self, endpoint: APIEndpoint) -> str:
        """Generate function name from endpoint"""
        # Remove special chars from path
        path_parts = [p for p in endpoint.path.split('/') if p and not p.startswith('{')]
        name = '_'.join(path_parts)
        return f"{endpoint.method.value}_{name}"

    def _camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
