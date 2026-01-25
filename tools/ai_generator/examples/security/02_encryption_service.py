#!/usr/bin/env python3
"""
Example: Encryption Service

This example demonstrates how to use the encryption service
for AES-256-GCM, RSA-4096, ChaCha20-Poly1305, and Argon2 hashing.
"""

from pathlib import Path
from tools.ai_generator.security import (
    EncryptionService,
    EncryptionConfig,
    EncryptionAlgorithm,
    KeyManagement
)


def example_aes_encryption():
    """AES-256-GCM encryption example"""
    print("=" * 60)
    print("Example 1: AES-256-GCM Encryption")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Encrypt sensitive data
    plaintext = "Sensitive customer data: Credit card 4532-****-****-1234"
    encrypted = service.encrypt(plaintext.encode())

    print(f"✅ Data encrypted successfully")
    print(f"📝 Original length: {len(plaintext)} bytes")
    print(f"🔒 Encrypted length: {len(encrypted)} bytes")
    print(f"🔑 Algorithm: AES-256-GCM")
    print(f"🔐 Key size: 256 bits")

    # Decrypt
    decrypted = service.decrypt(encrypted)
    print(f"\n✅ Data decrypted: {decrypted.decode()[:30]}...")
    print()


def example_rsa_encryption():
    """RSA-4096 public key encryption"""
    print("=" * 60)
    print("Example 2: RSA-4096 Public Key Encryption")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.RSA_4096,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Generate key pair
    public_key, private_key = service.generate_key_pair()

    print("✅ RSA-4096 key pair generated")
    print(f"🔑 Public key size: {len(public_key)} bytes")
    print(f"🔐 Private key size: {len(private_key)} bytes")

    # Encrypt with public key
    message = b"Secret message for asymmetric encryption"
    encrypted = service.encrypt_with_public_key(message, public_key)

    print(f"\n✅ Message encrypted with public key")
    print(f"🔒 Ciphertext size: {len(encrypted)} bytes")

    # Decrypt with private key
    decrypted = service.decrypt_with_private_key(encrypted, private_key)
    print(f"✅ Message decrypted: {decrypted.decode()}")
    print()


def example_chacha20_poly1305():
    """ChaCha20-Poly1305 AEAD encryption"""
    print("=" * 60)
    print("Example 3: ChaCha20-Poly1305 AEAD")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Encrypt with additional authenticated data
    plaintext = b"Confidential message"
    aad = b"metadata:user=admin,timestamp=2026-01-25"

    encrypted = service.encrypt_with_aad(plaintext, aad)

    print("✅ ChaCha20-Poly1305 encryption completed")
    print(f"📝 Message: {plaintext.decode()}")
    print(f"🔖 Additional data: {aad.decode()}")
    print(f"🔒 Encrypted size: {len(encrypted)} bytes")
    print("✨ AEAD provides both confidentiality and authenticity")

    # Decrypt
    decrypted = service.decrypt_with_aad(encrypted, aad)
    print(f"\n✅ Decrypted: {decrypted.decode()}")
    print()


def example_password_hashing():
    """Argon2 password hashing"""
    print("=" * 60)
    print("Example 4: Argon2 Password Hashing")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.ARGON2,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Hash passwords
    password = "MySecureP@ssw0rd!"
    hash1 = service.hash_password(password)
    hash2 = service.hash_password(password)  # Different salt = different hash

    print("✅ Password hashed with Argon2")
    print(f"🔐 Hash 1: {hash1[:50]}...")
    print(f"🔐 Hash 2: {hash2[:50]}...")
    print("📝 Same password, different hashes (unique salts)")

    # Verify password
    is_valid = service.verify_password(password, hash1)
    print(f"\n✅ Password verification: {is_valid}")

    # Wrong password
    is_valid_wrong = service.verify_password("WrongPassword", hash1)
    print(f"❌ Wrong password verification: {is_valid_wrong}")
    print()


def example_key_rotation():
    """Demonstrate key rotation"""
    print("=" * 60)
    print("Example 5: Key Rotation")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_management=KeyManagement.LOCAL,
        enable_key_rotation=True,
        rotation_days=90
    )

    service = EncryptionService(config)

    # Encrypt data
    data = b"Data encrypted with key version 1"
    encrypted_v1 = service.encrypt(data)

    print("✅ Data encrypted with key version 1")
    print(f"🔑 Key ID: {service.get_current_key_id()}")

    # Rotate key
    service.rotate_key()
    print("\n🔄 Key rotated to version 2")
    print(f"🔑 New Key ID: {service.get_current_key_id()}")

    # Can still decrypt old data
    decrypted_v1 = service.decrypt(encrypted_v1)
    print(f"✅ Old data still decryptable: {decrypted_v1.decode()}")

    # New encryptions use new key
    encrypted_v2 = service.encrypt(b"Data encrypted with key version 2")
    print(f"✅ New data encrypted with key version 2")
    print()


def example_file_encryption():
    """Encrypt entire files"""
    print("=" * 60)
    print("Example 6: File Encryption")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Create sample file
    test_file = Path("./output/test_document.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Confidential business data\nSalary: $150,000\nSSN: ***-**-1234")

    # Encrypt file
    encrypted_file = service.encrypt_file(test_file, Path("./output/test_document.txt.enc"))

    print(f"✅ File encrypted: {encrypted_file}")
    print(f"📄 Original size: {test_file.stat().st_size} bytes")
    print(f"🔒 Encrypted size: {encrypted_file.stat().st_size} bytes")

    # Decrypt file
    decrypted_file = service.decrypt_file(encrypted_file, Path("./output/test_document_decrypted.txt"))

    print(f"\n✅ File decrypted: {decrypted_file}")
    print(f"📝 Content verified: {decrypted_file.read_text()[:30]}...")
    print()


def example_database_field_encryption():
    """Field-level encryption for databases"""
    print("=" * 60)
    print("Example 7: Database Field Encryption")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_management=KeyManagement.LOCAL
    )

    service = EncryptionService(config)

    # Simulate database records
    users = [
        {"id": 1, "name": "Alice", "ssn": "123-45-6789", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "ssn": "987-65-4321", "email": "bob@example.com"},
    ]

    # Encrypt sensitive fields
    print("Encrypting sensitive database fields...")
    for user in users:
        user["ssn"] = service.encrypt(user["ssn"].encode()).hex()
        user["email"] = service.encrypt(user["email"].encode()).hex()

    print(f"\n✅ Encrypted {len(users)} user records")
    print("🔒 Encrypted SSN sample:", users[0]["ssn"][:50], "...")

    # Decrypt when needed
    print("\nDecrypting for authorized access...")
    for user in users:
        user["ssn"] = service.decrypt(bytes.fromhex(user["ssn"])).decode()
        user["email"] = service.decrypt(bytes.fromhex(user["email"])).decode()

    print(f"✅ Decrypted user: {users[0]['name']}, {users[0]['email']}")
    print()


def example_hsm_integration():
    """Hardware Security Module integration"""
    print("=" * 60)
    print("Example 8: HSM Integration (Enterprise)")
    print("=" * 60)

    config = EncryptionConfig(
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_management=KeyManagement.HSM,
        hsm_config={
            "provider": "AWS CloudHSM",
            "cluster_id": "cluster-abc123"
        }
    )

    service = EncryptionService(config)

    print("✅ Encryption service configured with HSM")
    print("🔐 Key storage: Hardware Security Module")
    print("🏢 Provider: AWS CloudHSM")
    print("📋 Compliance: FIPS 140-2 Level 3")
    print("\n🔑 Keys stored in tamper-resistant hardware")
    print("✨ Suitable for PCI DSS, HIPAA, and other compliance requirements")
    print()


if __name__ == "__main__":
    print("\n🔐 Encryption Service Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_aes_encryption()
    example_rsa_encryption()
    example_chacha20_poly1305()
    example_password_hashing()
    example_key_rotation()
    example_file_encryption()
    example_database_field_encryption()
    example_hsm_integration()

    print("=" * 60)
    print("✅ All encryption examples completed!")
    print("=" * 60)
    print("\n🔒 Security Best Practices:")
    print("   1. Always use authenticated encryption (GCM, Poly1305)")
    print("   2. Rotate keys regularly (90-180 days)")
    print("   3. Use HSM for production environments")
    print("   4. Never log or expose encryption keys")
    print("   5. Use Argon2 for password hashing (not MD5/SHA1)")
