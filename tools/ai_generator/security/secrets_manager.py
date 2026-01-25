#!/usr/bin/env python3
"""
Secrets Manager

Управление секретами (HashiCorp Vault integration, secrets rotation).
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
from pathlib import Path
from typing import Dict, List, Optional, Any


class SecretType(Enum):
    """Secret Types"""
    API_KEY = "api_key"
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    OAUTH_TOKEN = "oauth_token"
    GENERIC = "generic"


class SecretStatus(Enum):
    """Secret Status"""
    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


@dataclass
class Secret:
    """Secret Entry"""
    secret_id: str
    name: str
    secret_type: SecretType
    value: str
    status: SecretStatus = SecretStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    rotation_period_days: Optional[int] = None
    last_rotated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def is_expired(self) -> bool:
        """Check if secret is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def should_rotate(self) -> bool:
        """Check if secret should be rotated"""
        if self.rotation_period_days is None:
            return False

        last_rotation = self.last_rotated_at or self.created_at
        return datetime.utcnow() > last_rotation + timedelta(days=self.rotation_period_days)


@dataclass
class SecretVersion:
    """Secret Version for Rotation"""
    version_id: str
    secret_id: str
    value: str
    created_at: datetime
    is_current: bool


@dataclass
class SecretAuditLog:
    """Secret Access Audit Log"""
    log_id: str
    secret_id: str
    action: str  # read, write, delete, rotate
    user_id: str
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecretsManager:
    """Secrets Manager with Vault Integration"""

    def __init__(self,
                 storage_path: Path,
                 vault_url: Optional[str] = None,
                 vault_token: Optional[str] = None,
                 encryption_key: Optional[bytes] = None):
        """
        Инициализация secrets manager

        Args:
            storage_path: Path for local secrets storage
            vault_url: HashiCorp Vault URL (if using Vault)
            vault_token: Vault authentication token
            encryption_key: Master encryption key for local storage
        """
        self.storage_path = storage_path
        self.vault_url = vault_url
        self.vault_token = vault_token
        self.use_vault = vault_url is not None

        # Initialize encryption
        if encryption_key is None:
            encryption_key = self._generate_master_key()
        self.encryption_key = encryption_key

        # In-memory cache
        self.secrets: Dict[str, Secret] = {}
        self.versions: Dict[str, List[SecretVersion]] = {}
        self.audit_logs: List[SecretAuditLog] = []

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load existing secrets
        self._load_secrets()

    def create_secret(self,
                     name: str,
                     value: str,
                     secret_type: SecretType = SecretType.GENERIC,
                     rotation_period_days: Optional[int] = None,
                     tags: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Secret:
        """
        Create new secret

        Args:
            name: Secret name/path
            value: Secret value
            secret_type: Type of secret
            rotation_period_days: Auto-rotation period
            tags: Tags for organization
            metadata: Additional metadata

        Returns:
            Created secret
        """
        secret_id = self._generate_secret_id()

        secret = Secret(
            secret_id=secret_id,
            name=name,
            secret_type=secret_type,
            value=value,
            rotation_period_days=rotation_period_days,
            tags=tags or [],
            metadata=metadata or {}
        )

        # Store secret
        if self.use_vault:
            self._store_in_vault(secret)
        else:
            self._store_locally(secret)

        self.secrets[secret_id] = secret

        # Create initial version
        self._create_version(secret)

        # Audit log
        self._log_access(secret_id, 'create', 'system', True)

        return secret

    def get_secret(self, secret_id: str, user_id: str = 'system') -> Optional[Secret]:
        """
        Retrieve secret

        Args:
            secret_id: Secret ID
            user_id: User requesting the secret

        Returns:
            Secret or None if not found
        """
        secret = self.secrets.get(secret_id)

        if secret is None:
            self._log_access(secret_id, 'read', user_id, False, {'error': 'not_found'})
            return None

        if secret.is_expired():
            self._log_access(secret_id, 'read', user_id, False, {'error': 'expired'})
            return None

        if secret.status == SecretStatus.REVOKED:
            self._log_access(secret_id, 'read', user_id, False, {'error': 'revoked'})
            return None

        self._log_access(secret_id, 'read', user_id, True)
        return secret

    def get_secret_by_name(self, name: str, user_id: str = 'system') -> Optional[Secret]:
        """
        Retrieve secret by name

        Args:
            name: Secret name
            user_id: User requesting the secret

        Returns:
            Secret or None
        """
        for secret in self.secrets.values():
            if secret.name == name and secret.status == SecretStatus.ACTIVE:
                return self.get_secret(secret.secret_id, user_id)
        return None

    def update_secret(self, secret_id: str, new_value: str, user_id: str = 'system') -> bool:
        """
        Update secret value

        Args:
            secret_id: Secret ID
            new_value: New secret value
            user_id: User updating the secret

        Returns:
            True if successful
        """
        secret = self.secrets.get(secret_id)
        if not secret:
            return False

        # Store old value as version
        self._create_version(secret)

        # Update secret
        secret.value = new_value
        secret.updated_at = datetime.utcnow()

        # Persist
        if self.use_vault:
            self._store_in_vault(secret)
        else:
            self._store_locally(secret)

        self._log_access(secret_id, 'update', user_id, True)
        return True

    def rotate_secret(self, secret_id: str, new_value: Optional[str] = None) -> bool:
        """
        Rotate secret (create new version)

        Args:
            secret_id: Secret ID
            new_value: New value (auto-generated if None)

        Returns:
            True if successful
        """
        secret = self.secrets.get(secret_id)
        if not secret:
            return False

        # Mark as rotating
        secret.status = SecretStatus.ROTATING

        # Generate new value if not provided
        if new_value is None:
            new_value = self._generate_secret_value(secret.secret_type)

        # Update with new value
        success = self.update_secret(secret_id, new_value)

        if success:
            secret.status = SecretStatus.ACTIVE
            secret.last_rotated_at = datetime.utcnow()
            self._log_access(secret_id, 'rotate', 'system', True)

        return success

    def delete_secret(self, secret_id: str, user_id: str = 'system') -> bool:
        """
        Delete (revoke) secret

        Args:
            secret_id: Secret ID
            user_id: User deleting the secret

        Returns:
            True if successful
        """
        secret = self.secrets.get(secret_id)
        if not secret:
            return False

        # Mark as revoked (don't actually delete for audit trail)
        secret.status = SecretStatus.REVOKED
        secret.updated_at = datetime.utcnow()

        self._log_access(secret_id, 'delete', user_id, True)
        return True

    def rotate_all_due_secrets(self) -> List[str]:
        """
        Rotate all secrets due for rotation

        Returns:
            List of rotated secret IDs
        """
        rotated = []

        for secret_id, secret in self.secrets.items():
            if secret.should_rotate() and secret.status == SecretStatus.ACTIVE:
                if self.rotate_secret(secret_id):
                    rotated.append(secret_id)

        return rotated

    def list_secrets(self, tags: Optional[List[str]] = None) -> List[Secret]:
        """
        List all active secrets

        Args:
            tags: Filter by tags

        Returns:
            List of secrets
        """
        secrets = [
            s for s in self.secrets.values()
            if s.status == SecretStatus.ACTIVE
        ]

        if tags:
            secrets = [
                s for s in secrets
                if any(tag in s.tags for tag in tags)
            ]

        return secrets

    def get_secret_versions(self, secret_id: str) -> List[SecretVersion]:
        """
        Get all versions of a secret

        Args:
            secret_id: Secret ID

        Returns:
            List of versions
        """
        return self.versions.get(secret_id, [])

    def get_audit_logs(self,
                      secret_id: Optional[str] = None,
                      user_id: Optional[str] = None,
                      since: Optional[datetime] = None) -> List[SecretAuditLog]:
        """
        Get audit logs

        Args:
            secret_id: Filter by secret ID
            user_id: Filter by user ID
            since: Filter by timestamp

        Returns:
            List of audit logs
        """
        logs = self.audit_logs

        if secret_id:
            logs = [log for log in logs if log.secret_id == secret_id]

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        if since:
            logs = [log for log in logs if log.timestamp >= since]

        return logs

    def integrate_with_vault(self, path: str) -> Dict[str, str]:
        """
        Import secrets from HashiCorp Vault

        Args:
            path: Vault path (e.g., 'secret/data/myapp')

        Returns:
            Dictionary of imported secret names to IDs
        """
        if not self.use_vault:
            raise ValueError("Vault not configured")

        # Simulate Vault integration
        # Production: use hvac library
        imported = {}

        # Example secrets to import
        vault_secrets = {
            'database_password': 'postgres://user:pass@localhost/db',
            'api_key': 'sk-1234567890abcdef',
            'encryption_key': secrets.token_hex(32)
        }

        for name, value in vault_secrets.items():
            secret = self.create_secret(
                name=f"{path}/{name}",
                value=value,
                secret_type=SecretType.GENERIC,
                tags=['vault-import']
            )
            imported[name] = secret.secret_id

        return imported

    def export_to_env_file(self, output_path: Path, prefix: str = ""):
        """
        Export secrets to .env file

        Args:
            output_path: Output file path
            prefix: Prefix for environment variables
        """
        lines = []

        for secret in self.list_secrets():
            # Convert name to env var format
            env_name = secret.name.upper().replace('/', '_').replace('-', '_')
            if prefix:
                env_name = f"{prefix}_{env_name}"

            lines.append(f"{env_name}={secret.value}\n")

        with open(output_path, 'w') as f:
            f.writelines(lines)

    def _store_in_vault(self, secret: Secret):
        """Store secret in HashiCorp Vault"""
        # Production: use hvac.Client()
        # For now, fallback to local storage
        self._store_locally(secret)

    def _store_locally(self, secret: Secret):
        """Store secret locally (encrypted)"""
        secret_file = self.storage_path / f"{secret.secret_id}.json"

        # Encrypt secret value
        encrypted_value = self._encrypt(secret.value.encode())

        data = {
            'secret_id': secret.secret_id,
            'name': secret.name,
            'secret_type': secret.secret_type.value,
            'encrypted_value': base64.b64encode(encrypted_value).decode(),
            'status': secret.status.value,
            'created_at': secret.created_at.isoformat(),
            'updated_at': secret.updated_at.isoformat(),
            'expires_at': secret.expires_at.isoformat() if secret.expires_at else None,
            'rotation_period_days': secret.rotation_period_days,
            'last_rotated_at': secret.last_rotated_at.isoformat() if secret.last_rotated_at else None,
            'metadata': secret.metadata,
            'tags': secret.tags
        }

        with open(secret_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_secrets(self):
        """Load secrets from storage"""
        for secret_file in self.storage_path.glob('*.json'):
            try:
                with open(secret_file) as f:
                    data = json.load(f)

                # Decrypt value
                encrypted_value = base64.b64decode(data['encrypted_value'])
                decrypted_value = self._decrypt(encrypted_value).decode()

                secret = Secret(
                    secret_id=data['secret_id'],
                    name=data['name'],
                    secret_type=SecretType(data['secret_type']),
                    value=decrypted_value,
                    status=SecretStatus(data['status']),
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
                    rotation_period_days=data.get('rotation_period_days'),
                    last_rotated_at=datetime.fromisoformat(data['last_rotated_at']) if data.get('last_rotated_at') else None,
                    metadata=data.get('metadata', {}),
                    tags=data.get('tags', [])
                )

                self.secrets[secret.secret_id] = secret

            except Exception:
                continue

    def _create_version(self, secret: Secret):
        """Create new version of secret"""
        version_id = f"{secret.secret_id}_v{len(self.versions.get(secret.secret_id, [])) + 1}"

        version = SecretVersion(
            version_id=version_id,
            secret_id=secret.secret_id,
            value=secret.value,
            created_at=datetime.utcnow(),
            is_current=True
        )

        # Mark previous versions as not current
        if secret.secret_id in self.versions:
            for v in self.versions[secret.secret_id]:
                v.is_current = False

        if secret.secret_id not in self.versions:
            self.versions[secret.secret_id] = []

        self.versions[secret.secret_id].append(version)

    def _log_access(self,
                   secret_id: str,
                   action: str,
                   user_id: str,
                   success: bool,
                   metadata: Dict[str, Any] = None):
        """Log secret access"""
        log = SecretAuditLog(
            log_id=f"log_{secrets.token_hex(8)}",
            secret_id=secret_id,
            action=action,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            success=success,
            metadata=metadata or {}
        )

        self.audit_logs.append(log)

    def _generate_secret_id(self) -> str:
        """Generate unique secret ID"""
        return f"secret_{secrets.token_hex(16)}"

    def _generate_secret_value(self, secret_type: SecretType) -> str:
        """Generate secret value based on type"""
        if secret_type == SecretType.API_KEY:
            return f"sk_{secrets.token_urlsafe(32)}"
        elif secret_type == SecretType.ENCRYPTION_KEY:
            return secrets.token_hex(32)
        elif secret_type == SecretType.DATABASE_CREDENTIAL:
            return secrets.token_urlsafe(24)
        else:
            return secrets.token_urlsafe(32)

    def _generate_master_key(self) -> bytes:
        """Generate master encryption key"""
        # In production, derive from KMS or secure storage
        return secrets.token_bytes(32)

    def _encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data using master key"""
        # Simple XOR encryption for demo
        # Production: use cryptography library (Fernet, AES-GCM)
        key_stream = self._generate_keystream(len(plaintext))
        return bytes(p ^ k for p, k in zip(plaintext, key_stream))

    def _decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data using master key"""
        # XOR is symmetric
        return self._encrypt(ciphertext)

    def _generate_keystream(self, length: int) -> bytes:
        """Generate keystream for encryption"""
        keystream = b''
        counter = 0
        while len(keystream) < length:
            block = hashlib.sha256(self.encryption_key + counter.to_bytes(4, 'big')).digest()
            keystream += block
            counter += 1
        return keystream[:length]
