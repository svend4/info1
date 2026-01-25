#!/usr/bin/env python3
"""
SwiftUI Generator

Автоматическая генерация SwiftUI приложений с MVVM architecture, Combine, и async/await.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ArchitecturePattern(Enum):
    """Architecture Pattern"""
    MVVM = "mvvm"
    MVI = "mvi"
    CLEAN = "clean"
    VIPER = "viper"


class DataPersistence(Enum):
    """Data Persistence Solution"""
    CORE_DATA = "coredata"
    REALM = "realm"
    USERDEFAULTS = "userdefaults"
    SWIFTDATA = "swiftdata"


class NetworkLayer(Enum):
    """Networking Solution"""
    URLSESSION = "urlsession"
    ALAMOFIRE = "alamofire"
    MOYA = "moya"


@dataclass
class ViewSpec:
    """SwiftUI View Specification"""
    name: str
    type: str  # screen, component, modifier
    properties: List[Dict[str, str]] = field(default_factory=list)
    bindings: List[str] = field(default_factory=list)
    environment_objects: List[str] = field(default_factory=list)


@dataclass
class ViewModelSpec:
    """ViewModel Specification"""
    name: str
    properties: List[Dict[str, str]] = field(default_factory=list)
    published_properties: List[Dict[str, str]] = field(default_factory=list)
    methods: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class SwiftUIAppConfig:
    """SwiftUI App Configuration"""
    name: str
    bundle_id: str
    version: str = "1.0.0"
    min_ios_version: str = "16.0"
    architecture: ArchitecturePattern = ArchitecturePattern.MVVM
    persistence: Optional[DataPersistence] = None
    network: NetworkLayer = NetworkLayer.URLSESSION
    features: List[str] = field(default_factory=list)


class SwiftUIGenerator:
    """SwiftUI Application Generator"""

    def __init__(self, config: SwiftUIAppConfig):
        """
        Инициализация SwiftUI generator

        Args:
            config: Application configuration
        """
        self.config = config
        self.views: List[ViewSpec] = []
        self.view_models: List[ViewModelSpec] = []

    def add_view(self, view: ViewSpec, view_model: Optional[ViewModelSpec] = None):
        """
        Add view to application

        Args:
            view: View specification
            view_model: Optional ViewModel specification
        """
        self.views.append(view)
        if view_model:
            self.view_models.append(view_model)
        print(f"🍎 Added view: {view.name}")

    def generate_project(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete SwiftUI project

        Args:
            output_dir: Output directory path

        Returns:
            Dictionary of generated files
        """
        print(f"🚀 Generating SwiftUI project: {self.config.name}")

        output_dir.mkdir(parents=True, exist_ok=True)
        files = {}

        # Generate app entry point
        files[f'{self.config.name}App.swift'] = self._generate_app_entry()

        # Generate views
        for view in self.views:
            files[f'Views/{view.name}.swift'] = self._generate_view(view)

        # Generate view models
        for vm in self.view_models:
            files[f'ViewModels/{vm.name}.swift'] = self._generate_view_model(vm)

        # Generate models
        files['Models/User.swift'] = self._generate_user_model()
        files['Models/AppState.swift'] = self._generate_app_state()

        # Generate services
        files['Services/NetworkService.swift'] = self._generate_network_service()
        files['Services/AuthService.swift'] = self._generate_auth_service()

        # Generate utilities
        files['Utilities/Extensions.swift'] = self._generate_extensions()
        files['Utilities/Constants.swift'] = self._generate_constants()

        # Generate data layer
        if self.config.persistence == DataPersistence.CORE_DATA:
            files['Data/CoreDataManager.swift'] = self._generate_coredata_manager()
            files['Data/DataModel.xcdatamodeld'] = self._generate_coredata_model()

        # Generate project file
        files['project.pbxproj'] = self._generate_xcode_project()

        # Write files
        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(files)} files")
        return files

    def _generate_app_entry(self) -> str:
        """Generate main app entry point"""
        return f"""import SwiftUI

@main
struct {self.config.name}App: App {{
    @StateObject private var appState = AppState()

    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .environmentObject(appState)
        }}
    }}
}}
"""

    def _generate_view(self, view: ViewSpec) -> str:
        """Generate SwiftUI view"""
        has_viewmodel = any(vm.name == f"{view.name}ViewModel" for vm in self.view_models)

        state_properties = "\n    ".join([
            f"@State private var {prop['name']}: {prop['type']}" +
            (f" = {prop.get('default', 'nil')}" if 'default' in prop else "")
            for prop in view.properties
        ])

        viewmodel_line = ""
        if has_viewmodel:
            viewmodel_line = f"    @StateObject private var viewModel = {view.name}ViewModel()"

        return f"""import SwiftUI

struct {view.name}: View {{
    @EnvironmentObject var appState: AppState
{viewmodel_line}
    {state_properties}

    var body: some View {{
        NavigationView {{
            VStack(spacing: 20) {{
                Text("{view.name}")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Welcome to {view.name}")
                    .font(.subheadline)
                    .foregroundColor(.gray)

                Button(action: handleAction) {{
                    Text("Action Button")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }}
                .padding(.horizontal)

                Spacer()
            }}
            .padding()
            .navigationTitle("{view.name}")
        }}
    }}

    private func handleAction() {{
        print("Button tapped")
        {f"viewModel.performAction()" if has_viewmodel else "// Handle action"}
    }}
}}

#Preview {{
    {view.name}()
        .environmentObject(AppState())
}}
"""

    def _generate_view_model(self, vm: ViewModelSpec) -> str:
        """Generate ViewModel"""
        published_props = "\n    ".join([
            f"@Published var {prop['name']}: {prop['type']}" +
            (f" = {prop.get('default', 'nil')}" if 'default' in prop else "")
            for prop in vm.published_properties
        ])

        regular_props = "\n    ".join([
            f"private let {prop['name']}: {prop['type']}"
            for prop in vm.properties
        ])

        methods = "\n\n    ".join([
            self._generate_method(method)
            for method in vm.methods
        ])

        return f"""import Foundation
import Combine

@MainActor
class {vm.name}: ObservableObject {{
    {published_props}
    {regular_props}

    private var cancellables = Set<AnyCancellable>()
    private let networkService = NetworkService.shared

    init() {{
        setupBindings()
    }}

    private func setupBindings() {{
        // Setup Combine bindings
    }}

    {methods if methods else "// Add methods here"}
}}
"""

    def _generate_method(self, method: Dict[str, str]) -> str:
        """Generate method implementation"""
        name = method.get('name', 'performAction')
        return_type = method.get('return', 'Void')
        is_async = method.get('async', 'true') == 'true'

        if is_async:
            return f"""func {name}() async throws -> {return_type} {{
        // Async implementation
        try await Task.sleep(nanoseconds: 1_000_000_000)
        print("{name} completed")
    }}"""
        else:
            return f"""func {name}() -> {return_type} {{
        // Implementation
        print("{name} called")
    }}"""

    def _generate_user_model(self) -> str:
        """Generate User model"""
        return """import Foundation

struct User: Identifiable, Codable {
    let id: String
    var name: String
    var email: String
    var avatar: URL?
    var createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case email
        case avatar
        case createdAt = "created_at"
    }
}

extension User {
    static var preview: User {
        User(
            id: UUID().uuidString,
            name: "John Doe",
            email: "john@example.com",
            avatar: nil,
            createdAt: Date()
        )
    }
}
"""

    def _generate_app_state(self) -> str:
        """Generate app state management"""
        return """import Foundation
import SwiftUI

@MainActor
class AppState: ObservableObject {
    @Published var user: User?
    @Published var isAuthenticated: Bool = false
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func login(email: String, password: String) async throws {
        isLoading = true
        defer { isLoading = false }

        do {
            // Perform login
            let user = try await AuthService.shared.login(email: email, password: password)
            self.user = user
            self.isAuthenticated = true
        } catch {
            self.errorMessage = error.localizedDescription
            throw error
        }
    }

    func logout() {
        user = nil
        isAuthenticated = false
        AuthService.shared.logout()
    }
}
"""

    def _generate_network_service(self) -> str:
        """Generate network service"""
        if self.config.network == NetworkLayer.URLSESSION:
            return """import Foundation

enum NetworkError: Error {
    case invalidURL
    case invalidResponse
    case decodingError
    case serverError(Int)
}

class NetworkService {
    static let shared = NetworkService()

    private let baseURL = "https://api.example.com"
    private let session: URLSession

    private init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: configuration)
    }

    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: baseURL + endpoint) else {
            throw NetworkError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = await getAuthToken() {
            request.setValue("Bearer \\(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = body
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError(httpResponse.statusCode)
        }

        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingError
        }
    }

    private func getAuthToken() async -> String? {
        // Retrieve token from keychain
        return nil
    }
}
"""
        else:
            return "// Alamofire implementation would go here"

    def _generate_auth_service(self) -> str:
        """Generate authentication service"""
        return """import Foundation

class AuthService {
    static let shared = AuthService()

    private let networkService = NetworkService.shared
    private let keychainKey = "authToken"

    private init() {}

    func login(email: String, password: String) async throws -> User {
        struct LoginRequest: Codable {
            let email: String
            let password: String
        }

        struct LoginResponse: Codable {
            let user: User
            let token: String
        }

        let requestBody = LoginRequest(email: email, password: password)
        let data = try JSONEncoder().encode(requestBody)

        let response: LoginResponse = try await networkService.request(
            endpoint: "/auth/login",
            method: "POST",
            body: data
        )

        // Save token to keychain
        saveToken(response.token)

        return response.user
    }

    func logout() {
        // Remove token from keychain
        deleteToken()
    }

    private func saveToken(_ token: String) {
        UserDefaults.standard.set(token, forKey: keychainKey)
    }

    private func deleteToken() {
        UserDefaults.standard.removeObject(forKey: keychainKey)
    }

    func getToken() -> String? {
        return UserDefaults.standard.string(forKey: keychainKey)
    }
}
"""

    def _generate_extensions(self) -> str:
        """Generate Swift extensions"""
        return """import SwiftUI

extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}

extension String {
    var isValidEmail: Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format:"SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: self)
    }
}

extension Date {
    func formatted(style: DateFormatter.Style = .medium) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = style
        return formatter.string(from: self)
    }
}
"""

    def _generate_constants(self) -> str:
        """Generate app constants"""
        return """import Foundation
import SwiftUI

enum AppConstants {
    static let appName = "MyApp"
    static let apiVersion = "v1"

    enum Colors {
        static let primary = Color.blue
        static let secondary = Color.gray
        static let accent = Color.green
        static let background = Color(UIColor.systemBackground)
    }

    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
        static let extraLarge: CGFloat = 32
    }

    enum FontSizes {
        static let title: CGFloat = 28
        static let headline: CGFloat = 20
        static let body: CGFloat = 16
        static let caption: CGFloat = 12
    }
}
"""

    def _generate_coredata_manager(self) -> str:
        """Generate Core Data manager"""
        return f"""import CoreData

class CoreDataManager {{
    static let shared = CoreDataManager()

    let persistentContainer: NSPersistentContainer

    private init() {{
        persistentContainer = NSPersistentContainer(name: "{self.config.name}Model")
        persistentContainer.loadPersistentStores {{ description, error in
            if let error = error {{
                fatalError("Core Data failed to load: \\(error.localizedDescription)")
            }}
        }}
    }}

    var viewContext: NSManagedObjectContext {{
        return persistentContainer.viewContext
    }}

    func save() {{
        let context = viewContext
        if context.hasChanges {{
            do {{
                try context.save()
            }} catch {{
                let nsError = error as NSError
                fatalError("Unresolved error \\(nsError), \\(nsError.userInfo)")
            }}
        }}
    }}
}}
"""

    def _generate_coredata_model(self) -> str:
        """Generate Core Data model XML"""
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<model type="com.apple.IDECoreDataModeler.DataModel" documentVersion="1.0" lastSavedToolsVersion="21513" systemVersion="22A380" minimumToolsVersion="Automatic" sourceLanguage="Swift" userDefinedModelVersionIdentifier="">
    <entity name="UserEntity" representedClassName="UserEntity" syncable="YES">
        <attribute name="id" optional="NO" attributeType="String"/>
        <attribute name="name" optional="NO" attributeType="String"/>
        <attribute name="email" optional="NO" attributeType="String"/>
        <attribute name="createdAt" optional="NO" attributeType="Date" usesScalarValueType="NO"/>
    </entity>
</model>"""

    def _generate_xcode_project(self) -> str:
        """Generate simplified Xcode project file"""
        return f"""// !$*UTF8*$!
{{
    archiveVersion = 1;
    classes = {{
    }};
    objectVersion = 56;
    objects = {{
        /* Project object */
        /* Build configuration */
        buildSettings = {{
            PRODUCT_NAME = "{self.config.name}";
            PRODUCT_BUNDLE_IDENTIFIER = "{self.config.bundle_id}";
            IPHONEOS_DEPLOYMENT_TARGET = {self.config.min_ios_version};
            SWIFT_VERSION = 5.9;
        }};
    }};
    rootObject = /* Project object */;
}}
"""
