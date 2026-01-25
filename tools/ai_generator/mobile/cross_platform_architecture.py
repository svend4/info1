#!/usr/bin/env python3
"""
Cross-Platform Architecture Generator

Unified architecture для React Native, Flutter, SwiftUI, и Jetpack Compose с shared business logic.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class Platform(Enum):
    """Target Platform"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"
    ALL = "all"


class SharedCodeStrategy(Enum):
    """Shared Code Strategy"""
    KOTLIN_MULTIPLATFORM = "kmp"  # Kotlin Multiplatform
    CAPACITOR = "capacitor"  # Web-based with native bridges
    FFI = "ffi"  # Foreign Function Interface (Rust/C++)
    REST_API = "rest"  # Shared via REST API


class Architecture(Enum):
    """Architecture Pattern"""
    CLEAN = "clean"
    HEXAGONAL = "hexagonal"
    ONION = "onion"
    MODULAR = "modular"


@dataclass
class SharedModule:
    """Shared Module Specification"""
    name: str
    language: str  # kotlin, dart, rust, typescript
    platforms: List[Platform] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class FeatureModule:
    """Feature Module Specification"""
    name: str
    layers: List[str] = field(default_factory=list)  # domain, data, presentation
    shared_logic: bool = True
    platform_specific: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossPlatformConfig:
    """Cross-Platform Configuration"""
    project_name: str
    platforms: List[Platform] = field(default_factory=list)
    shared_strategy: SharedCodeStrategy = SharedCodeStrategy.REST_API
    architecture: Architecture = Architecture.CLEAN
    features: List[FeatureModule] = field(default_factory=list)


class CrossPlatformArchitectureGenerator:
    """Cross-Platform Architecture Generator"""

    def __init__(self, config: CrossPlatformConfig):
        """
        Инициализация cross-platform generator

        Args:
            config: Cross-platform configuration
        """
        self.config = config
        self.shared_modules: List[SharedModule] = []

    def add_shared_module(self, module: SharedModule):
        """
        Add shared module

        Args:
            module: Shared module specification
        """
        self.shared_modules.append(module)
        print(f"🌐 Added shared module: {module.name}")

    def generate_architecture(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete cross-platform architecture

        Args:
            output_dir: Output directory path

        Returns:
            Dictionary of generated files
        """
        print(f"🚀 Generating cross-platform architecture: {self.config.project_name}")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate monorepo structure
        files['README.md'] = self._generate_readme()
        files['package.json'] = self._generate_root_package_json()

        # Generate shared modules
        if self.config.shared_strategy == SharedCodeStrategy.KOTLIN_MULTIPLATFORM:
            files.update(self._generate_kmp_modules(output_dir))
        elif self.config.shared_strategy == SharedCodeStrategy.CAPACITOR:
            files.update(self._generate_capacitor_modules(output_dir))
        elif self.config.shared_strategy == SharedCodeStrategy.FFI:
            files.update(self._generate_ffi_modules(output_dir))

        # Generate platform-specific projects
        for platform in self.config.platforms:
            if platform == Platform.IOS:
                files.update(self._generate_ios_wrapper(output_dir))
            elif platform == Platform.ANDROID:
                files.update(self._generate_android_wrapper(output_dir))
            elif platform == Platform.WEB:
                files.update(self._generate_web_wrapper(output_dir))

        # Generate clean architecture layers
        files.update(self._generate_domain_layer(output_dir))
        files.update(self._generate_data_layer(output_dir))
        files.update(self._generate_presentation_layer(output_dir))

        # Generate CI/CD
        files['.github/workflows/ci.yml'] = self._generate_github_actions()

        # Generate documentation
        files['docs/ARCHITECTURE.md'] = self._generate_architecture_doc()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} files")
        return files

    def _generate_readme(self) -> str:
        """Generate README"""
        platforms_list = ', '.join([p.value for p in self.config.platforms])

        return f"""# {self.config.project_name}

Cross-platform mobile application with {self.config.architecture.value} architecture.

## Platforms

{platforms_list}

## Architecture

This project follows **{self.config.architecture.value.upper()} Architecture** with the following layers:

```
├── domain/           # Business logic (platform-agnostic)
│   ├── entities/
│   ├── usecases/
│   └── repositories/
├── data/             # Data layer
│   ├── models/
│   ├── repositories/
│   └── datasources/
└── presentation/     # UI layer (platform-specific)
    ├── ios/
    ├── android/
    └── web/
```

## Shared Code Strategy

**{self.config.shared_strategy.value.upper()}**: Sharing business logic across platforms.

## Getting Started

### Prerequisites

- Node.js 18+
- Xcode (for iOS)
- Android Studio (for Android)
- Flutter/Dart SDK (if using Flutter)

### Installation

```bash
# Install dependencies
npm install

# Run iOS
npm run ios

# Run Android
npm run android

# Run Web
npm run web
```

## Project Structure

```
{self.config.project_name}/
├── shared/           # Shared business logic
├── platforms/
│   ├── ios/
│   ├── android/
│   └── web/
├── docs/
└── scripts/
```

## Testing

```bash
# Run all tests
npm test

# Platform-specific tests
npm run test:ios
npm run test:android
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT
"""

    def _generate_root_package_json(self) -> str:
        """Generate root package.json for monorepo"""
        return json.dumps({
            "name": self.config.project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "workspaces": [
                "packages/*",
                "platforms/*"
            ],
            "scripts": {
                "ios": "cd platforms/ios && npm run ios",
                "android": "cd platforms/android && npm run android",
                "web": "cd platforms/web && npm start",
                "test": "npm run test --workspaces",
                "lint": "eslint . --ext .ts,.tsx",
                "build": "npm run build --workspaces"
            },
            "devDependencies": {
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "eslint": "^8.50.0",
                "prettier": "^3.0.0",
                "typescript": "^5.2.0"
            }
        }, indent=2)

    def _generate_kmp_modules(self, output_dir: Path) -> Dict[str, str]:
        """Generate Kotlin Multiplatform modules"""
        files = {}

        # Build gradle for KMP
        files['shared/build.gradle.kts'] = """plugins {
    kotlin("multiplatform") version "1.9.20"
    kotlin("plugin.serialization") version "1.9.20"
}

kotlin {
    ios()
    android()

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("androidx.core:core-ktx:1.12.0")
            }
        }

        val iosMain by getting {
            dependencies {
                // iOS-specific dependencies
            }
        }
    }
}
"""

        # Shared domain models
        files['shared/src/commonMain/kotlin/domain/User.kt'] = """package domain

import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String? = null
)
"""

        # Shared repository interface
        files['shared/src/commonMain/kotlin/domain/UserRepository.kt'] = """package domain

interface UserRepository {
    suspend fun getUser(userId: String): Result<User>
    suspend fun updateUser(user: User): Result<User>
}
"""

        # Platform-specific implementations
        files['shared/src/androidMain/kotlin/data/AndroidUserRepository.kt'] = """package data

import domain.User
import domain.UserRepository

class AndroidUserRepository : UserRepository {
    override suspend fun getUser(userId: String): Result<User> {
        // Android-specific implementation
        return Result.success(User("1", "Android User", "user@android.com"))
    }

    override suspend fun updateUser(user: User): Result<User> {
        return Result.success(user)
    }
}
"""

        files['shared/src/iosMain/kotlin/data/IOSUserRepository.kt'] = """package data

import domain.User
import domain.UserRepository

class IOSUserRepository : UserRepository {
    override suspend fun getUser(userId: String): Result<User> {
        // iOS-specific implementation
        return Result.success(User("1", "iOS User", "user@ios.com"))
    }

    override suspend fun updateUser(user: User): Result<User> {
        return Result.success(user)
    }
}
"""

        return files

    def _generate_capacitor_modules(self, output_dir: Path) -> Dict[str, str]:
        """Generate Capacitor modules"""
        files = {}

        files['capacitor.config.ts'] = f"""import {{ CapacitorConfig }} from '@capacitor/cli';

const config: CapacitorConfig = {{
  appId: 'com.{self.config.project_name.lower()}.app',
  appName: '{self.config.project_name}',
  webDir: 'dist',
  server: {{
    androidScheme: 'https'
  }}
}};

export default config;
"""

        files['shared/src/bridge/NativeBridge.ts'] = """import { Plugins } from '@capacitor/core';

export class NativeBridge {
  static async getUserLocation(): Promise<{ lat: number; lng: number }> {
    const { Geolocation } = Plugins;
    const position = await Geolocation.getCurrentPosition();
    return {
      lat: position.coords.latitude,
      lng: position.coords.longitude
    };
  }

  static async saveToStorage(key: string, value: any): Promise<void> {
    const { Storage } = Plugins;
    await Storage.set({ key, value: JSON.stringify(value) });
  }

  static async getFromStorage(key: string): Promise<any> {
    const { Storage } = Plugins;
    const { value } = await Storage.get({ key });
    return value ? JSON.parse(value) : null;
  }
}
"""

        return files

    def _generate_ffi_modules(self, output_dir: Path) -> Dict[str, str]:
        """Generate FFI (Rust) modules"""
        files = {}

        files['shared/Cargo.toml'] = f"""[package]
name = "{self.config.project_name.lower()}_shared"
version = "1.0.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "staticlib"]

[dependencies]
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
"""

        files['shared/src/lib.rs'] = """use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
}

#[no_mangle]
pub extern "C" fn create_user(
    id: *const libc::c_char,
    name: *const libc::c_char,
    email: *const libc::c_char,
) -> *mut User {
    let id = unsafe { std::ffi::CStr::from_ptr(id).to_str().unwrap() };
    let name = unsafe { std::ffi::CStr::from_ptr(name).to_str().unwrap() };
    let email = unsafe { std::ffi::CStr::from_ptr(email).to_str().unwrap() };

    Box::into_raw(Box::new(User {
        id: id.to_string(),
        name: name.to_string(),
        email: email.to_string(),
    }))
}

#[no_mangle]
pub extern "C" fn free_user(ptr: *mut User) {
    if !ptr.is_null() {
        unsafe { Box::from_raw(ptr) };
    }
}
"""

        return files

    def _generate_ios_wrapper(self, output_dir: Path) -> Dict[str, str]:
        """Generate iOS platform wrapper"""
        files = {}

        files['platforms/ios/Podfile'] = """platform :ios, '14.0'

target 'App' do
  use_frameworks!

  # Shared module
  pod 'SharedModule', :path => '../../shared'

  # Dependencies
  pod 'Alamofire', '~> 5.8'
  pod 'SwiftyJSON', '~> 5.0'
end
"""

        files['platforms/ios/AppDelegate.swift'] = """import UIKit
import SharedModule

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        // Initialize shared module
        SharedModule.initialize()
        return true
    }
}
"""

        return files

    def _generate_android_wrapper(self, output_dir: Path) -> Dict[str, str]:
        """Generate Android platform wrapper"""
        files = {}

        files['platforms/android/app/build.gradle'] = """plugins {
    id 'com.android.application'
    id 'kotlin-android'
}

android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.app"
        minSdk 24
        targetSdk 34
    }
}

dependencies {
    implementation project(':shared')
    implementation 'androidx.core:core-ktx:1.12.0'
}
"""

        files['platforms/android/settings.gradle'] = """include ':app'
include ':shared'
project(':shared').projectDir = new File(rootProject.projectDir, '../../shared')
"""

        return files

    def _generate_web_wrapper(self, output_dir: Path) -> Dict[str, str]:
        """Generate web platform wrapper"""
        files = {}

        files['platforms/web/package.json'] = json.dumps({
            "name": f"{self.config.project_name}-web",
            "version": "1.0.0",
            "scripts": {
                "start": "vite",
                "build": "vite build"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "shared-module": "file:../../shared"
            },
            "devDependencies": {
                "vite": "^5.0.0",
                "@vitejs/plugin-react": "^4.2.0"
            }
        }, indent=2)

        files['platforms/web/src/main.tsx'] = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

        return files

    def _generate_domain_layer(self, output_dir: Path) -> Dict[str, str]:
        """Generate domain layer (Clean Architecture)"""
        files = {}

        files['shared/domain/entities/User.ts'] = """export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}
"""

        files['shared/domain/usecases/GetUser.ts'] = """import { User } from '../entities/User';
import { UserRepository } from '../repositories/UserRepository';

export class GetUser {
  constructor(private repository: UserRepository) {}

  async execute(userId: string): Promise<User> {
    return await this.repository.getUser(userId);
  }
}
"""

        files['shared/domain/repositories/UserRepository.ts'] = """import { User } from '../entities/User';

export interface UserRepository {
  getUser(userId: string): Promise<User>;
  updateUser(user: User): Promise<User>;
}
"""

        return files

    def _generate_data_layer(self, output_dir: Path) -> Dict[str, str]:
        """Generate data layer"""
        files = {}

        files['shared/data/repositories/UserRepositoryImpl.ts'] = """import { User } from '../../domain/entities/User';
import { UserRepository } from '../../domain/repositories/UserRepository';
import { ApiDataSource } from '../datasources/ApiDataSource';

export class UserRepositoryImpl implements UserRepository {
  constructor(private apiDataSource: ApiDataSource) {}

  async getUser(userId: string): Promise<User> {
    return await this.apiDataSource.fetchUser(userId);
  }

  async updateUser(user: User): Promise<User> {
    return await this.apiDataSource.updateUser(user);
  }
}
"""

        files['shared/data/datasources/ApiDataSource.ts'] = """import { User } from '../../domain/entities/User';

export class ApiDataSource {
  private baseUrl = 'https://api.example.com';

  async fetchUser(userId: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/${userId}`);
    return await response.json();
  }

  async updateUser(user: User): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/${user.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user)
    });
    return await response.json();
  }
}
"""

        return files

    def _generate_presentation_layer(self, output_dir: Path) -> Dict[str, str]:
        """Generate presentation layer"""
        files = {}

        files['shared/presentation/viewmodels/UserViewModel.ts'] = """import { GetUser } from '../../domain/usecases/GetUser';
import { User } from '../../domain/entities/User';

export class UserViewModel {
  private user: User | null = null;
  private isLoading = false;
  private error: string | null = null;

  constructor(private getUser: GetUser) {}

  async loadUser(userId: string): Promise<void> {
    this.isLoading = true;
    this.error = null;

    try {
      this.user = await this.getUser.execute(userId);
    } catch (e) {
      this.error = (e as Error).message;
    } finally {
      this.isLoading = false;
    }
  }

  getUser(): User | null {
    return this.user;
  }

  isUserLoading(): boolean {
    return this.isLoading;
  }

  getError(): string | null {
    return this.error;
  }
}
"""

        return files

    def _generate_github_actions(self) -> str:
        """Generate GitHub Actions CI/CD"""
        platforms_jobs = []

        if Platform.IOS in self.config.platforms:
            platforms_jobs.append("""  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build iOS
        run: |
          cd platforms/ios
          xcodebuild -workspace App.xcworkspace -scheme App -sdk iphoneos""")

        if Platform.ANDROID in self.config.platforms:
            platforms_jobs.append("""  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'adopt'
      - name: Build Android
        run: |
          cd platforms/android
          ./gradlew assembleDebug""")

        if Platform.WEB in self.config.platforms:
            platforms_jobs.append("""  build-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Build Web
        run: |
          npm install
          npm run build:web""")

        return f"""name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
      - name: Run linter
        run: npm run lint

{chr(10).join(platforms_jobs)}
"""

    def _generate_architecture_doc(self) -> str:
        """Generate architecture documentation"""
        return f"""# {self.config.project_name} Architecture

## Overview

This project implements **{self.config.architecture.value.upper()} Architecture** with cross-platform capabilities.

## Architecture Layers

### 1. Domain Layer (Business Logic)

Platform-agnostic business logic:

- **Entities**: Core business models
- **Use Cases**: Business operations
- **Repository Interfaces**: Data access contracts

### 2. Data Layer

Data management and API integration:

- **Repository Implementations**: Concrete data access
- **Data Sources**: API clients, local storage
- **Models**: Data transfer objects

### 3. Presentation Layer

Platform-specific UI implementations:

- **ViewModels**: Presentation logic
- **Views**: UI components (SwiftUI, Jetpack Compose, React Native)
- **State Management**: Platform-specific state handling

## Shared Code Strategy

**{self.config.shared_strategy.value.upper()}**

{self._get_strategy_description()}

## Dependency Flow

```
Presentation → Domain ← Data
```

Dependencies flow **inward** - outer layers depend on inner layers, never the reverse.

## Platform-Specific Code

Each platform has its own directory:

- `platforms/ios/` - SwiftUI implementation
- `platforms/android/` - Jetpack Compose implementation
- `platforms/web/` - React implementation

## Testing Strategy

- **Unit Tests**: Domain layer (use cases, entities)
- **Integration Tests**: Data layer (repositories, API clients)
- **UI Tests**: Presentation layer (platform-specific)

## Build Process

1. Build shared modules
2. Generate platform-specific bindings
3. Build each platform application
4. Run tests
5. Package for distribution

## Continuous Integration

See `.github/workflows/ci.yml` for CI/CD configuration.
"""

    def _get_strategy_description(self) -> str:
        """Get description for shared code strategy"""
        descriptions = {
            SharedCodeStrategy.KOTLIN_MULTIPLATFORM:
                "Using **Kotlin Multiplatform Mobile (KMM)** to share business logic between iOS and Android. "
                "Domain and data layers are written in Kotlin and compiled to native code for each platform.",

            SharedCodeStrategy.CAPACITOR:
                "Using **Capacitor** to wrap web application with native capabilities. "
                "Business logic is written in TypeScript and shared across all platforms via JavaScript bridge.",

            SharedCodeStrategy.FFI:
                "Using **Foreign Function Interface (FFI)** with Rust/C++ core. "
                "High-performance business logic compiled to native libraries and accessed from each platform.",

            SharedCodeStrategy.REST_API:
                "Using **REST API** as shared business logic layer. "
                "All business logic resides in backend services, platforms only implement UI and local state."
        }
        return descriptions.get(self.config.shared_strategy, "")
