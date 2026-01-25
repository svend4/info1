#!/usr/bin/env python3
"""
Electron Desktop App Generator

Генерация Electron desktop application.
"""

import json
from typing import Dict, Any


class ElectronAppGenerator:
    """Генератор Electron приложения"""

    def generate_package_json(self, app_name: str, version: str) -> Dict[str, Any]:
        """Генерация package.json"""
        return {
            "name": app_name,
            "version": version,
            "description": "AI Project Generator Desktop App",
            "main": "main.js",
            "scripts": {
                "start": "electron .",
                "build": "electron-builder",
                "build:mac": "electron-builder --mac",
                "build:win": "electron-builder --win",
                "build:linux": "electron-builder --linux"
            },
            "dependencies": {
                "electron": "^28.0.0"
            },
            "devDependencies": {
                "electron-builder": "^24.0.0"
            },
            "build": {
                "appId": f"com.aigenerator.{app_name}",
                "productName": "AI Generator",
                "directories": {
                    "output": "dist"
                },
                "files": ["**/*"],
                "mac": {"category": "public.app-category.developer-tools"},
                "win": {"target": "nsis"},
                "linux": {"target": ["AppImage", "deb"]}
            }
        }

    def generate_main_js(self) -> str:
        """Генерация main.js"""
        return """const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('create-project', async (event, data) => {
    // Call AI Generator API
    return { success: true, projectName: data.name };
});
"""

    def generate_index_html(self) -> str:
        """Генерация index.html"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>AI Project Generator</title>
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        button { padding: 10px 20px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Project Generator</h1>
        <div>
            <input id="projectName" placeholder="Project Name" />
            <select id="template">
                <option>React TypeScript</option>
                <option>Node.js API</option>
                <option>Python Flask</option>
            </select>
            <button onclick="createProject()">Create Project</button>
        </div>
        <div id="output"></div>
    </div>
    <script src="renderer.js"></script>
</body>
</html>
"""

    def save_app(self, app_name: str, version: str, output_dir: str):
        """Сохранение приложения"""
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # package.json
        with open(output_path / 'package.json', 'w') as f:
            json.dump(self.generate_package_json(app_name, version), f, indent=2)

        # main.js
        with open(output_path / 'main.js', 'w') as f:
            f.write(self.generate_main_js())

        # index.html
        with open(output_path / 'index.html', 'w') as f:
            f.write(self.generate_index_html())

        print(f"✅ Electron app generated: {output_path}")
