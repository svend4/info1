"""
Integration tests for Security & Compliance modules
"""

import pytest
from pathlib import Path
from tools.ai_generator.security import (
    SSOGenerator, SSOConfig, SSOProvider,
    EncryptionService, EncryptionConfig, EncryptionAlgorithm,
    ComplianceGenerator, ComplianceFramework, ComplianceConfig,
    VulnerabilityScanner,
    ZeroTrustGenerator, ZeroTrustConfig, ZeroTrustProvider,
    SecretsManager, SecretsConfig, SecretsProvider
)


@pytest.mark.integration
@pytest.mark.security
class TestSSOIntegration:
    """Integration tests for SSO/SAML generation"""

    def test_okta_sso_generation(self, temp_dir):
        """Test Okta SSO configuration generation"""
        config = SSOConfig(
            provider=SSOProvider.OKTA,
            entity_id="https://test.example.com",
            acs_url="https://test.example.com/saml/acs"
        )

        generator = SSOGenerator(config)
        files = generator.generate(temp_dir)

        assert len(files) > 0
        assert any("config" in str(f).lower() for f in files.keys())

    def test_multiple_providers(self, temp_dir):
        """Test multiple SSO providers"""
        providers = [SSOProvider.OKTA, SSOProvider.AZURE_AD, SSOProvider.GOOGLE_WORKSPACE]

        for provider in providers:
            config = SSOConfig(
                provider=provider,
                entity_id=f"https://test-{provider.value}.example.com",
                acs_url=f"https://test-{provider.value}.example.com/saml/acs"
            )

            generator = SSOGenerator(config)
            files = generator.generate(temp_dir / provider.value)

            assert len(files) > 0


@pytest.mark.integration
@pytest.mark.security
class TestEncryptionIntegration:
    """Integration tests for encryption service"""

    def test_aes_encryption_roundtrip(self):
        """Test AES encryption and decryption"""
        config = EncryptionConfig(algorithm=EncryptionAlgorithm.AES_256_GCM)
        service = EncryptionService(config)

        plaintext = b"Sensitive test data"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext
        assert encrypted != plaintext

    def test_password_hashing(self):
        """Test Argon2 password hashing"""
        config = EncryptionConfig(algorithm=EncryptionAlgorithm.ARGON2)
        service = EncryptionService(config)

        password = "TestPassword123!"
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)

        # Different hashes due to unique salts
        assert hash1 != hash2

        # Both verify correctly
        assert service.verify_password(password, hash1)
        assert service.verify_password(password, hash2)

        # Wrong password fails
        assert not service.verify_password("WrongPassword", hash1)


@pytest.mark.integration
@pytest.mark.security
class TestComplianceIntegration:
    """Integration tests for compliance framework"""

    @pytest.mark.parametrize("framework", [
        ComplianceFramework.SOC2,
        ComplianceFramework.ISO27001,
        ComplianceFramework.GDPR,
        ComplianceFramework.HIPAA
    ])
    def test_compliance_generation(self, framework, temp_dir):
        """Test compliance framework generation"""
        config = ComplianceConfig(
            framework=framework,
            organization="Test Corp"
        )

        generator = ComplianceGenerator(config)
        generator.add_control("Access Control", "AC-001", "Test control")

        files = generator.generate(temp_dir / framework.value)

        assert len(files) > 0


@pytest.mark.integration
@pytest.mark.security
class TestVulnerabilityScannerIntegration:
    """Integration tests for vulnerability scanner"""

    def test_dependency_scanning(self, temp_dir):
        """Test dependency vulnerability scanning"""
        # Create mock requirements.txt
        requirements_file = temp_dir / "requirements.txt"
        requirements_file.write_text("requests==2.25.0\nflask==1.1.0\n")

        scanner = VulnerabilityScanner()
        results = scanner.scan_dependencies(
            file_path=requirements_file,
            language="python"
        )

        assert results.total_packages >= 0
        assert hasattr(results, 'vulnerabilities')

    def test_code_scanning(self, temp_dir, sample_code):
        """Test static code analysis"""
        # Create test file
        test_file = temp_dir / "test_code.py"
        test_file.write_text(sample_code)

        scanner = VulnerabilityScanner()
        results = scanner.scan_code(
            directory=temp_dir,
            languages=["python"]
        )

        assert results.files_scanned > 0


@pytest.mark.integration
@pytest.mark.security
class TestZeroTrustIntegration:
    """Integration tests for Zero Trust architecture"""

    def test_basic_zero_trust_setup(self, temp_dir):
        """Test basic Zero Trust configuration"""
        config = ZeroTrustConfig(
            provider=ZeroTrustProvider.BEYONDCORP,
            enable_device_trust=True
        )

        generator = ZeroTrustGenerator(config)
        files = generator.generate(temp_dir)

        assert len(files) > 0

    def test_network_microsegmentation(self, temp_dir):
        """Test network microsegmentation"""
        config = ZeroTrustConfig(
            provider=ZeroTrustProvider.BEYONDCORP,
            enable_network_microsegmentation=True
        )

        generator = ZeroTrustGenerator(config)

        # Add network segments
        generator.add_segment("dmz", "Public", ["web"])
        generator.add_segment("app", "Application", ["api"])

        files = generator.generate(temp_dir)

        assert len(files) > 0


@pytest.mark.integration
@pytest.mark.security
class TestSecretsManagerIntegration:
    """Integration tests for secrets manager"""

    def test_vault_initialization(self, temp_dir):
        """Test HashiCorp Vault setup"""
        config = SecretsConfig(
            provider=SecretsProvider.HASHICORP_VAULT,
            vault_address="http://localhost:8200"
        )

        manager = SecretsManager(config)

        # Test initialization (mock)
        assert manager is not None

    def test_secret_operations(self):
        """Test secret store and retrieve operations"""
        config = SecretsConfig(provider=SecretsProvider.HASHICORP_VAULT)
        manager = SecretsManager(config)

        # Mock secret operations
        secret_data = {
            "username": "testuser",
            "password": "testpass"
        }

        # Store secret
        manager.store_secret("test/secret", secret_data)

        # Retrieve secret
        retrieved = manager.get_secret("test/secret")

        assert retrieved == secret_data
