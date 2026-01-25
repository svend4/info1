#!/usr/bin/env python3
"""
Unit tests for project_template_generator.py

Tests all 16 project types and various generator options.
"""

import unittest
import os
import shutil
import json
import tempfile
import sys
import subprocess
from pathlib import Path

# Get generator script path
GENERATOR_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_template_generator.py')


class TestProjectTypes(unittest.TestCase):
    """Test generation for all 16 project types"""

    def setUp(self):
        """Create temporary directory for test projects"""
        self.test_dir = tempfile.mkdtemp(prefix='test_templates_')

    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _test_project_type(self, project_type, expected_type_name):
        """Helper method to test a project type"""
        project_name = f"test-{project_type}"
        project_path = os.path.join(self.test_dir, project_name)

        # Generate project using subprocess
        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT,
             '--name', project_name,
             '--type', project_type,
             '--output', self.test_dir],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, f"Generator failed for {project_type}: {result.stderr}")

        # Verify project directory exists
        self.assertTrue(os.path.exists(project_path), f"Project directory not created for {project_type}")

        # Verify required files
        required_files = ['README.md', 'МЕТОДОЛОГИЯ.md', 'METRICS.md', '.methodology.json']
        for file_name in required_files:
            file_path = os.path.join(project_path, file_name)
            self.assertTrue(os.path.exists(file_path), f"Required file {file_name} not found for {project_type}")

        # Verify required directories
        required_dirs = ['01-Концепция', '02-Архитектура', '03-Реализация', 'docs', 'tools']
        for dir_name in required_dirs:
            dir_path = os.path.join(project_path, dir_name)
            self.assertTrue(os.path.isdir(dir_path), f"Required directory {dir_name} not found for {project_type}")

        # Validate .methodology.json
        with open(os.path.join(project_path, '.methodology.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.assertEqual(config['project_name'], project_name)
        self.assertEqual(config['project_type'], project_type)
        self.assertIn('created', config)
        self.assertIn('methodology_version', config)
        self.assertEqual(config['cycle'], 1)

        # Verify README contains project type
        with open(os.path.join(project_path, 'README.md'), 'r', encoding='utf-8') as f:
            readme_content = f.read()
            self.assertIn(expected_type_name, readme_content, f"README doesn't mention project type for {project_type}")

    def test_software_type(self):
        """Test software project generation"""
        self._test_project_type('software', 'Software Project')

    def test_research_type(self):
        """Test research project generation"""
        self._test_project_type('research', 'Research Project')

    def test_business_type(self):
        """Test business project generation"""
        self._test_project_type('business', 'Business Project')

    def test_education_type(self):
        """Test education project generation"""
        self._test_project_type('education', 'Educational Project')

    def test_legal_type(self):
        """Test legal project generation"""
        self._test_project_type('legal', 'Legal Project')

    def test_healthcare_type(self):
        """Test healthcare project generation"""
        self._test_project_type('healthcare', 'Healthcare Project')

    def test_arts_type(self):
        """Test arts project generation"""
        self._test_project_type('arts', 'Arts & Creative Project')

    def test_finance_type(self):
        """Test finance project generation"""
        self._test_project_type('finance', 'Finance Project')

    def test_government_type(self):
        """Test government project generation"""
        self._test_project_type('government', 'Government Project')

    def test_nonprofit_type(self):
        """Test nonprofit project generation"""
        self._test_project_type('nonprofit', 'Nonprofit Project')

    def test_manufacturing_type(self):
        """Test manufacturing project generation"""
        self._test_project_type('manufacturing', 'Manufacturing Project')

    def test_agriculture_type(self):
        """Test agriculture project generation"""
        self._test_project_type('agriculture', 'Agriculture Project')

    def test_sports_type(self):
        """Test sports project generation"""
        self._test_project_type('sports', 'Sports Project')

    def test_hospitality_type(self):
        """Test hospitality project generation"""
        self._test_project_type('hospitality', 'Hospitality & Tourism Project')

    def test_retail_type(self):
        """Test retail project generation"""
        self._test_project_type('retail', 'Retail Project')

    def test_hobby_type(self):
        """Test hobby project generation"""
        self._test_project_type('hobby', 'Hobby & Personal Project')


class TestGeneratorOptions(unittest.TestCase):
    """Test various generator options"""

    def setUp(self):
        """Create temporary directory for test projects"""
        self.test_dir = tempfile.mkdtemp(prefix='test_options_')

    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_templates_option(self):
        """Test --templates option for types that have extended templates"""
        project_name = "test-templates"
        project_type = "research"

        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT,
             '--name', project_name,
             '--type', project_type,
             '--output', self.test_dir,
             '--templates'],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, f"Generator failed: {result.stderr}")

        project_path = os.path.join(self.test_dir, project_name)
        templates_dir = os.path.join(project_path, 'docs', 'templates')

        # Research type should have templates
        self.assertTrue(os.path.exists(templates_dir), "Templates directory not created")

        # Check if at least one template file exists
        template_files = list(Path(templates_dir).glob('*.md'))
        self.assertGreater(len(template_files), 0, "No template files found")

    def test_git_initialization(self):
        """Test git initialization (if git is available)"""
        project_name = "test-git"

        try:
            result = subprocess.run(
                [sys.executable, GENERATOR_SCRIPT,
                 '--name', project_name,
                 '--type', 'software',
                 '--output', self.test_dir,
                 '--git'],
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0, f"Generator failed: {result.stderr}")

            project_path = os.path.join(self.test_dir, project_name)
            git_dir = os.path.join(project_path, '.git')

            # Only check if git is available on system
            if shutil.which('git'):
                self.assertTrue(os.path.exists(git_dir), "Git repository not initialized")
                self.assertTrue(os.path.exists(os.path.join(project_path, '.gitignore')), ".gitignore not created")
        except Exception as e:
            # If git not available, skip this test
            self.skipTest(f"Git not available: {e}")

    def test_custom_output_directory(self):
        """Test custom output directory"""
        custom_dir = os.path.join(self.test_dir, 'custom', 'path')
        project_name = "test-custom-dir"

        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT,
             '--name', project_name,
             '--type', 'software',
             '--output', custom_dir],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, f"Generator failed: {result.stderr}")

        project_path = os.path.join(custom_dir, project_name)
        self.assertTrue(os.path.exists(project_path), "Project not created in custom directory")


class TestDomainSpecificFolders(unittest.TestCase):
    """Test domain-specific folder structures"""

    def setUp(self):
        """Create temporary directory for test projects"""
        self.test_dir = tempfile.mkdtemp(prefix='test_domains_')

    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_software_folders(self):
        """Test software-specific folders"""
        subprocess.run([sys.executable, GENERATOR_SCRIPT,
                       '--name', 'test', '--type', 'software', '--output', self.test_dir],
                      capture_output=True)
        project_path = os.path.join(self.test_dir, 'test')

        expected_folders = ['src', 'tests', 'examples']
        for folder in expected_folders:
            self.assertTrue(os.path.isdir(os.path.join(project_path, folder)),
                          f"Software folder {folder} not created")

    def test_healthcare_folders(self):
        """Test healthcare-specific folders"""
        subprocess.run([sys.executable, GENERATOR_SCRIPT,
                       '--name', 'test', '--type', 'healthcare', '--output', self.test_dir],
                      capture_output=True)
        project_path = os.path.join(self.test_dir, 'test')

        expected_folders = ['protocols', 'cases', 'research']
        for folder in expected_folders:
            self.assertTrue(os.path.isdir(os.path.join(project_path, folder)),
                          f"Healthcare folder {folder} not created")

    def test_research_folders(self):
        """Test research-specific folders"""
        subprocess.run([sys.executable, GENERATOR_SCRIPT,
                       '--name', 'test', '--type', 'research', '--output', self.test_dir],
                      capture_output=True)
        project_path = os.path.join(self.test_dir, 'test')

        expected_folders = ['data', 'experiments', 'publications']
        for folder in expected_folders:
            self.assertTrue(os.path.isdir(os.path.join(project_path, folder)),
                          f"Research folder {folder} not created")

    def test_manufacturing_folders(self):
        """Test manufacturing-specific folders"""
        subprocess.run([sys.executable, GENERATOR_SCRIPT,
                       '--name', 'test', '--type', 'manufacturing', '--output', self.test_dir],
                      capture_output=True)
        project_path = os.path.join(self.test_dir, 'test')

        expected_folders = ['production', 'quality', 'inventory']
        for folder in expected_folders:
            self.assertTrue(os.path.isdir(os.path.join(project_path, folder)),
                          f"Manufacturing folder {folder} not created")


class TestHealthMetrics(unittest.TestCase):
    """Test health_metrics.py integration"""

    def setUp(self):
        """Create temporary directory for test projects"""
        self.test_dir = tempfile.mkdtemp(prefix='test_metrics_')

    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_health_metrics_copied(self):
        """Test that health_metrics.py is copied to project"""
        subprocess.run([sys.executable, GENERATOR_SCRIPT,
                       '--name', 'test', '--type', 'software', '--output', self.test_dir],
                      capture_output=True)
        project_path = os.path.join(self.test_dir, 'test')

        health_metrics = os.path.join(project_path, 'tools', 'health_metrics.py')
        self.assertTrue(os.path.exists(health_metrics), "health_metrics.py not copied")

        # Verify it's executable
        with open(health_metrics, 'r') as f:
            content = f.read()
            self.assertIn('def main', content, "health_metrics.py doesn't contain expected function")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProjectTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratorOptions))
    suite.addTests(loader.loadTestsFromTestCase(TestDomainSpecificFolders))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMetrics))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEMPLATE GENERATOR TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
