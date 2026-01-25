#!/usr/bin/env python3
"""
ML Feature Store

Централизованное хранилище features для training и inference с versioning.
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union


class FeatureType(Enum):
    """Feature Data Type"""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TIMESTAMP = "timestamp"


class FeatureStatus(Enum):
    """Feature Status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class FeatureDefinition:
    """Feature Definition"""
    feature_name: str
    feature_type: FeatureType
    description: str
    entity: str  # e.g., "user", "product", "transaction"
    version: int = 1
    status: FeatureStatus = FeatureStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    transformation: Optional[str] = None  # Transformation logic
    dependencies: List[str] = field(default_factory=list)  # Dependent features
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureValue:
    """Feature Value with Metadata"""
    entity_id: str
    feature_name: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1


@dataclass
class FeatureSet:
    """Collection of Related Features"""
    feature_set_id: str
    name: str
    features: List[str]  # Feature names
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)


class MLFeatureStore:
    """ML Feature Store - Centralized Feature Management"""

    def __init__(self, storage_path: Path):
        """
        Инициализация feature store

        Args:
            storage_path: Path for feature storage
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.storage_path / "definitions").mkdir(exist_ok=True)
        (self.storage_path / "values").mkdir(exist_ok=True)
        (self.storage_path / "feature_sets").mkdir(exist_ok=True)

        self.features: Dict[str, FeatureDefinition] = {}
        self.feature_sets: Dict[str, FeatureSet] = {}

        self._load_features()

    def register_feature(self,
                        feature_name: str,
                        feature_type: FeatureType,
                        entity: str,
                        description: str = "",
                        created_by: str = "system",
                        tags: List[str] = None,
                        transformation: Optional[str] = None,
                        dependencies: List[str] = None,
                        validation_rules: Dict[str, Any] = None) -> FeatureDefinition:
        """
        Register new feature

        Args:
            feature_name: Feature name
            feature_type: Feature data type
            entity: Entity type
            description: Feature description
            created_by: Creator
            tags: Tags for organization
            transformation: Transformation logic
            dependencies: Dependent features
            validation_rules: Validation rules

        Returns:
            Registered feature definition
        """
        # Check if feature already exists
        if feature_name in self.features:
            existing = self.features[feature_name]
            if existing.status == FeatureStatus.ACTIVE:
                raise ValueError(f"Feature {feature_name} already exists")

            # Create new version
            version = existing.version + 1
        else:
            version = 1

        feature = FeatureDefinition(
            feature_name=feature_name,
            feature_type=feature_type,
            entity=entity,
            description=description,
            version=version,
            created_by=created_by,
            tags=tags or [],
            transformation=transformation,
            dependencies=dependencies or [],
            validation_rules=validation_rules or {}
        )

        self.features[feature_name] = feature
        self._save_feature_definition(feature)

        print(f"✅ Registered feature: {feature_name} v{version}")
        return feature

    def write_features(self,
                      entity_id: str,
                      features: Dict[str, Any],
                      timestamp: Optional[datetime] = None):
        """
        Write feature values

        Args:
            entity_id: Entity ID
            features: Dictionary of feature_name -> value
            timestamp: Feature timestamp
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Validate features
        for feature_name, value in features.items():
            if feature_name not in self.features:
                raise ValueError(f"Unknown feature: {feature_name}")

            feature_def = self.features[feature_name]

            # Validate type
            if not self._validate_type(value, feature_def.feature_type):
                raise ValueError(f"Invalid type for {feature_name}: expected {feature_def.feature_type.value}")

            # Validate rules
            if feature_def.validation_rules:
                self._validate_rules(value, feature_def.validation_rules)

        # Write to storage
        self._write_feature_values(entity_id, features, timestamp)

    def read_features(self,
                     entity_id: str,
                     feature_names: List[str],
                     timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Read feature values

        Args:
            entity_id: Entity ID
            feature_names: Features to read
            timestamp: Point-in-time timestamp (latest if None)

        Returns:
            Dictionary of feature_name -> value
        """
        features = {}

        for feature_name in feature_names:
            if feature_name not in self.features:
                raise ValueError(f"Unknown feature: {feature_name}")

            value = self._read_feature_value(entity_id, feature_name, timestamp)
            features[feature_name] = value

        return features

    def create_feature_set(self,
                          name: str,
                          features: List[str],
                          description: str = "",
                          tags: List[str] = None) -> FeatureSet:
        """
        Create feature set

        Args:
            name: Feature set name
            features: List of feature names
            description: Description
            tags: Tags

        Returns:
            Created feature set
        """
        # Validate features exist
        for feature_name in features:
            if feature_name not in self.features:
                raise ValueError(f"Unknown feature: {feature_name}")

        feature_set = FeatureSet(
            feature_set_id=f"fs_{hashlib.md5(name.encode()).hexdigest()[:8]}",
            name=name,
            features=features,
            description=description,
            tags=tags or []
        )

        self.feature_sets[feature_set.feature_set_id] = feature_set
        self._save_feature_set(feature_set)

        print(f"✅ Created feature set: {name} ({len(features)} features)")
        return feature_set

    def get_feature_set(self,
                       entity_ids: List[str],
                       feature_set_id: str,
                       timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get feature set for multiple entities

        Args:
            entity_ids: List of entity IDs
            feature_set_id: Feature set ID
            timestamp: Point-in-time timestamp

        Returns:
            List of feature dictionaries
        """
        feature_set = self.feature_sets.get(feature_set_id)
        if not feature_set:
            raise ValueError(f"Feature set not found: {feature_set_id}")

        results = []
        for entity_id in entity_ids:
            features = self.read_features(entity_id, feature_set.features, timestamp)
            features['entity_id'] = entity_id
            results.append(features)

        return results

    def materialize_training_dataset(self,
                                    feature_set_id: str,
                                    entity_ids: List[str],
                                    output_path: Path,
                                    format: str = "json") -> Path:
        """
        Materialize training dataset

        Args:
            feature_set_id: Feature set to materialize
            entity_ids: Entity IDs to include
            output_path: Output file path
            format: Output format (json, csv, parquet)

        Returns:
            Path to materialized dataset
        """
        print(f"📦 Materializing training dataset: {feature_set_id}")

        # Get feature values
        dataset = self.get_feature_set(entity_ids, feature_set_id)

        # Save to file
        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(dataset, f, indent=2, default=str)
        elif format == "csv":
            import csv
            if dataset:
                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
                    writer.writeheader()
                    writer.writerows(dataset)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"✅ Materialized {len(dataset)} samples to {output_path}")
        return output_path

    def list_features(self,
                     entity: Optional[str] = None,
                     tags: Optional[List[str]] = None) -> List[FeatureDefinition]:
        """
        List features

        Args:
            entity: Filter by entity
            tags: Filter by tags

        Returns:
            List of feature definitions
        """
        features = list(self.features.values())

        if entity:
            features = [f for f in features if f.entity == entity]

        if tags:
            features = [f for f in features if any(tag in f.tags for tag in tags)]

        return features

    def get_feature_lineage(self, feature_name: str) -> Dict[str, Any]:
        """
        Get feature lineage (dependencies)

        Args:
            feature_name: Feature name

        Returns:
            Lineage information
        """
        feature = self.features.get(feature_name)
        if not feature:
            raise ValueError(f"Feature not found: {feature_name}")

        lineage = {
            'feature_name': feature_name,
            'version': feature.version,
            'entity': feature.entity,
            'dependencies': feature.dependencies,
            'transformation': feature.transformation,
            'downstream_features': []
        }

        # Find features that depend on this one
        for fname, fdef in self.features.items():
            if feature_name in fdef.dependencies:
                lineage['downstream_features'].append(fname)

        return lineage

    def deprecate_feature(self, feature_name: str) -> bool:
        """
        Deprecate feature

        Args:
            feature_name: Feature to deprecate

        Returns:
            True if successful
        """
        feature = self.features.get(feature_name)
        if not feature:
            return False

        feature.status = FeatureStatus.DEPRECATED
        self._save_feature_definition(feature)

        print(f"⚠️  Deprecated feature: {feature_name}")
        return True

    def _validate_type(self, value: Any, feature_type: FeatureType) -> bool:
        """Validate feature value type"""
        if value is None:
            return True

        type_validators = {
            FeatureType.INT: lambda v: isinstance(v, int),
            FeatureType.FLOAT: lambda v: isinstance(v, (int, float)),
            FeatureType.STRING: lambda v: isinstance(v, str),
            FeatureType.BOOLEAN: lambda v: isinstance(v, bool),
            FeatureType.CATEGORICAL: lambda v: isinstance(v, (str, int)),
            FeatureType.EMBEDDING: lambda v: isinstance(v, list),
            FeatureType.TIMESTAMP: lambda v: isinstance(v, (datetime, str, int, float))
        }

        validator = type_validators.get(feature_type)
        return validator(value) if validator else True

    def _validate_rules(self, value: Any, rules: Dict[str, Any]):
        """Validate feature value against rules"""
        if 'min' in rules and value < rules['min']:
            raise ValueError(f"Value {value} below minimum {rules['min']}")

        if 'max' in rules and value > rules['max']:
            raise ValueError(f"Value {value} above maximum {rules['max']}")

        if 'allowed_values' in rules and value not in rules['allowed_values']:
            raise ValueError(f"Value {value} not in allowed values: {rules['allowed_values']}")

    def _write_feature_values(self, entity_id: str, features: Dict[str, Any], timestamp: datetime):
        """Write feature values to storage"""
        # Create entity directory
        entity_dir = self.storage_path / "values" / entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Write features
        for feature_name, value in features.items():
            feature_file = entity_dir / f"{feature_name}.jsonl"

            feature_value = {
                'entity_id': entity_id,
                'feature_name': feature_name,
                'value': value,
                'timestamp': timestamp.isoformat()
            }

            with open(feature_file, 'a') as f:
                f.write(json.dumps(feature_value, default=str) + '\n')

    def _read_feature_value(self,
                           entity_id: str,
                           feature_name: str,
                           timestamp: Optional[datetime] = None) -> Any:
        """Read feature value from storage"""
        feature_file = self.storage_path / "values" / entity_id / f"{feature_name}.jsonl"

        if not feature_file.exists():
            return None

        # Read all values
        values = []
        with open(feature_file) as f:
            for line in f:
                try:
                    value_data = json.loads(line)
                    value_ts = datetime.fromisoformat(value_data['timestamp'])

                    if timestamp is None or value_ts <= timestamp:
                        values.append((value_ts, value_data['value']))
                except:
                    continue

        if not values:
            return None

        # Return latest value before timestamp
        values.sort(key=lambda x: x[0], reverse=True)
        return values[0][1]

    def _save_feature_definition(self, feature: FeatureDefinition):
        """Save feature definition"""
        def_path = self.storage_path / "definitions" / f"{feature.feature_name}.json"

        def_dict = {
            'feature_name': feature.feature_name,
            'feature_type': feature.feature_type.value,
            'entity': feature.entity,
            'description': feature.description,
            'version': feature.version,
            'status': feature.status.value,
            'created_at': feature.created_at.isoformat(),
            'created_by': feature.created_by,
            'tags': feature.tags,
            'metadata': feature.metadata,
            'transformation': feature.transformation,
            'dependencies': feature.dependencies,
            'validation_rules': feature.validation_rules
        }

        with open(def_path, 'w') as f:
            json.dump(def_dict, f, indent=2)

    def _save_feature_set(self, feature_set: FeatureSet):
        """Save feature set"""
        fs_path = self.storage_path / "feature_sets" / f"{feature_set.feature_set_id}.json"

        fs_dict = {
            'feature_set_id': feature_set.feature_set_id,
            'name': feature_set.name,
            'features': feature_set.features,
            'description': feature_set.description,
            'created_at': feature_set.created_at.isoformat(),
            'tags': feature_set.tags
        }

        with open(fs_path, 'w') as f:
            json.dump(fs_dict, f, indent=2)

    def _load_features(self):
        """Load feature definitions"""
        def_dir = self.storage_path / "definitions"
        if not def_dir.exists():
            return

        for def_file in def_dir.glob("*.json"):
            try:
                with open(def_file) as f:
                    data = json.load(f)

                feature = FeatureDefinition(
                    feature_name=data['feature_name'],
                    feature_type=FeatureType(data['feature_type']),
                    entity=data['entity'],
                    description=data.get('description', ''),
                    version=data.get('version', 1),
                    status=FeatureStatus(data.get('status', 'active')),
                    created_at=datetime.fromisoformat(data['created_at']),
                    created_by=data.get('created_by', 'system'),
                    tags=data.get('tags', []),
                    metadata=data.get('metadata', {}),
                    transformation=data.get('transformation'),
                    dependencies=data.get('dependencies', []),
                    validation_rules=data.get('validation_rules', {})
                )

                self.features[feature.feature_name] = feature

            except Exception as e:
                print(f"Warning: Failed to load {def_file}: {e}")

        # Load feature sets
        fs_dir = self.storage_path / "feature_sets"
        if fs_dir.exists():
            for fs_file in fs_dir.glob("*.json"):
                try:
                    with open(fs_file) as f:
                        data = json.load(f)

                    feature_set = FeatureSet(
                        feature_set_id=data['feature_set_id'],
                        name=data['name'],
                        features=data['features'],
                        description=data.get('description', ''),
                        created_at=datetime.fromisoformat(data['created_at']),
                        tags=data.get('tags', [])
                    )

                    self.feature_sets[feature_set.feature_set_id] = feature_set

                except Exception as e:
                    print(f"Warning: Failed to load {fs_file}: {e}")
