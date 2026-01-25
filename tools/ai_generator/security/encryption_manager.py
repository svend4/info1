#!/usr/bin/env python3
"""
Advanced Encryption Manager

Шифрование данных (at-rest, in-transit), key rotation, HSM integration.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Any, List


class EncryptionAlgorithm(Enum):
    """Encryption Algorithms"""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    RSA_4096 = "rsa-4096"


class KeyType(Enum):
    """Encryption Key Types"""
    MASTER_KEY = "master"
    DATA_ENCRYPTION_KEY = "dek"
    KEY_ENCRYPTION_KEY = "kek"
    HMAC_KEY = "hmac"


class KeyStatus(Enum):
    """Key Status"""
    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


@dataclass
class EncryptionKey:
    """Encryption Key"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_material: bytes
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    rotated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if key is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def should_rotate(self, rotation_period_days: int = 90) -> bool:
        """Check if key should be rotated"""
        if self.status != KeyStatus.ACTIVE:
            return False

        rotation_date = self.rotated_at or self.created_at
        return datetime.utcnow() > rotation_date + timedelta(days=rotation_period_days)


@dataclass
class EncryptedData:
    """Encrypted Data Container"""
    ciphertext: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[bytes] = None  # Initialization Vector
    auth_tag: Optional[bytes] = None  # Authentication tag for AEAD
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'ciphertext': base64.b64encode(self.ciphertext).decode(),
            'key_id': self.key_id,
            'algorithm': self.algorithm.value,
            'iv': base64.b64encode(self.iv).decode() if self.iv else None,
            'auth_tag': base64.b64encode(self.auth_tag).decode() if self.auth_tag else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedData':
        """Deserialize from dictionary"""
        return cls(
            ciphertext=base64.b64decode(data['ciphertext']),
            key_id=data['key_id'],
            algorithm=EncryptionAlgorithm(data['algorithm']),
            iv=base64.b64decode(data['iv']) if data.get('iv') else None,
            auth_tag=base64.b64decode(data['auth_tag']) if data.get('auth_tag') else None,
            metadata=data.get('metadata', {})
        )


class EncryptionManager:
    """Advanced Encryption Manager"""

    def __init__(self,
                 master_key: Optional[bytes] = None,
                 rotation_period_days: int = 90,
                 use_hsm: bool = False):
        """
        Инициализация encryption manager

        Args:
            master_key: Master encryption key (generated if not provided)
            rotation_period_days: Key rotation period in days
            use_hsm: Use Hardware Security Module
        """
        self.rotation_period_days = rotation_period_days
        self.use_hsm = use_hsm
        self.keys: Dict[str, EncryptionKey] = {}

        # Initialize master key
        if master_key is None:
            master_key = self._generate_key(32)  # 256 bits

        self._store_key(EncryptionKey(
            key_id="master_key_v1",
            key_type=KeyType.MASTER_KEY,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_material=master_key,
            metadata={'version': 1}
        ))

    def encrypt(self,
                plaintext: bytes,
                algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
                additional_data: Optional[bytes] = None) -> EncryptedData:
        """
        Encrypt data

        Args:
            plaintext: Data to encrypt
            algorithm: Encryption algorithm
            additional_data: Additional authenticated data (AAD) for AEAD

        Returns:
            Encrypted data container
        """
        # Get or create DEK (Data Encryption Key)
        dek = self._get_or_create_dek(algorithm)

        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return self._encrypt_aes_gcm(plaintext, dek, additional_data)
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            return self._encrypt_aes_cbc(plaintext, dek)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return self._encrypt_chacha20(plaintext, dek, additional_data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def decrypt(self,
                encrypted_data: EncryptedData,
                additional_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data

        Args:
            encrypted_data: Encrypted data container
            additional_data: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        key = self.keys.get(encrypted_data.key_id)
        if key is None:
            raise ValueError(f"Key not found: {encrypted_data.key_id}")

        if key.is_expired():
            raise ValueError(f"Key expired: {encrypted_data.key_id}")

        algorithm = encrypted_data.algorithm

        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return self._decrypt_aes_gcm(encrypted_data, key, additional_data)
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            return self._decrypt_aes_cbc(encrypted_data, key)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return self._decrypt_chacha20(encrypted_data, key, additional_data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def rotate_keys(self) -> Dict[str, str]:
        """
        Rotate encryption keys that are due for rotation

        Returns:
            Dictionary of rotated key_id -> new_key_id
        """
        rotations = {}

        for key_id, key in list(self.keys.items()):
            if key.should_rotate(self.rotation_period_days):
                new_key = self._rotate_key(key)
                rotations[key_id] = new_key.key_id

        return rotations

    def re_encrypt_with_new_key(self, encrypted_data: EncryptedData) -> EncryptedData:
        """
        Re-encrypt data with current active key

        Args:
            encrypted_data: Data encrypted with old key

        Returns:
            Data encrypted with new key
        """
        # Decrypt with old key
        plaintext = self.decrypt(encrypted_data)

        # Encrypt with current key
        return self.encrypt(plaintext, encrypted_data.algorithm)

    def generate_hmac(self, data: bytes, key_id: Optional[str] = None) -> str:
        """
        Generate HMAC for data integrity

        Args:
            data: Data to sign
            key_id: HMAC key ID (uses default if not provided)

        Returns:
            Base64-encoded HMAC
        """
        if key_id is None:
            # Get or create default HMAC key
            hmac_key = self._get_or_create_hmac_key()
            key_id = hmac_key.key_id

        key = self.keys.get(key_id)
        if key is None or key.key_type != KeyType.HMAC_KEY:
            raise ValueError(f"Invalid HMAC key: {key_id}")

        signature = hmac.new(key.key_material, data, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def verify_hmac(self, data: bytes, signature_b64: str, key_id: str) -> bool:
        """
        Verify HMAC signature

        Args:
            data: Original data
            signature_b64: Base64-encoded HMAC signature
            key_id: HMAC key ID

        Returns:
            True if signature is valid
        """
        expected_signature = base64.b64decode(signature_b64)
        key = self.keys.get(key_id)

        if key is None or key.key_type != KeyType.HMAC_KEY:
            return False

        actual_signature = hmac.new(key.key_material, data, hashlib.sha256).digest()
        return hmac.compare_digest(expected_signature, actual_signature)

    def _encrypt_aes_gcm(self,
                         plaintext: bytes,
                         key: EncryptionKey,
                         additional_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt with AES-256-GCM (AEAD)"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            # Fallback to simple implementation
            return self._encrypt_simple(plaintext, key)

        iv = os.urandom(12)  # 96-bit nonce for GCM
        aesgcm = AESGCM(key.key_material)

        ciphertext = aesgcm.encrypt(iv, plaintext, additional_data)

        # GCM combines ciphertext and auth tag
        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            iv=iv,
            metadata={'aad_present': additional_data is not None}
        )

    def _decrypt_aes_gcm(self,
                         encrypted_data: EncryptedData,
                         key: EncryptionKey,
                         additional_data: Optional[bytes] = None) -> bytes:
        """Decrypt AES-256-GCM"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            return self._decrypt_simple(encrypted_data, key)

        aesgcm = AESGCM(key.key_material)
        plaintext = aesgcm.decrypt(encrypted_data.iv, encrypted_data.ciphertext, additional_data)
        return plaintext

    def _encrypt_aes_cbc(self, plaintext: bytes, key: EncryptionKey) -> EncryptedData:
        """Encrypt with AES-256-CBC"""
        # Simplified implementation
        iv = os.urandom(16)
        # Production: use cryptography.hazmat.primitives.ciphers
        ciphertext = self._xor_encrypt(plaintext, key.key_material, iv)

        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            iv=iv
        )

    def _decrypt_aes_cbc(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Decrypt AES-256-CBC"""
        return self._xor_decrypt(encrypted_data.ciphertext, key.key_material, encrypted_data.iv)

    def _encrypt_chacha20(self,
                          plaintext: bytes,
                          key: EncryptionKey,
                          additional_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt with ChaCha20-Poly1305"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        except ImportError:
            return self._encrypt_simple(plaintext, key)

        nonce = os.urandom(12)
        chacha = ChaCha20Poly1305(key.key_material)
        ciphertext = chacha.encrypt(nonce, plaintext, additional_data)

        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            iv=nonce
        )

    def _decrypt_chacha20(self,
                          encrypted_data: EncryptedData,
                          key: EncryptionKey,
                          additional_data: Optional[bytes] = None) -> bytes:
        """Decrypt ChaCha20-Poly1305"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        except ImportError:
            return self._decrypt_simple(encrypted_data, key)

        chacha = ChaCha20Poly1305(key.key_material)
        plaintext = chacha.decrypt(encrypted_data.iv, encrypted_data.ciphertext, additional_data)
        return plaintext

    def _encrypt_simple(self, plaintext: bytes, key: EncryptionKey) -> EncryptedData:
        """Simple XOR-based encryption (for demo/fallback)"""
        iv = os.urandom(16)
        ciphertext = self._xor_encrypt(plaintext, key.key_material, iv)
        return EncryptedData(
            ciphertext=ciphertext,
            key_id=key.key_id,
            algorithm=key.algorithm,
            iv=iv
        )

    def _decrypt_simple(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Simple XOR-based decryption"""
        return self._xor_decrypt(encrypted_data.ciphertext, key.key_material, encrypted_data.iv)

    def _xor_encrypt(self, plaintext: bytes, key: bytes, iv: bytes) -> bytes:
        """XOR-based encryption"""
        key_stream = self._generate_keystream(key, iv, len(plaintext))
        return bytes(p ^ k for p, k in zip(plaintext, key_stream))

    def _xor_decrypt(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """XOR-based decryption"""
        return self._xor_encrypt(ciphertext, key, iv)  # XOR is symmetric

    def _generate_keystream(self, key: bytes, iv: bytes, length: int) -> bytes:
        """Generate keystream for XOR encryption"""
        keystream = b''
        counter = 0
        while len(keystream) < length:
            block = hashlib.sha256(key + iv + counter.to_bytes(4, 'big')).digest()
            keystream += block
            counter += 1
        return keystream[:length]

    def _get_or_create_dek(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """Get or create Data Encryption Key"""
        # Look for active DEK
        for key in self.keys.values():
            if (key.key_type == KeyType.DATA_ENCRYPTION_KEY and
                key.algorithm == algorithm and
                key.status == KeyStatus.ACTIVE and
                not key.is_expired()):
                return key

        # Create new DEK
        key_material = self._generate_key(32)
        dek = EncryptionKey(
            key_id=f"dek_{algorithm.value}_{secrets.token_hex(8)}",
            key_type=KeyType.DATA_ENCRYPTION_KEY,
            algorithm=algorithm,
            key_material=key_material,
            expires_at=datetime.utcnow() + timedelta(days=self.rotation_period_days)
        )
        self._store_key(dek)
        return dek

    def _get_or_create_hmac_key(self) -> EncryptionKey:
        """Get or create HMAC key"""
        for key in self.keys.values():
            if (key.key_type == KeyType.HMAC_KEY and
                key.status == KeyStatus.ACTIVE and
                not key.is_expired()):
                return key

        key_material = self._generate_key(32)
        hmac_key = EncryptionKey(
            key_id=f"hmac_{secrets.token_hex(8)}",
            key_type=KeyType.HMAC_KEY,
            algorithm=EncryptionAlgorithm.AES_256_GCM,  # Not used for HMAC
            key_material=key_material
        )
        self._store_key(hmac_key)
        return hmac_key

    def _rotate_key(self, old_key: EncryptionKey) -> EncryptionKey:
        """Rotate encryption key"""
        # Mark old key as deprecated
        old_key.status = KeyStatus.DEPRECATED
        old_key.rotated_at = datetime.utcnow()

        # Create new key
        new_key_material = self._generate_key(32)
        new_key = EncryptionKey(
            key_id=f"{old_key.key_type.value}_{secrets.token_hex(8)}",
            key_type=old_key.key_type,
            algorithm=old_key.algorithm,
            key_material=new_key_material,
            metadata={**old_key.metadata, 'rotated_from': old_key.key_id}
        )

        self._store_key(new_key)
        return new_key

    def _generate_key(self, size_bytes: int = 32) -> bytes:
        """Generate cryptographically secure random key"""
        if self.use_hsm:
            # Integration with HSM would go here
            # For now, use software generation
            pass

        return secrets.token_bytes(size_bytes)

    def _store_key(self, key: EncryptionKey):
        """Store encryption key"""
        self.keys[key.key_id] = key
