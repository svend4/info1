#!/usr/bin/env python3
"""
White Label Module

White-label настройка для партнеров и ресселеров.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BrandingConfig:
    """Конфигурация брендинга"""
    partner_name: str
    company_name: str
    logo_url: str
    favicon_url: str
    primary_color: str
    secondary_color: str
    custom_css: Optional[str] = None
    custom_domain: Optional[str] = None
    email_from_name: Optional[str] = None
    support_email: Optional[str] = None
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class WhiteLabelInstance:
    """White-label инстанс"""
    instance_id: str
    partner_id: str
    branding: BrandingConfig
    features_enabled: List[str]
    custom_features: Dict[str, Any]
    billing_enabled: bool
    analytics_enabled: bool
    created_at: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['branding'] = self.branding.to_dict()
        return data


class WhiteLabelManager:
    """
    White Label Manager

    Управление white-label конфигурациями:
    - Брендинг и кастомизация
    - Фичи и права
    - Настройка UI/UX
    - Интеграция биллинга
    """

    def __init__(self, storage_path: str = './whitelabel'):
        """Инициализация"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.instances: Dict[str, WhiteLabelInstance] = {}
        self._load_instances()

    def _load_instances(self):
        """Загрузка инстансов"""
        instances_file = self.storage_path / 'instances.json'
        if instances_file.exists():
            with open(instances_file, 'r') as f:
                data = json.load(f)
                for inst_data in data.values():
                    branding_data = inst_data['branding']
                    inst_data['branding'] = BrandingConfig(**branding_data)
                    self.instances[inst_data['instance_id']] = WhiteLabelInstance(**inst_data)

    def _save_instances(self):
        """Сохранение инстансов"""
        instances_file = self.storage_path / 'instances.json'
        data = {iid: inst.to_dict() for iid, inst in self.instances.items()}
        with open(instances_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_instance(
        self,
        partner_id: str,
        branding: BrandingConfig,
        features: List[str] = None
    ) -> WhiteLabelInstance:
        """Создание white-label инстанса"""
        import uuid
        from datetime import datetime

        instance_id = str(uuid.uuid4())

        instance = WhiteLabelInstance(
            instance_id=instance_id,
            partner_id=partner_id,
            branding=branding,
            features_enabled=features or [],
            custom_features={},
            billing_enabled=True,
            analytics_enabled=True,
            created_at=datetime.now().isoformat()
        )

        self.instances[instance_id] = instance
        self._save_instances()

        return instance

    def generate_custom_css(self, branding: BrandingConfig) -> str:
        """Генерация кастомного CSS"""
        return f"""
/* White Label Custom CSS */
:root {{
  --primary-color: {branding.primary_color};
  --secondary-color: {branding.secondary_color};
  --brand-name: "{branding.company_name}";
}}

.logo {{
  background-image: url('{branding.logo_url}');
}}

.btn-primary {{
  background-color: var(--primary-color);
}}

.btn-secondary {{
  background-color: var(--secondary_color);
}}

{branding.custom_css or ''}
"""

    def generate_config_file(self, instance_id: str) -> Dict[str, Any]:
        """Генерация конфигурационного файла"""
        if instance_id not in self.instances:
            raise ValueError(f"Instance {instance_id} not found")

        instance = self.instances[instance_id]
        branding = instance.branding

        return {
            'branding': {
                'name': branding.company_name,
                'logo': branding.logo_url,
                'favicon': branding.favicon_url,
                'colors': {
                    'primary': branding.primary_color,
                    'secondary': branding.secondary_color
                },
                'domain': branding.custom_domain
            },
            'features': instance.features_enabled,
            'integrations': {
                'billing': instance.billing_enabled,
                'analytics': instance.analytics_enabled
            },
            'email': {
                'from_name': branding.email_from_name or branding.company_name,
                'support_email': branding.support_email
            },
            'legal': {
                'terms_url': branding.terms_url,
                'privacy_url': branding.privacy_url
            }
        }

    def export_package(self, instance_id: str, output_dir: str):
        """Экспорт white-label пакета"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Config
        config = self.generate_config_file(instance_id)
        with open(output_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)

        # Custom CSS
        instance = self.instances[instance_id]
        css = self.generate_custom_css(instance.branding)
        with open(output_path / 'custom.css', 'w') as f:
            f.write(css)

        # Environment file
        env_content = f"""
BRAND_NAME={instance.branding.company_name}
CUSTOM_DOMAIN={instance.branding.custom_domain or ''}
PRIMARY_COLOR={instance.branding.primary_color}
SUPPORT_EMAIL={instance.branding.support_email or ''}
"""
        with open(output_path / '.env', 'w') as f:
            f.write(env_content.strip())

        print(f"✅ White-label package exported to: {output_path}")
