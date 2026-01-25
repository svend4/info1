"""
Developer Tools Package

IDE extensions, CLI tools и desktop applications.
"""

from .vscode_extension import VSCodeExtensionGenerator, VSCodeExtensionConfig
from .jetbrains_plugin import JetBrainsPluginGenerator
from .cli_package_manager import CLIPackageManager
from .copilot_integration import CopilotIntegration
from .electron_app import ElectronAppGenerator

__all__ = [
    'VSCodeExtensionGenerator',
    'VSCodeExtensionConfig',
    'JetBrainsPluginGenerator',
    'CLIPackageManager',
    'CopilotIntegration',
    'ElectronAppGenerator'
]

__version__ = '1.0.0'
