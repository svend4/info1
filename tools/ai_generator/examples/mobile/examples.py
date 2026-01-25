#!/usr/bin/env python3
"""
Mobile Development Examples - React Native, SwiftUI, Jetpack Compose, Flutter, KMP
"""

from pathlib import Path
from tools.ai_generator.mobile import (
    ReactNativeGenerator, AppConfig, StateManagement,
    SwiftUIGenerator,
    JetpackComposeGenerator,
    FlutterGenerator,
    KotlinMultiplatformGenerator
)


def example_react_native_app():
    """Generate React Native app"""
    print("=" * 60)
    print("React Native App Generation")
    print("=" * 60)

    config = AppConfig(
        app_name="TaskMaster",
        bundle_id="com.example.taskmaster",
        state_management=StateManagement.REDUX
    )

    generator = ReactNativeGenerator(config)
    files = generator.generate(Path("./output/taskmaster-rn"))

    print(f"✅ Generated React Native app")
    print(f"   App: TaskMaster")
    print(f"   State: Redux")
    print(f"   Files: {len(files)}")
    print()


def example_swiftui_app():
    """Generate SwiftUI iOS app"""
    print("=" * 60)
    print("SwiftUI App Generation")
    print("=" * 60)

    generator = SwiftUIGenerator()

    files = generator.generate(
        app_name="FitnessTracker",
        architecture="MVVM",
        enable_combine=True,
        output_dir=Path("./output/fitness-ios")
    )

    print(f"✅ Generated SwiftUI app")
    print(f"   App: FitnessTracker")
    print(f"   Architecture: MVVM + Combine")
    print(f"   Files: {len(files)}")
    print()


def example_jetpack_compose_app():
    """Generate Jetpack Compose Android app"""
    print("=" * 60)
    print("Jetpack Compose App Generation")
    print("=" * 60)

    generator = JetpackComposeGenerator()

    files = generator.generate(
        app_name="ShoppingApp",
        package_name="com.example.shopping",
        di_framework="hilt",
        output_dir=Path("./output/shopping-android")
    )

    print(f"✅ Generated Jetpack Compose app")
    print(f"   App: ShoppingApp")
    print(f"   DI: Hilt")
    print(f"   Files: {len(files)}")
    print()


def example_flutter_app():
    """Generate Flutter app"""
    print("=" * 60)
    print("Flutter App Generation")
    print("=" * 60)

    generator = FlutterGenerator()

    files = generator.generate(
        app_name="weather_app",
        state_management="bloc",
        enable_navigation=True,
        output_dir=Path("./output/weather-flutter")
    )

    print(f"✅ Generated Flutter app")
    print(f"   App: weather_app")
    print(f"   State: BLoC")
    print(f"   Files: {len(files)}")
    print()


def example_kotlin_multiplatform():
    """Generate Kotlin Multiplatform project"""
    print("=" * 60)
    print("Kotlin Multiplatform Generation")
    print("=" * 60)

    generator = KotlinMultiplatformGenerator()

    files = generator.generate(
        project_name="SharedLogic",
        platforms=["android", "ios"],
        shared_modules=["network", "database", "domain"],
        output_dir=Path("./output/kmp-shared")
    )

    print(f"✅ Generated KMP project")
    print(f"   Platforms: Android, iOS")
    print(f"   Modules: network, database, domain")
    print(f"   Files: {len(files)}")
    print()


if __name__ == "__main__":
    print("\n📱 Mobile Development Examples\n")
    example_react_native_app()
    example_swiftui_app()
    example_jetpack_compose_app()
    example_flutter_app()
    example_kotlin_multiplatform()
    print("✅ All mobile development examples completed!\n")
