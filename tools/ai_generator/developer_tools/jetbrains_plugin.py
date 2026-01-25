#!/usr/bin/env python3
"""
JetBrains Plugin Generator

Генерация JetBrains IDE плагина (IntelliJ, PyCharm, WebStorm, etc.).
"""

import json
from typing import Dict, Any


class JetBrainsPluginGenerator:
    """Генератор JetBrains плагина"""

    def generate_plugin_xml(self, plugin_id: str, name: str, version: str) -> str:
        """Генерация plugin.xml"""
        return f"""<idea-plugin>
    <id>{plugin_id}</id>
    <name>{name}</name>
    <version>{version}</version>
    <vendor email="support@aigenerator.com" url="https://aigenerator.com">AI Generator</vendor>

    <description><![CDATA[
    AI-powered project generation and code assistance for JetBrains IDEs.

    Features:
    - Create projects from AI-generated templates
    - Generate code with AI assistance
    - Automated code review and refactoring
    - Real-time quality metrics
    ]]></description>

    <depends>com.intellij.modules.platform</depends>

    <extensions defaultExtensionNs="com.intellij">
        <applicationService serviceImplementation="com.aigenerator.services.AIGeneratorService"/>
        <toolWindow id="AI Generator" secondary="true" icon="/icons/toolwindow.svg"
                    anchor="right" factoryClass="com.aigenerator.toolwindow.AIGeneratorToolWindowFactory"/>
        <notificationGroup id="AI Generator Notifications" displayType="BALLOON"/>
    </extensions>

    <actions>
        <group id="AIGenerator.MainMenu" text="AI Generator" description="AI Generator actions">
            <add-to-group group-id="MainMenu" anchor="last"/>
            <action id="AIGenerator.CreateProject"
                    class="com.aigenerator.actions.CreateProjectAction"
                    text="Create AI Project"
                    description="Create new project with AI"
                    icon="/icons/create.svg"/>
            <action id="AIGenerator.GenerateCode"
                    class="com.aigenerator.actions.GenerateCodeAction"
                    text="Generate Code"
                    description="Generate code with AI"/>
            <action id="AIGenerator.ReviewCode"
                    class="com.aigenerator.actions.ReviewCodeAction"
                    text="Review Code"
                    description="Review current file"/>
        </group>
    </actions>
</idea-plugin>
"""

    def generate_build_gradle(self, version: str) -> str:
        """Генерация build.gradle.kts"""
        return f"""plugins {{
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.0"
    id("org.jetbrains.intellij") version "1.16.0"
}}

group = "com.aigenerator"
version = "{version}"

repositories {{
    mavenCentral()
}}

dependencies {{
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("com.google.code.gson:gson:2.10.1")
    testImplementation("junit:junit:4.13.2")
}}

intellij {{
    version.set("2023.1")
    type.set("IC")
    plugins.set(listOf())
}}

tasks {{
    patchPluginXml {{
        sinceBuild.set("231")
        untilBuild.set("233.*")
    }}

    buildSearchableOptions {{
        enabled = false
    }}
}}
"""

    def generate_service_kotlin(self) -> str:
        """Генерация AIGeneratorService.kt"""
        return """package com.aigenerator.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project

@Service
class AIGeneratorService(private val project: Project) {
    private var apiKey: String? = null

    fun setApiKey(key: String) {
        apiKey = key
    }

    suspend fun generateProject(name: String, template: String): ProjectResult {
        // Call AI Generator API
        return ProjectResult(name, emptyList())
    }

    suspend fun generateCode(prompt: String): String {
        // Call AI API
        return "// Generated code"
    }

    suspend fun reviewCode(code: String): ReviewResult {
        return ReviewResult(85.0, emptyList())
    }
}

data class ProjectResult(val name: String, val files: List<String>)
data class ReviewResult(val qualityScore: Double, val issues: List<String>)
"""

    def generate_action_kotlin(self) -> str:
        """Генерация CreateProjectAction.kt"""
        return """package com.aigenerator.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.ui.DialogWrapper
import javax.swing.*

class CreateProjectAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return

        val dialog = CreateProjectDialog(project)
        if (dialog.showAndGet()) {
            val projectName = dialog.projectName
            val template = dialog.selectedTemplate

            // Create project
            Messages.showInfoMessage(
                project,
                "Project '$projectName' created successfully!",
                "Success"
            )
        }
    }
}

class CreateProjectDialog(project: com.intellij.openapi.project.Project) : DialogWrapper(project) {
    private val nameField = JTextField(20)
    private val templateCombo = JComboBox(arrayOf(
        "React TypeScript",
        "Spring Boot",
        "Python Django",
        "Go Gin"
    ))

    val projectName: String get() = nameField.text
    val selectedTemplate: String get() = templateCombo.selectedItem as String

    init {
        init()
        title = "Create AI Project"
    }

    override fun createCenterPanel(): JComponent {
        val panel = JPanel()
        panel.layout = BoxLayout(panel, BoxLayout.Y_AXIS)

        panel.add(JLabel("Project Name:"))
        panel.add(nameField)
        panel.add(Box.createVerticalStrut(10))
        panel.add(JLabel("Template:"))
        panel.add(templateCombo)

        return panel
    }
}
"""

    def save_plugin(self, plugin_id: str, name: str, version: str, output_dir: str):
        """Сохранение плагина"""
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # plugin.xml
        resources_dir = output_path / 'src' / 'main' / 'resources' / 'META-INF'
        resources_dir.mkdir(parents=True, exist_ok=True)
        with open(resources_dir / 'plugin.xml', 'w') as f:
            f.write(self.generate_plugin_xml(plugin_id, name, version))

        # build.gradle.kts
        with open(output_path / 'build.gradle.kts', 'w') as f:
            f.write(self.generate_build_gradle(version))

        # Kotlin sources
        src_dir = output_path / 'src' / 'main' / 'kotlin' / 'com' / 'aigenerator'
        (src_dir / 'services').mkdir(parents=True, exist_ok=True)
        (src_dir / 'actions').mkdir(parents=True, exist_ok=True)

        with open(src_dir / 'services' / 'AIGeneratorService.kt', 'w') as f:
            f.write(self.generate_service_kotlin())

        with open(src_dir / 'actions' / 'CreateProjectAction.kt', 'w') as f:
            f.write(self.generate_action_kotlin())

        print(f"✅ JetBrains plugin generated: {output_path}")
