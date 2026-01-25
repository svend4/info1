#!/usr/bin/env python3
"""
VS Code Extension Generator

Генерация VS Code расширения для AI Project Generator.
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class VSCodeExtensionConfig:
    """Конфигурация VS Code расширения"""
    name: str
    display_name: str
    description: str
    version: str
    publisher: str
    keywords: List[str]


class VSCodeExtensionGenerator:
    """Генератор VS Code расширения"""

    def __init__(self):
        """Инициализация"""
        self.config = None

    def generate_package_json(self, config: VSCodeExtensionConfig) -> Dict[str, Any]:
        """Генерация package.json"""
        return {
            "name": config.name,
            "displayName": config.display_name,
            "description": config.description,
            "version": config.version,
            "publisher": config.publisher,
            "engines": {
                "vscode": "^1.75.0"
            },
            "categories": ["Other", "Snippets", "Programming Languages"],
            "keywords": config.keywords,
            "activationEvents": [
                "onCommand:aigenerator.createProject",
                "onCommand:aigenerator.generateCode",
                "onView:aigenerator.sidebar"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "aigenerator.createProject",
                        "title": "AI Generator: Create New Project",
                        "icon": "$(new-folder)"
                    },
                    {
                        "command": "aigenerator.generateCode",
                        "title": "AI Generator: Generate Code",
                        "icon": "$(sparkle)"
                    },
                    {
                        "command": "aigenerator.reviewCode",
                        "title": "AI Generator: Review Code",
                        "icon": "$(checklist)"
                    }
                ],
                "views": {
                    "explorer": [
                        {
                            "id": "aigenerator.sidebar",
                            "name": "AI Generator",
                            "icon": "resources/icon.svg"
                        }
                    ]
                },
                "viewsContainers": {
                    "activitybar": [
                        {
                            "id": "aigenerator",
                            "title": "AI Generator",
                            "icon": "resources/icon.svg"
                        }
                    ]
                },
                "configuration": {
                    "title": "AI Generator",
                    "properties": {
                        "aigenerator.apiKey": {
                            "type": "string",
                            "default": "",
                            "description": "API Key for AI Generator"
                        },
                        "aigenerator.autoReview": {
                            "type": "boolean",
                            "default": true,
                            "description": "Automatically review code on save"
                        }
                    }
                }
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc -watch -p ./",
                "test": "node ./out/test/runTest.js"
            },
            "devDependencies": {
                "@types/vscode": "^1.75.0",
                "@types/node": "^18.0.0",
                "typescript": "^4.9.0"
            }
        }

    def generate_extension_ts(self) -> str:
        """Генерация extension.ts"""
        return """import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Generator extension activated');

    // Create Project command
    let createProject = vscode.commands.registerCommand('aigenerator.createProject', async () => {
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'my-awesome-project'
        });

        if (projectName) {
            const template = await vscode.window.showQuickPick([
                'React TypeScript',
                'Node.js Express',
                'Python Flask',
                'Go API'
            ], {
                placeHolder: 'Select template'
            });

            if (template) {
                await generateProject(projectName, template);
                vscode.window.showInformationMessage(`Project "${projectName}" created!`);
            }
        }
    });

    // Generate Code command
    let generateCode = vscode.commands.registerCommand('aigenerator.generateCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const prompt = await vscode.window.showInputBox({
            prompt: 'Describe the code you want to generate',
            placeHolder: 'e.g., Create a function to validate emails'
        });

        if (prompt) {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Generating code...',
                cancellable: false
            }, async (progress) => {
                const code = await callAIGenerator(prompt);
                editor.edit(editBuilder => {
                    editBuilder.insert(editor.selection.active, code);
                });
            });
        }
    });

    // Code Review command
    let reviewCode = vscode.commands.registerCommand('aigenerator.reviewCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        const document = editor.document;
        const code = document.getText();

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Reviewing code...',
            cancellable: false
        }, async (progress) => {
            const review = await reviewCodeWithAI(code);
            showReviewResults(review);
        });
    });

    context.subscriptions.push(createProject, generateCode, reviewCode);
}

async function generateProject(name: string, template: string): Promise<void> {
    // Call AI Generator API
    const config = vscode.workspace.getConfiguration('aigenerator');
    const apiKey = config.get<string>('apiKey');

    // Implementation here
}

async function callAIGenerator(prompt: string): Promise<string> {
    // Call AI API
    return `// Generated code for: ${prompt}\\nfunction example() {}`;
}

async function reviewCodeWithAI(code: string): Promise<any> {
    // Call review API
    return {
        quality_score: 85,
        issues: []
    };
}

function showReviewResults(review: any): void {
    vscode.window.showInformationMessage(`Code quality: ${review.quality_score}/100`);
}

export function deactivate() {}
"""

    def generate_tsconfig(self) -> Dict[str, Any]:
        """Генерация tsconfig.json"""
        return {
            "compilerOptions": {
                "module": "commonjs",
                "target": "ES2020",
                "outDir": "out",
                "lib": ["ES2020"],
                "sourceMap": true,
                "rootDir": "src",
                "strict": true
            },
            "exclude": ["node_modules", ".vscode-test"]
        }

    def generate_readme(self, config: VSCodeExtensionConfig) -> str:
        """Генерация README.md"""
        return f"""# {config.display_name}

{config.description}

## Features

- 🚀 Create new projects from AI-generated templates
- ✨ Generate code with AI assistance
- 🔍 Automated code review
- 📊 Real-time quality metrics

## Usage

### Create Project
1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Type "AI Generator: Create New Project"
3. Enter project name and select template

### Generate Code
1. Place cursor where you want to insert code
2. Run "AI Generator: Generate Code"
3. Describe what you want

### Review Code
1. Open any code file
2. Run "AI Generator: Review Code"
3. View quality report

## Configuration

- `aigenerator.apiKey`: Your AI Generator API key
- `aigenerator.autoReview`: Auto-review on save (default: true)

## Requirements

- VS Code 1.75.0 or higher
- AI Generator API key

## Installation

1. Download from VS Code Marketplace
2. Configure API key in settings
3. Start creating!

## License

MIT
"""

    def save_extension(self, config: VSCodeExtensionConfig, output_dir: str):
        """Сохранение расширения"""
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # package.json
        package_json = self.generate_package_json(config)
        with open(output_path / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

        # tsconfig.json
        tsconfig = self.generate_tsconfig()
        with open(output_path / 'tsconfig.json', 'w') as f:
            json.dump(tsconfig, f, indent=2)

        # src/extension.ts
        src_dir = output_path / 'src'
        src_dir.mkdir(exist_ok=True)
        with open(src_dir / 'extension.ts', 'w') as f:
            f.write(self.generate_extension_ts())

        # README.md
        with open(output_path / 'README.md', 'w') as f:
            f.write(self.generate_readme(config))

        print(f"✅ VS Code extension generated: {output_path}")
