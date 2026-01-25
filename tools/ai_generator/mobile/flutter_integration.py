#!/usr/bin/env python3
"""
Flutter Integration Generator

Автоматическая генерация Flutter приложений с BLoC pattern, GetX, и Provider.
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class StateManagementFlutter(Enum):
    """State Management Pattern"""
    BLOC = "bloc"
    GETX = "getx"
    PROVIDER = "provider"
    RIVERPOD = "riverpod"
    MOBX = "mobx"


class RouterType(Enum):
    """Router Type"""
    NAVIGATOR = "navigator"
    GO_ROUTER = "go_router"
    AUTO_ROUTE = "auto_route"


@dataclass
class WidgetSpec:
    """Flutter Widget Specification"""
    name: str
    type: str  # stateless, stateful, screen
    properties: List[Dict[str, str]] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class BlocSpec:
    """BLoC Specification"""
    name: str
    events: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)


@dataclass
class FlutterAppConfig:
    """Flutter App Configuration"""
    name: str
    package_name: str
    version: str = "1.0.0"
    state_management: StateManagementFlutter = StateManagementFlutter.BLOC
    router: RouterType = RouterType.GO_ROUTER
    features: List[str] = field(default_factory=list)


class FlutterGenerator:
    """Flutter Application Generator"""

    def __init__(self, config: FlutterAppConfig):
        """
        Инициализация Flutter generator

        Args:
            config: Application configuration
        """
        self.config = config
        self.widgets: List[WidgetSpec] = []
        self.blocs: List[BlocSpec] = []

    def add_screen(self, widget: WidgetSpec, bloc: Optional[BlocSpec] = None):
        """
        Add screen to application

        Args:
            widget: Widget specification
            bloc: Optional BLoC specification
        """
        self.widgets.append(widget)
        if bloc:
            self.blocs.append(bloc)
        print(f"🦋 Added screen: {widget.name}")

    def generate_project(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete Flutter project

        Args:
            output_dir: Output directory path

        Returns:
            Dictionary of generated files
        """
        print(f"🚀 Generating Flutter project: {self.config.name}")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate pubspec.yaml
        files['pubspec.yaml'] = self._generate_pubspec()

        # Generate main.dart
        files['lib/main.dart'] = self._generate_main()

        # Generate widgets
        for widget in self.widgets:
            files[f'lib/screens/{widget.name.lower()}_screen.dart'] = \
                self._generate_widget(widget)

        # Generate BLoCs/state management
        if self.config.state_management == StateManagementFlutter.BLOC:
            for bloc in self.blocs:
                files[f'lib/blocs/{bloc.name.lower()}_bloc.dart'] = \
                    self._generate_bloc(bloc)
                files[f'lib/blocs/{bloc.name.lower()}_event.dart'] = \
                    self._generate_bloc_events(bloc)
                files[f'lib/blocs/{bloc.name.lower()}_state.dart'] = \
                    self._generate_bloc_states(bloc)

        # Generate models
        files['lib/models/user.dart'] = self._generate_user_model()

        # Generate services
        files['lib/services/api_service.dart'] = self._generate_api_service()
        files['lib/services/auth_service.dart'] = self._generate_auth_service()

        # Generate repositories
        files['lib/repositories/user_repository.dart'] = self._generate_repository()

        # Generate router
        if self.config.router == RouterType.GO_ROUTER:
            files['lib/router/app_router.dart'] = self._generate_go_router()

        # Generate utilities
        files['lib/utils/constants.dart'] = self._generate_constants()
        files['lib/utils/extensions.dart'] = self._generate_extensions()

        # Generate theme
        files['lib/theme/app_theme.dart'] = self._generate_theme()
        files['lib/theme/colors.dart'] = self._generate_colors()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} files")
        return files

    def _generate_pubspec(self) -> str:
        """Generate pubspec.yaml"""
        dependencies = {
            "flutter": {"sdk": "flutter"},
            "cupertino_icons": "^1.0.2"
        }

        # Add state management
        if self.config.state_management == StateManagementFlutter.BLOC:
            dependencies["flutter_bloc"] = "^8.1.3"
            dependencies["equatable"] = "^2.0.5"
        elif self.config.state_management == StateManagementFlutter.GETX:
            dependencies["get"] = "^4.6.6"
        elif self.config.state_management == StateManagementFlutter.PROVIDER:
            dependencies["provider"] = "^6.1.1"
        elif self.config.state_management == StateManagementFlutter.RIVERPOD:
            dependencies["flutter_riverpod"] = "^2.4.9"

        # Add router
        if self.config.router == RouterType.GO_ROUTER:
            dependencies["go_router"] = "^12.1.3"

        # Add common packages
        dependencies.update({
            "dio": "^5.4.0",
            "shared_preferences": "^2.2.2",
            "freezed_annotation": "^2.4.1",
            "json_annotation": "^4.8.1"
        })

        dev_dependencies = {
            "flutter_test": {"sdk": "flutter"},
            "flutter_lints": "^3.0.1",
            "build_runner": "^2.4.7",
            "freezed": "^2.4.6",
            "json_serializable": "^6.7.1"
        }

        pubspec = {
            "name": self.config.package_name,
            "description": f"A new Flutter project: {self.config.name}",
            "version": self.config.version,
            "environment": {
                "sdk": ">=3.2.0 <4.0.0"
            },
            "dependencies": dependencies,
            "dev_dependencies": dev_dependencies,
            "flutter": {
                "uses-material-design": True
            }
        }

        return yaml.dump(pubspec, default_flow_style=False, sort_keys=False)

    def _generate_main(self) -> str:
        """Generate main.dart"""
        imports = ["import 'package:flutter/material.dart';"]

        if self.config.state_management == StateManagementFlutter.BLOC:
            imports.append("import 'package:flutter_bloc/flutter_bloc.dart';")
        elif self.config.state_management == StateManagementFlutter.GETX:
            imports.append("import 'package:get/get.dart';")
        elif self.config.state_management == StateManagementFlutter.PROVIDER:
            imports.append("import 'package:provider/provider.dart';")

        if self.config.router == RouterType.GO_ROUTER:
            imports.append("import 'router/app_router.dart';")

        imports.append("import 'theme/app_theme.dart';")

        app_widget = """  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '${self.config.name}',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      home: HomeScreen(),
    );
  }"""

        if self.config.router == RouterType.GO_ROUTER:
            app_widget = """  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '${self.config.name}',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      routerConfig: AppRouter.router,
    );
  }"""

        return f"""{chr(10).join(imports)}

void main() {{
  runApp(const MyApp());
}}

class MyApp extends StatelessWidget {{
  const MyApp({{super.key}});

{app_widget}
}}
"""

    def _generate_widget(self, widget: WidgetSpec) -> str:
        """Generate Flutter widget"""
        class_type = "StatelessWidget" if widget.type == "stateless" else "StatefulWidget"

        if widget.type == "stateless":
            return f"""import 'package:flutter/material.dart';

class {widget.name}Screen extends {class_type} {{
  const {widget.name}Screen({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{widget.name}'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '{widget.name} Screen',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {{
                // Handle action
              }},
              child: const Text('Action Button'),
            ),
          ],
        ),
      ),
    );
  }}
}}
"""
        else:
            return f"""import 'package:flutter/material.dart';

class {widget.name}Screen extends StatefulWidget {{
  const {widget.name}Screen({{super.key}});

  @override
  State<{widget.name}Screen> createState() => _{widget.name}ScreenState();
}}

class _{widget.name}ScreenState extends State<{widget.name}Screen> {{
  @override
  void initState() {{
    super.initState();
    // Initialize state
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{widget.name}'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '{widget.name} Screen',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _handleAction,
              child: const Text('Action Button'),
            ),
          ],
        ),
      ),
    );
  }}

  void _handleAction() {{
    // Handle action
    setState(() {{
      // Update state
    }});
  }}
}}
"""

    def _generate_bloc(self, bloc: BlocSpec) -> str:
        """Generate BLoC"""
        return f"""import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '{bloc.name.lower()}_event.dart';
import '{bloc.name.lower()}_state.dart';

class {bloc.name}Bloc extends Bloc<{bloc.name}Event, {bloc.name}State> {{
  {bloc.name}Bloc() : super({bloc.name}Initial()) {{
    on<{bloc.events[0] if bloc.events else 'LoadData'}>(_onLoadData);
  }}

  Future<void> _onLoadData(
    {bloc.events[0] if bloc.events else 'LoadData'} event,
    Emitter<{bloc.name}State> emit,
  ) async {{
    emit({bloc.name}Loading());

    try {{
      // Load data
      await Future.delayed(const Duration(seconds: 1));
      emit({bloc.name}Loaded());
    }} catch (e) {{
      emit({bloc.name}Error(e.toString()));
    }}
  }}
}}
"""

    def _generate_bloc_events(self, bloc: BlocSpec) -> str:
        """Generate BLoC events"""
        events = bloc.events if bloc.events else ['LoadData', 'RefreshData']

        event_classes = "\n\n".join([
            f"class {event} extends {bloc.name}Event {{\n  const {event}();\n}}"
            for event in events
        ])

        return f"""import 'package:equatable/equatable.dart';

abstract class {bloc.name}Event extends Equatable {{
  const {bloc.name}Event();

  @override
  List<Object?> get props => [];
}}

{event_classes}
"""

    def _generate_bloc_states(self, bloc: BlocSpec) -> str:
        """Generate BLoC states"""
        states = bloc.states if bloc.states else ['Initial', 'Loading', 'Loaded', 'Error']

        state_classes = []
        for state in states:
            if state == 'Error':
                state_classes.append(
                    f"""class {bloc.name}{state} extends {bloc.name}State {{
  final String message;
  const {bloc.name}{state}(this.message);

  @override
  List<Object?> get props => [message];
}}"""
                )
            else:
                state_classes.append(
                    f"class {bloc.name}{state} extends {bloc.name}State {{\n  const {bloc.name}{state}();\n}}"
                )

        return f"""import 'package:equatable/equatable.dart';

abstract class {bloc.name}State extends Equatable {{
  const {bloc.name}State();

  @override
  List<Object?> get props => [];
}}

{chr(10).join(state_classes)}
"""

    def _generate_user_model(self) -> str:
        """Generate User model"""
        return """import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    String? avatar,
    @JsonKey(name: 'created_at') DateTime? createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
"""

    def _generate_api_service(self) -> str:
        """Generate API service"""
        return """import 'package:dio/dio.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio _dio;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.example.com',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token
          final token = await _getAuthToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) {
          // Handle errors
          return handler.next(error);
        },
      ),
    );
  }

  Future<String?> _getAuthToken() async {
    // Retrieve token from storage
    return null;
  }

  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await _dio.get(path, queryParameters: queryParameters);
    return response.data as T;
  }

  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
    );
    return response.data as T;
  }

  Future<T> put<T>(
    String path, {
    dynamic data,
  }) async {
    final response = await _dio.put(path, data: data);
    return response.data as T;
  }

  Future<void> delete(String path) async {
    await _dio.delete(path);
  }
}
"""

    def _generate_auth_service(self) -> str:
        """Generate auth service"""
        return """import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;

  final ApiService _api = ApiService();
  static const String _tokenKey = 'auth_token';

  AuthService._internal();

  Future<User> login(String email, String password) async {
    final response = await _api.post<Map<String, dynamic>>(
      '/auth/login',
      data: {
        'email': email,
        'password': password,
      },
    );

    final token = response['token'] as String;
    await _saveToken(token);

    return User.fromJson(response['user'] as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await _deleteToken();
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<void> _deleteToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }
}
"""

    def _generate_repository(self) -> str:
        """Generate repository"""
        return """import '../models/user.dart';
import '../services/api_service.dart';

class UserRepository {
  final ApiService _api = ApiService();

  Future<User> getUser(String userId) async {
    final response = await _api.get<Map<String, dynamic>>('/users/$userId');
    return User.fromJson(response);
  }

  Future<User> updateUser(User user) async {
    final response = await _api.put<Map<String, dynamic>>(
      '/users/${user.id}',
      data: user.toJson(),
    );
    return User.fromJson(response);
  }

  Future<List<User>> getUsers() async {
    final response = await _api.get<List<dynamic>>('/users');
    return response.map((json) => User.fromJson(json as Map<String, dynamic>)).toList();
  }
}
"""

    def _generate_go_router(self) -> str:
        """Generate GoRouter configuration"""
        routes = ",\n      ".join([
            f'''GoRoute(
        path: '/{widget.name.lower()}',
        builder: (context, state) => const {widget.name}Screen(),
      )'''
            for widget in self.widgets
        ])

        screen_imports = "\n".join([
            f"import '../screens/{widget.name.lower()}_screen.dart';"
            for widget in self.widgets
        ])

        return f"""import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
{screen_imports}

class AppRouter {{
  static final GoRouter router = GoRouter(
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const {self.widgets[0].name if self.widgets else 'Home'}Screen(),
      ),
      {routes}
    ],
  );
}}
"""

    def _generate_constants(self) -> str:
        """Generate constants"""
        return """class AppConstants {
  static const String appName = 'MyApp';
  static const String apiVersion = 'v1';

  // API Endpoints
  static const String baseUrl = 'https://api.example.com';

  // Spacing
  static const double spacingSmall = 8.0;
  static const double spacingMedium = 16.0;
  static const double spacingLarge = 24.0;

  // Border Radius
  static const double borderRadiusSmall = 4.0;
  static const double borderRadiusMedium = 8.0;
  static const double borderRadiusLarge = 16.0;
}
"""

    def _generate_extensions(self) -> str:
        """Generate extensions"""
        return """import 'package:flutter/material.dart';

extension StringExtension on String {
  bool get isValidEmail {
    return RegExp(r'^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$').hasMatch(this);
  }

  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}

extension ContextExtension on BuildContext {
  void showSnackBar(String message) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => Theme.of(this).textTheme;
  ColorScheme get colorScheme => Theme.of(this).colorScheme;
}

extension DateTimeExtension on DateTime {
  String toFormattedString() {
    return '$day/$month/$year';
  }
}
"""

    def _generate_theme(self) -> str:
        """Generate app theme"""
        return """import 'package:flutter/material.dart';
import 'colors.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: AppColors.background,
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: AppColors.backgroundDark,
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }
}
"""

    def _generate_colors(self) -> str:
        """Generate color definitions"""
        return """import 'package:flutter/material.dart';

class AppColors {
  // Primary
  static const Color primary = Color(0xFF6200EE);
  static const Color primaryVariant = Color(0xFF3700B3);
  static const Color secondary = Color(0xFF03DAC6);

  // Background
  static const Color background = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF121212);

  // Text
  static const Color textPrimary = Color(0xFF000000);
  static const Color textSecondary = Color(0xFF666666);

  // Status
  static const Color success = Color(0xFF4CAF50);
  static const Color error = Color(0xFFB00020);
  static const Color warning = Color(0xFFFF9800);
  static const Color info = Color(0xFF2196F3);
}
"""
