#!/usr/bin/env python3
"""
React Native Generator

Автоматическая генерация React Native приложений с TypeScript, navigation, и state management.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class NavigationType(Enum):
    """Navigation Type"""
    STACK = "stack"
    TAB = "tab"
    DRAWER = "drawer"
    BOTTOM_TAB = "bottom_tab"


class StateManagement(Enum):
    """State Management Solution"""
    REDUX = "redux"
    MOBX = "mobx"
    ZUSTAND = "zustand"
    RECOIL = "recoil"
    CONTEXT_API = "context"


class UILibrary(Enum):
    """UI Component Library"""
    NATIVE_BASE = "native-base"
    REACT_NATIVE_PAPER = "react-native-paper"
    REACT_NATIVE_ELEMENTS = "react-native-elements"
    UI_KITTEN = "ui-kitten"
    TAMAGUI = "tamagui"


@dataclass
class ComponentSpec:
    """React Native Component Specification"""
    name: str
    type: str  # screen, component, hook
    props: List[Dict[str, str]] = field(default_factory=list)
    state: List[Dict[str, str]] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    api_calls: List[str] = field(default_factory=list)
    navigation_targets: List[str] = field(default_factory=list)


@dataclass
class ScreenSpec:
    """Screen Specification"""
    name: str
    route: str
    components: List[ComponentSpec] = field(default_factory=list)
    requires_auth: bool = False
    header_shown: bool = True


@dataclass
class AppConfig:
    """React Native App Configuration"""
    name: str
    bundle_id: str
    version: str = "1.0.0"
    navigation_type: NavigationType = NavigationType.STACK
    state_management: StateManagement = StateManagement.ZUSTAND
    ui_library: Optional[UILibrary] = None
    features: List[str] = field(default_factory=list)  # auth, push, analytics, etc.


class ReactNativeGenerator:
    """React Native Application Generator"""

    def __init__(self, config: AppConfig):
        """
        Инициализация React Native generator

        Args:
            config: Application configuration
        """
        self.config = config
        self.screens: List[ScreenSpec] = []
        self.components: List[ComponentSpec] = []

    def add_screen(self, screen: ScreenSpec):
        """
        Add screen to application

        Args:
            screen: Screen specification
        """
        self.screens.append(screen)
        print(f"📱 Added screen: {screen.name} ({screen.route})")

    def generate_project(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete React Native project

        Args:
            output_dir: Output directory path

        Returns:
            Dictionary of generated files
        """
        print(f"🚀 Generating React Native project: {self.config.name}")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate core files
        files['package.json'] = self._generate_package_json()
        files['tsconfig.json'] = self._generate_tsconfig()
        files['App.tsx'] = self._generate_app_tsx()
        files['metro.config.js'] = self._generate_metro_config()
        files['.eslintrc.js'] = self._generate_eslint_config()
        files['.prettierrc'] = self._generate_prettier_config()

        # Generate navigation
        files['src/navigation/AppNavigator.tsx'] = self._generate_navigator()

        # Generate screens
        for screen in self.screens:
            screen_path = f"src/screens/{screen.name}/{screen.name}.tsx"
            files[screen_path] = self._generate_screen(screen)
            files[f"src/screens/{screen.name}/styles.ts"] = self._generate_screen_styles(screen)

        # Generate state management
        if self.config.state_management == StateManagement.ZUSTAND:
            files['src/store/useStore.ts'] = self._generate_zustand_store()
        elif self.config.state_management == StateManagement.REDUX:
            files['src/store/store.ts'] = self._generate_redux_store()

        # Generate API service
        files['src/services/api.ts'] = self._generate_api_service()

        # Generate types
        files['src/types/index.ts'] = self._generate_types()

        # Generate utils
        files['src/utils/helpers.ts'] = self._generate_helpers()

        # Platform-specific files
        files['android/app/build.gradle'] = self._generate_android_gradle()
        files['ios/Podfile'] = self._generate_ios_podfile()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} files")
        return files

    def _generate_package_json(self) -> str:
        """Generate package.json"""
        dependencies = {
            "react": "18.2.0",
            "react-native": "0.72.0",
            "@react-navigation/native": "^6.1.0",
        }

        # Add navigation dependencies
        if self.config.navigation_type == NavigationType.STACK:
            dependencies["@react-navigation/stack"] = "^6.3.0"
        elif self.config.navigation_type in [NavigationType.TAB, NavigationType.BOTTOM_TAB]:
            dependencies["@react-navigation/bottom-tabs"] = "^6.5.0"
        elif self.config.navigation_type == NavigationType.DRAWER:
            dependencies["@react-navigation/drawer"] = "^6.6.0"

        dependencies["react-native-screens"] = "^3.20.0"
        dependencies["react-native-safe-area-context"] = "^4.5.0"

        # Add state management
        if self.config.state_management == StateManagement.ZUSTAND:
            dependencies["zustand"] = "^4.3.0"
        elif self.config.state_management == StateManagement.REDUX:
            dependencies["@reduxjs/toolkit"] = "^1.9.0"
            dependencies["react-redux"] = "^8.0.0"
        elif self.config.state_management == StateManagement.MOBX:
            dependencies["mobx"] = "^6.9.0"
            dependencies["mobx-react-lite"] = "^3.4.0"

        # Add UI library
        if self.config.ui_library == UILibrary.NATIVE_BASE:
            dependencies["native-base"] = "^3.4.0"
        elif self.config.ui_library == UILibrary.REACT_NATIVE_PAPER:
            dependencies["react-native-paper"] = "^5.8.0"

        # Add features
        if "auth" in self.config.features:
            dependencies["@react-native-async-storage/async-storage"] = "^1.18.0"
        if "push" in self.config.features:
            dependencies["@react-native-firebase/messaging"] = "^18.0.0"
        if "analytics" in self.config.features:
            dependencies["@react-native-firebase/analytics"] = "^18.0.0"

        dependencies["axios"] = "^1.4.0"

        dev_dependencies = {
            "@types/react": "^18.2.0",
            "@types/react-native": "^0.72.0",
            "@typescript-eslint/eslint-plugin": "^5.59.0",
            "@typescript-eslint/parser": "^5.59.0",
            "eslint": "^8.40.0",
            "prettier": "^2.8.0",
            "typescript": "^5.0.0"
        }

        package = {
            "name": self.config.name.lower().replace(" ", "-"),
            "version": self.config.version,
            "private": True,
            "scripts": {
                "android": "react-native run-android",
                "ios": "react-native run-ios",
                "start": "react-native start",
                "test": "jest",
                "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
                "format": "prettier --write \"src/**/*.{ts,tsx}\""
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies
        }

        return json.dumps(package, indent=2)

    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration"""
        return json.dumps({
            "compilerOptions": {
                "target": "esnext",
                "module": "commonjs",
                "lib": ["es2017"],
                "allowJs": True,
                "jsx": "react-native",
                "noEmit": True,
                "isolatedModules": True,
                "strict": True,
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "allowSyntheticDefaultImports": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"]
                }
            },
            "include": ["src"],
            "exclude": ["node_modules"]
        }, indent=2)

    def _generate_app_tsx(self) -> str:
        """Generate main App.tsx"""
        imports = [
            "import React from 'react';",
            "import { StatusBar } from 'react-native';",
            "import { SafeAreaProvider } from 'react-native-safe-area-context';",
            "import AppNavigator from './src/navigation/AppNavigator';"
        ]

        if self.config.state_management == StateManagement.REDUX:
            imports.append("import { Provider } from 'react-redux';")
            imports.append("import { store } from './src/store/store';")

        if self.config.ui_library == UILibrary.NATIVE_BASE:
            imports.append("import { NativeBaseProvider } from 'native-base';")
        elif self.config.ui_library == UILibrary.REACT_NATIVE_PAPER:
            imports.append("import { Provider as PaperProvider } from 'react-native-paper';")

        app_content = "      <AppNavigator />"

        if self.config.ui_library == UILibrary.NATIVE_BASE:
            app_content = f"      <NativeBaseProvider>\n  {app_content}\n      </NativeBaseProvider>"
        elif self.config.ui_library == UILibrary.REACT_NATIVE_PAPER:
            app_content = f"      <PaperProvider>\n  {app_content}\n      </PaperProvider>"

        if self.config.state_management == StateManagement.REDUX:
            app_content = f"      <Provider store={{store}}>\n  {app_content}\n      </Provider>"

        return f"""{chr(10).join(imports)}

const App = () => {{
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" />
{app_content}
    </SafeAreaProvider>
  );
}};

export default App;
"""

    def _generate_navigator(self) -> str:
        """Generate navigation configuration"""
        nav_type = self.config.navigation_type

        if nav_type == NavigationType.STACK:
            import_line = "import { createStackNavigator } from '@react-navigation/stack';"
            create_line = "const Stack = createStackNavigator();"
            container_start = "    <Stack.Navigator initialRouteName=\"Home\">"
            container_end = "    </Stack.Navigator>"
            screen_template = "      <Stack.Screen name=\"{name}\" component={{{name}Screen}} />"

        elif nav_type == NavigationType.BOTTOM_TAB:
            import_line = "import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';"
            create_line = "const Tab = createBottomTabNavigator();"
            container_start = "    <Tab.Navigator>"
            container_end = "    </Tab.Navigator>"
            screen_template = "      <Tab.Screen name=\"{name}\" component={{{name}Screen}} />"

        else:
            import_line = "import { createStackNavigator } from '@react-navigation/stack';"
            create_line = "const Stack = createStackNavigator();"
            container_start = "    <Stack.Navigator>"
            container_end = "    </Stack.Navigator>"
            screen_template = "      <Stack.Screen name=\"{name}\" component={{{name}Screen}} />"

        # Import screens
        screen_imports = "\n".join([
            f"import {screen.name}Screen from '../screens/{screen.name}/{screen.name}';"
            for screen in self.screens
        ])

        # Generate screen entries
        screen_entries = "\n".join([
            screen_template.format(name=screen.name)
            for screen in self.screens
        ])

        return f"""import React from 'react';
import {{ NavigationContainer }} from '@react-navigation/native';
{import_line}
{screen_imports}

{create_line}

const AppNavigator = () => {{
  return (
    <NavigationContainer>
{container_start}
{screen_entries}
{container_end}
    </NavigationContainer>
  );
}};

export default AppNavigator;
"""

    def _generate_screen(self, screen: ScreenSpec) -> str:
        """Generate screen component"""
        hooks = ["useState", "useEffect"]

        state_hook = ""
        if self.config.state_management == StateManagement.ZUSTAND:
            hooks.append("useStore")
            state_hook = "  const { user, isLoading } = useStore();"

        return f"""import React, {{ {', '.join(hooks)} }} from 'react';
import {{ View, Text, StyleSheet, TouchableOpacity }} from 'react-native';
{f"import {{ useStore }} from '../../store/useStore';" if self.config.state_management == StateManagement.ZUSTAND else ""}
import styles from './styles';

interface {screen.name}ScreenProps {{
  navigation: any;
  route: any;
}}

const {screen.name}Screen: React.FC<{screen.name}ScreenProps> = ({{ navigation, route }}) => {{
{state_hook}

  useEffect(() => {{
    // Component initialization
    console.log('{screen.name} screen mounted');
  }}, []);

  const handlePress = () => {{
    // Handle user action
    console.log('Button pressed');
  }};

  return (
    <View style={{styles.container}}>
      <Text style={{styles.title}}>{screen.name}</Text>
      <Text style={{styles.subtitle}}>Welcome to {screen.name} screen</Text>

      <TouchableOpacity style={{styles.button}} onPress={{handlePress}}>
        <Text style={{styles.buttonText}}>Action Button</Text>
      </TouchableOpacity>
    </View>
  );
}};

export default {screen.name}Screen;
"""

    def _generate_screen_styles(self, screen: ScreenSpec) -> str:
        """Generate screen styles"""
        return """import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default styles;
"""

    def _generate_zustand_store(self) -> str:
        """Generate Zustand store"""
        return """import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AppState {
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  setUser: (user) => set({ user }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  logout: () => set({ user: null, error: null }),
}));
"""

    def _generate_redux_store(self) -> str:
        """Generate Redux store"""
        return """import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AppState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AppState = {
  user: null,
  isLoading: false,
  error: null,
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.error = null;
    },
  },
});

export const { setUser, setLoading, setError, logout } = appSlice.actions;

export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
"""

    def _generate_api_service(self) -> str:
        """Generate API service"""
        return """import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = 'https://api.example.com';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Add auth token if available
        const token = await this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          await this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  private async getAuthToken(): Promise<string | null> {
    // Retrieve token from storage
    return null;
  }

  private async handleUnauthorized() {
    // Handle logout
    console.log('Unauthorized - logging out');
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export default new ApiService();
"""

    def _generate_types(self) -> str:
        """Generate TypeScript types"""
        return """export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

export type NavigationParams = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};
"""

    def _generate_helpers(self) -> str:
        """Generate utility helpers"""
        return """export const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString();
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

export const validateEmail = (email: string): boolean => {
  const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return re.test(email);
};
"""

    def _generate_metro_config(self) -> str:
        """Generate Metro bundler configuration"""
        return """const { getDefaultConfig } = require('metro-config');

module.exports = (async () => {
  const defaultConfig = await getDefaultConfig();
  return {
    ...defaultConfig,
    transformer: {
      babelTransformerPath: require.resolve('react-native-svg-transformer'),
    },
    resolver: {
      assetExts: defaultConfig.resolver.assetExts.filter(ext => ext !== 'svg'),
      sourceExts: [...defaultConfig.resolver.sourceExts, 'svg'],
    },
  };
})();
"""

    def _generate_eslint_config(self) -> str:
        """Generate ESLint configuration"""
        return """module.exports = {
  root: true,
  extends: [
    '@react-native-community',
    'plugin:@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    'react-native/no-inline-styles': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'off',
  },
};
"""

    def _generate_prettier_config(self) -> str:
        """Generate Prettier configuration"""
        return json.dumps({
            "semi": True,
            "singleQuote": True,
            "trailingComma": "es5",
            "tabWidth": 2,
            "printWidth": 100
        }, indent=2)

    def _generate_android_gradle(self) -> str:
        """Generate Android build.gradle"""
        return f"""apply plugin: "com.android.application"

android {{
    compileSdkVersion 33

    defaultConfig {{
        applicationId "{self.config.bundle_id}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "{self.config.version}"
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }}
    }}
}}

dependencies {{
    implementation "com.facebook.react:react-native:+"
}}
"""

    def _generate_ios_podfile(self) -> str:
        """Generate iOS Podfile"""
        return f"""platform :ios, '13.0'
require_relative '../node_modules/react-native/scripts/react_native_pods'
require_relative '../node_modules/@react-native-community/cli-platform-ios/native_modules'

target '{self.config.name}' do
  config = use_native_modules!

  use_react_native!(
    :path => config[:reactNativePath],
    :hermes_enabled => true
  )

  post_install do |installer|
    react_native_post_install(installer)
  end
end
"""
