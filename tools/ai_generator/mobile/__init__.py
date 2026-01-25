"""
Advanced Mobile Development Package

React Native, SwiftUI, Jetpack Compose, Flutter, и cross-platform architecture.
"""

from .react_native_generator import (
    ReactNativeGenerator,
    ComponentSpec,
    ScreenSpec,
    AppConfig,
    NavigationType,
    StateManagement,
    UILibrary
)

from .swiftui_generator import (
    SwiftUIGenerator,
    ViewSpec,
    ViewModelSpec,
    SwiftUIAppConfig,
    ArchitecturePattern,
    DataPersistence,
    NetworkLayer
)

from .jetpack_compose_generator import (
    JetpackComposeGenerator,
    ComposableSpec,
    ViewModelKtSpec,
    ComposeAppConfig,
    AndroidArchitecture,
    DependencyInjection,
    Database
)

from .flutter_integration import (
    FlutterGenerator,
    WidgetSpec,
    BlocSpec,
    FlutterAppConfig,
    StateManagementFlutter,
    RouterType
)

from .cross_platform_architecture import (
    CrossPlatformArchitectureGenerator,
    SharedModule,
    FeatureModule,
    CrossPlatformConfig,
    Platform,
    SharedCodeStrategy,
    Architecture
)

__all__ = [
    # React Native Generator
    'ReactNativeGenerator',
    'ComponentSpec',
    'ScreenSpec',
    'AppConfig',
    'NavigationType',
    'StateManagement',
    'UILibrary',

    # SwiftUI Generator
    'SwiftUIGenerator',
    'ViewSpec',
    'ViewModelSpec',
    'SwiftUIAppConfig',
    'ArchitecturePattern',
    'DataPersistence',
    'NetworkLayer',

    # Jetpack Compose Generator
    'JetpackComposeGenerator',
    'ComposableSpec',
    'ViewModelKtSpec',
    'ComposeAppConfig',
    'AndroidArchitecture',
    'DependencyInjection',
    'Database',

    # Flutter Integration
    'FlutterGenerator',
    'WidgetSpec',
    'BlocSpec',
    'FlutterAppConfig',
    'StateManagementFlutter',
    'RouterType',

    # Cross-Platform Architecture
    'CrossPlatformArchitectureGenerator',
    'SharedModule',
    'FeatureModule',
    'CrossPlatformConfig',
    'Platform',
    'SharedCodeStrategy',
    'Architecture'
]

__version__ = '1.0.0'
