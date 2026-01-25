#!/usr/bin/env python3
"""
Jetpack Compose Generator

Автоматическая генерация Android приложений с Jetpack Compose, MVVM, и Kotlin Coroutines.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class AndroidArchitecture(Enum):
    """Architecture Pattern"""
    MVVM = "mvvm"
    MVI = "mvi"
    CLEAN = "clean"


class DependencyInjection(Enum):
    """Dependency Injection Framework"""
    HILT = "hilt"
    KOIN = "koin"
    DAGGER = "dagger"


class Database(Enum):
    """Database Solution"""
    ROOM = "room"
    REALM = "realm"
    SQLDELIGHT = "sqldelight"


@dataclass
class ComposableSpec:
    """Jetpack Compose Composable Specification"""
    name: str
    type: str  # screen, component
    parameters: List[Dict[str, str]] = field(default_factory=list)
    state: List[Dict[str, str]] = field(default_factory=list)
    events: List[str] = field(default_factory=list)


@dataclass
class ViewModelKtSpec:
    """Android ViewModel Specification"""
    name: str
    state_properties: List[Dict[str, str]] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)


@dataclass
class ComposeAppConfig:
    """Jetpack Compose App Configuration"""
    name: str
    package_name: str
    version: str = "1.0.0"
    min_sdk: int = 24
    target_sdk: int = 34
    architecture: AndroidArchitecture = AndroidArchitecture.MVVM
    di_framework: DependencyInjection = DependencyInjection.HILT
    database: Optional[Database] = None
    features: List[str] = field(default_factory=list)


class JetpackComposeGenerator:
    """Jetpack Compose Application Generator"""

    def __init__(self, config: ComposeAppConfig):
        """
        Инициализация Jetpack Compose generator

        Args:
            config: Application configuration
        """
        self.config = config
        self.composables: List[ComposableSpec] = []
        self.viewmodels: List[ViewModelKtSpec] = []

    def add_screen(self, composable: ComposableSpec, viewmodel: Optional[ViewModelKtSpec] = None):
        """
        Add screen to application

        Args:
            composable: Composable specification
            viewmodel: Optional ViewModel specification
        """
        self.composables.append(composable)
        if viewmodel:
            self.viewmodels.append(viewmodel)
        print(f"🤖 Added screen: {composable.name}")

    def generate_project(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete Jetpack Compose project

        Args:
            output_dir: Output directory path

        Returns:
            Dictionary of generated files
        """
        print(f"🚀 Generating Jetpack Compose project: {self.config.name}")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        package_path = self.config.package_name.replace('.', '/')

        # Generate Gradle files
        files['build.gradle.kts'] = self._generate_root_gradle()
        files['app/build.gradle.kts'] = self._generate_app_gradle()
        files['settings.gradle.kts'] = self._generate_settings_gradle()

        # Generate app entry point
        files[f'app/src/main/java/{package_path}/MainActivity.kt'] = self._generate_main_activity()
        files[f'app/src/main/java/{package_path}/App.kt'] = self._generate_app()

        # Generate composables
        for comp in self.composables:
            files[f'app/src/main/java/{package_path}/ui/screens/{comp.name}.kt'] = \
                self._generate_composable(comp)

        # Generate ViewModels
        for vm in self.viewmodels:
            files[f'app/src/main/java/{package_path}/ui/viewmodels/{vm.name}.kt'] = \
                self._generate_viewmodel(vm)

        # Generate navigation
        files[f'app/src/main/java/{package_path}/navigation/Navigation.kt'] = \
            self._generate_navigation()

        # Generate data layer
        files[f'app/src/main/java/{package_path}/data/models/User.kt'] = \
            self._generate_user_model()
        files[f'app/src/main/java/{package_path}/data/repository/UserRepository.kt'] = \
            self._generate_repository()
        files[f'app/src/main/java/{package_path}/data/remote/ApiService.kt'] = \
            self._generate_api_service()

        # Generate DI
        if self.config.di_framework == DependencyInjection.HILT:
            files[f'app/src/main/java/{package_path}/di/AppModule.kt'] = \
                self._generate_hilt_module()

        # Generate database
        if self.config.database == Database.ROOM:
            files[f'app/src/main/java/{package_path}/data/local/AppDatabase.kt'] = \
                self._generate_room_database()

        # Generate utilities
        files[f'app/src/main/java/{package_path}/utils/Extensions.kt'] = \
            self._generate_extensions()
        files[f'app/src/main/java/{package_path}/ui/theme/Theme.kt'] = \
            self._generate_theme()
        files[f'app/src/main/java/{package_path}/ui/theme/Color.kt'] = \
            self._generate_colors()

        # Generate manifest
        files['app/src/main/AndroidManifest.xml'] = self._generate_manifest()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} files")
        return files

    def _generate_root_gradle(self) -> str:
        """Generate root build.gradle.kts"""
        return """plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false
}
"""

    def _generate_app_gradle(self) -> str:
        """Generate app build.gradle.kts"""
        hilt_deps = ""
        room_deps = ""

        if self.config.di_framework == DependencyInjection.HILT:
            hilt_deps = '''
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")'''

        if self.config.database == Database.ROOM:
            room_deps = '''
    implementation("androidx.room:room-runtime:2.6.0")
    implementation("androidx.room:room-ktx:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")'''

        return f"""plugins {{
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("kotlin-kapt")
}}

android {{
    namespace = "{self.config.package_name}"
    compileSdk = {self.config.target_sdk}

    defaultConfig {{
        applicationId = "{self.config.package_name}"
        minSdk = {self.config.min_sdk}
        targetSdk = {self.config.target_sdk}
        versionCode = 1
        versionName = "{self.config.version}"

        vectorDrawables {{
            useSupportLibrary = true
        }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}

    kotlinOptions {{
        jvmTarget = "17"
    }}

    buildFeatures {{
        compose = true
    }}

    composeOptions {{
        kotlinCompilerExtensionVersion = "1.5.4"
    }}

    packaging {{
        resources {{
            excludes += "/META-INF/{{AL2.0,LGPL2.1}}"
        }}
    }}
}}

dependencies {{
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")

    // Android Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.activity:activity-compose:1.8.1")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.5")

    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.6.2")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
{hilt_deps}
{room_deps}

    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}}
"""

    def _generate_settings_gradle(self) -> str:
        """Generate settings.gradle.kts"""
        return f"""pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{self.config.name}"
include(":app")
"""

    def _generate_main_activity(self) -> str:
        """Generate MainActivity"""
        hilt_annotation = "@AndroidEntryPoint\n" if self.config.di_framework == DependencyInjection.HILT else ""

        return f"""package {self.config.package_name}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
{f"import dagger.hilt.android.AndroidEntryPoint" if self.config.di_framework == DependencyInjection.HILT else ""}
import {self.config.package_name}.navigation.Navigation
import {self.config.package_name}.ui.theme.AppTheme

{hilt_annotation}class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            AppTheme {{
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {{
                    Navigation()
                }}
            }}
        }}
    }}
}}
"""

    def _generate_app(self) -> str:
        """Generate Application class"""
        if self.config.di_framework == DependencyInjection.HILT:
            return f"""package {self.config.package_name}

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application() {{
    override fun onCreate() {{
        super.onCreate()
    }}
}}
"""
        else:
            return f"""package {self.config.package_name}

import android.app.Application

class App : Application() {{
    override fun onCreate() {{
        super.onCreate()
    }}
}}
"""

    def _generate_composable(self, comp: ComposableSpec) -> str:
        """Generate Composable screen"""
        has_viewmodel = any(vm.name == f"{comp.name}ViewModel" for vm in self.viewmodels)

        viewmodel_line = ""
        if has_viewmodel:
            if self.config.di_framework == DependencyInjection.HILT:
                viewmodel_line = f"    val viewModel: {comp.name}ViewModel = hiltViewModel()"
            else:
                viewmodel_line = f"    val viewModel: {comp.name}ViewModel = viewModel()"

        return f"""package {self.config.package_name}.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
{f"import androidx.hilt.navigation.compose.hiltViewModel" if has_viewmodel and self.config.di_framework == DependencyInjection.HILT else ""}
{f"import androidx.lifecycle.viewmodel.compose.viewModel" if has_viewmodel and self.config.di_framework != DependencyInjection.HILT else ""}
{f"import {self.config.package_name}.ui.viewmodels.{comp.name}ViewModel" if has_viewmodel else ""}

@Composable
fun {comp.name}Screen(
    onNavigateBack: () -> Unit = {{}}
) {{
{viewmodel_line}

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {{
        Text(
            text = "{comp.name}",
            style = MaterialTheme.typography.headlineLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Welcome to {comp.name} screen",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {{ /* Handle action */ }},
            modifier = Modifier.fillMaxWidth()
        ) {{
            Text("Action Button")
        }}
    }}
}}
"""

    def _generate_viewmodel(self, vm: ViewModelKtSpec) -> str:
        """Generate ViewModel"""
        hilt_annotation = "@HiltViewModel\n" if self.config.di_framework == DependencyInjection.HILT else ""
        inject_annotation = "@Inject constructor(" if self.config.di_framework == DependencyInjection.HILT else "("

        state_properties = "\n    ".join([
            f"val {prop['name']}: StateFlow<{prop['type']}> get() = _{prop['name']}.asStateFlow()"
            for prop in vm.state_properties
        ])

        private_states = "\n    ".join([
            f"private val _{prop['name']} = MutableStateFlow<{prop['type']}>({prop.get('default', 'null')})"
            for prop in vm.state_properties
        ])

        return f"""package {self.config.package_name}.ui.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
{f"import dagger.hilt.android.lifecycle.HiltViewModel" if self.config.di_framework == DependencyInjection.HILT else ""}
{f"import javax.inject.Inject" if self.config.di_framework == DependencyInjection.HILT else ""}
import {self.config.package_name}.data.repository.UserRepository

{hilt_annotation}class {vm.name} {inject_annotation}
    private val repository: UserRepository
) : ViewModel() {{

    {private_states}

    {state_properties}

    init {{
        loadData()
    }}

    private fun loadData() {{
        viewModelScope.launch {{
            try {{
                // Load data from repository
            }} catch (e: Exception) {{
                // Handle error
            }}
        }}
    }}

    fun performAction() {{
        viewModelScope.launch {{
            // Perform action
        }}
    }}
}}
"""

    def _generate_navigation(self) -> str:
        """Generate navigation graph"""
        routes = "\n        ".join([
            f'''composable("{comp.name.lower()}") {{
            {comp.name}Screen()
        }}'''
            for comp in self.composables
        ])

        screen_imports = "\n".join([
            f"import {self.config.package_name}.ui.screens.{comp.name}Screen"
            for comp in self.composables
        ])

        return f"""package {self.config.package_name}.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
{screen_imports}

sealed class Screen(val route: String) {{
    {chr(10).join([f'    object {comp.name} : Screen("{comp.name.lower()}")' for comp in self.composables])}
}}

@Composable
fun Navigation() {{
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.{self.composables[0].name if self.composables else 'Home'}.route
    ) {{
        {routes}
    }}
}}
"""

    def _generate_user_model(self) -> str:
        """Generate User data model"""
        return f"""package {self.config.package_name}.data.models

import com.google.gson.annotations.SerializedName

data class User(
    val id: String,
    val name: String,
    val email: String,
    @SerializedName("avatar_url")
    val avatarUrl: String? = null,
    @SerializedName("created_at")
    val createdAt: String
)
"""

    def _generate_repository(self) -> str:
        """Generate repository"""
        inject_annotation = "@Inject constructor(" if self.config.di_framework == DependencyInjection.HILT else "("

        return f"""package {self.config.package_name}.data.repository

import {self.config.package_name}.data.models.User
import {self.config.package_name}.data.remote.ApiService
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
{f"import javax.inject.Inject" if self.config.di_framework == DependencyInjection.HILT else ""}
{f"import javax.inject.Singleton" if self.config.di_framework == DependencyInjection.HILT else ""}

{f"@Singleton" if self.config.di_framework == DependencyInjection.HILT else ""}
class UserRepository {inject_annotation}
    private val apiService: ApiService
) {{

    fun getUser(userId: String): Flow<Result<User>> = flow {{
        try {{
            val user = apiService.getUser(userId)
            emit(Result.success(user))
        }} catch (e: Exception) {{
            emit(Result.failure(e))
        }}
    }}

    suspend fun updateUser(user: User): Result<User> {{
        return try {{
            val updated = apiService.updateUser(user.id, user)
            Result.success(updated)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}
}}
"""

    def _generate_api_service(self) -> str:
        """Generate Retrofit API service"""
        return f"""package {self.config.package_name}.data.remote

import {self.config.package_name}.data.models.User
import retrofit2.http.*

interface ApiService {{

    @GET("users/{{userId}}")
    suspend fun getUser(@Path("userId") userId: String): User

    @PUT("users/{{userId}}")
    suspend fun updateUser(
        @Path("userId") userId: String,
        @Body user: User
    ): User

    @POST("auth/login")
    suspend fun login(@Body credentials: Map<String, String>): Map<String, Any>
}}
"""

    def _generate_hilt_module(self) -> str:
        """Generate Hilt DI module"""
        return f"""package {self.config.package_name}.di

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import {self.config.package_name}.data.remote.ApiService
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {{

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {{
        val loggingInterceptor = HttpLoggingInterceptor().apply {{
            level = HttpLoggingInterceptor.Level.BODY
        }}

        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }}

    @Provides
    @Singleton
    fun provideGson(): Gson {{
        return GsonBuilder()
            .setLenient()
            .create()
    }}

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, gson: Gson): Retrofit {{
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }}

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {{
        return retrofit.create(ApiService::class.java)
    }}
}}
"""

    def _generate_room_database(self) -> str:
        """Generate Room database"""
        return f"""package {self.config.package_name}.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import {self.config.package_name}.data.models.User

@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {{
    // Add DAOs here
}}
"""

    def _generate_extensions(self) -> str:
        """Generate Kotlin extensions"""
        return f"""package {self.config.package_name}.utils

import android.content.Context
import android.widget.Toast
import androidx.compose.ui.graphics.Color

fun Context.showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {{
    Toast.makeText(this, message, duration).show()
}}

fun String.isValidEmail(): Boolean {{
    return android.util.Patterns.EMAIL_ADDRESS.matcher(this).matches()
}}

fun Color.toHex(): String {{
    val red = (this.red * 255).toInt()
    val green = (this.green * 255).toInt()
    val blue = (this.blue * 255).toInt()
    return String.format("#%02X%02X%02X", red, green, blue)
}}
"""

    def _generate_theme(self) -> str:
        """Generate Material3 theme"""
        return f"""package {self.config.package_name}.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {{
    val colorScheme = when {{
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }}

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}}
"""

    def _generate_colors(self) -> str:
        """Generate color definitions"""
        return f"""package {self.config.package_name}.ui.theme

import androidx.compose.ui.graphics.Color

val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
"""

    def _generate_manifest(self) -> str:
        """Generate AndroidManifest.xml"""
        application_name = ".App" if self.config.di_framework == DependencyInjection.HILT else "android.app.Application"

        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:name="{application_name}"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{self.config.name}">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.{self.config.name}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""
