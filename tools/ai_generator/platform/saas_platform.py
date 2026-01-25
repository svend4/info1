#!/usr/bin/env python3
"""
SaaS Platform Module

Облачная SaaS платформа для AI Project Generator с мультитенантностью.
"""

import json
import uuid
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path


class SubscriptionTier(Enum):
    """Уровни подписки"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class BillingCycle(Enum):
    """Цикл выставления счетов"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class TenantStatus(Enum):
    """Статус тенанта"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


@dataclass
class PricingPlan:
    """План тарификации"""
    tier: SubscriptionTier
    name: str
    monthly_price: float
    yearly_price: float
    features: List[str]
    limits: Dict[str, int]
    support_level: str
    sla_uptime: float  # %

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['tier'] = self.tier.value
        return data


@dataclass
class Tenant:
    """Тенант в SaaS системе"""
    tenant_id: str
    organization_name: str
    domain: str
    subscription_tier: SubscriptionTier
    status: TenantStatus
    created_at: str
    trial_ends_at: Optional[str] = None
    subscription_ends_at: Optional[str] = None
    custom_domain: Optional[str] = None
    branding: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    usage_stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['subscription_tier'] = self.subscription_tier.value
        data['status'] = self.status.value
        return data


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    tenant_id: str
    plan: SubscriptionTier
    billing_cycle: BillingCycle
    status: str
    started_at: str
    next_billing_date: str
    amount: float
    payment_method_id: Optional[str] = None
    auto_renew: bool = True

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['plan'] = self.plan.value
        data['billing_cycle'] = self.billing_cycle.value
        return data


@dataclass
class UsageMetrics:
    """Метрики использования"""
    tenant_id: str
    period_start: str
    period_end: str
    projects_created: int
    api_calls: int
    storage_used_gb: float
    ai_requests: int
    compute_hours: float
    bandwidth_gb: float

    def to_dict(self) -> Dict:
        return asdict(self)


class SaaSPlatform:
    """
    SaaS Platform Manager

    Управление облачной SaaS платформой:
    - Мультитенантность
    - Управление подписками
    - Биллинг
    - Квоты и лимиты
    - Метрики использования
    """

    # Тарифные планы
    PRICING_PLANS = {
        SubscriptionTier.FREE: PricingPlan(
            tier=SubscriptionTier.FREE,
            name="Free",
            monthly_price=0.0,
            yearly_price=0.0,
            features=[
                "5 projects per month",
                "Basic templates",
                "Community support",
                "1 user"
            ],
            limits={
                'projects_per_month': 5,
                'api_calls_per_day': 100,
                'storage_gb': 1,
                'ai_requests_per_month': 50,
                'users': 1
            },
            support_level="community",
            sla_uptime=95.0
        ),

        SubscriptionTier.STARTER: PricingPlan(
            tier=SubscriptionTier.STARTER,
            name="Starter",
            monthly_price=29.0,
            yearly_price=290.0,  # 2 months free
            features=[
                "50 projects per month",
                "All templates",
                "Email support",
                "5 users",
                "Custom branding",
                "API access"
            ],
            limits={
                'projects_per_month': 50,
                'api_calls_per_day': 1000,
                'storage_gb': 10,
                'ai_requests_per_month': 500,
                'users': 5
            },
            support_level="email",
            sla_uptime=99.0
        ),

        SubscriptionTier.PROFESSIONAL: PricingPlan(
            tier=SubscriptionTier.PROFESSIONAL,
            name="Professional",
            monthly_price=99.0,
            yearly_price=990.0,
            features=[
                "Unlimited projects",
                "Premium templates",
                "Priority support",
                "25 users",
                "Custom templates",
                "Advanced analytics",
                "White-label option",
                "SSO integration"
            ],
            limits={
                'projects_per_month': -1,  # unlimited
                'api_calls_per_day': 10000,
                'storage_gb': 100,
                'ai_requests_per_month': 5000,
                'users': 25
            },
            support_level="priority",
            sla_uptime=99.5
        ),

        SubscriptionTier.ENTERPRISE: PricingPlan(
            tier=SubscriptionTier.ENTERPRISE,
            name="Enterprise",
            monthly_price=499.0,
            yearly_price=4990.0,
            features=[
                "Unlimited everything",
                "Dedicated support",
                "Unlimited users",
                "On-premise option",
                "Custom integrations",
                "Dedicated infrastructure",
                "SLA 99.9%",
                "Security audit"
            ],
            limits={
                'projects_per_month': -1,
                'api_calls_per_day': -1,
                'storage_gb': -1,
                'ai_requests_per_month': -1,
                'users': -1
            },
            support_level="dedicated",
            sla_uptime=99.9
        )
    }

    def __init__(self, storage_path: str = './saas_data'):
        """
        Инициализация SaaS платформы

        Args:
            storage_path: Путь для хранения данных
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.tenants: Dict[str, Tenant] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_metrics: Dict[str, List[UsageMetrics]] = {}

        self._load_data()

    def _load_data(self):
        """Загрузка данных из хранилища"""
        # Загрузка тенантов
        tenants_file = self.storage_path / 'tenants.json'
        if tenants_file.exists():
            with open(tenants_file, 'r') as f:
                data = json.load(f)
                for tenant_data in data.values():
                    tenant_data['subscription_tier'] = SubscriptionTier(tenant_data['subscription_tier'])
                    tenant_data['status'] = TenantStatus(tenant_data['status'])
                    self.tenants[tenant_data['tenant_id']] = Tenant(**tenant_data)

        # Загрузка подписок
        subs_file = self.storage_path / 'subscriptions.json'
        if subs_file.exists():
            with open(subs_file, 'r') as f:
                data = json.load(f)
                for sub_data in data.values():
                    sub_data['plan'] = SubscriptionTier(sub_data['plan'])
                    sub_data['billing_cycle'] = BillingCycle(sub_data['billing_cycle'])
                    self.subscriptions[sub_data['subscription_id']] = Subscription(**sub_data)

    def _save_tenants(self):
        """Сохранение тенантов"""
        tenants_file = self.storage_path / 'tenants.json'
        data = {tid: tenant.to_dict() for tid, tenant in self.tenants.items()}
        with open(tenants_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_subscriptions(self):
        """Сохранение подписок"""
        subs_file = self.storage_path / 'subscriptions.json'
        data = {sid: sub.to_dict() for sid, sub in self.subscriptions.items()}
        with open(subs_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_tenant(
        self,
        organization_name: str,
        admin_email: str,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        trial_days: int = 14
    ) -> Tenant:
        """
        Создание нового тенанта

        Args:
            organization_name: Название организации
            admin_email: Email администратора
            tier: Уровень подписки
            trial_days: Дни пробного периода

        Returns:
            Созданный тенант
        """
        tenant_id = str(uuid.uuid4())
        domain = self._generate_subdomain(organization_name)

        # Trial period для платных планов
        trial_ends = None
        status = TenantStatus.ACTIVE

        if tier != SubscriptionTier.FREE:
            trial_ends = (datetime.now() + timedelta(days=trial_days)).isoformat()
            status = TenantStatus.TRIAL

        tenant = Tenant(
            tenant_id=tenant_id,
            organization_name=organization_name,
            domain=domain,
            subscription_tier=tier,
            status=status,
            created_at=datetime.now().isoformat(),
            trial_ends_at=trial_ends,
            settings={
                'admin_email': admin_email,
                'timezone': 'UTC',
                'language': 'en'
            },
            usage_stats={
                'projects_created': 0,
                'api_calls': 0,
                'storage_used_gb': 0
            }
        )

        self.tenants[tenant_id] = tenant
        self._save_tenants()

        # Создание начальной подписки
        self._create_subscription(tenant_id, tier)

        return tenant

    def _generate_subdomain(self, org_name: str) -> str:
        """Генерация субдомена из названия организации"""
        # Преобразование в slug
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', org_name.lower())
        slug = slug.strip('-')

        # Проверка уникальности
        base_slug = slug
        counter = 1
        while any(t.domain == f"{slug}.aigenerator.app" for t in self.tenants.values()):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return f"{slug}.aigenerator.app"

    def _create_subscription(
        self,
        tenant_id: str,
        tier: SubscriptionTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> Subscription:
        """Создание подписки"""
        plan = self.PRICING_PLANS[tier]
        subscription_id = str(uuid.uuid4())

        amount = plan.monthly_price if billing_cycle == BillingCycle.MONTHLY else plan.yearly_price
        next_billing = datetime.now() + timedelta(days=30 if billing_cycle == BillingCycle.MONTHLY else 365)

        subscription = Subscription(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            plan=tier,
            billing_cycle=billing_cycle,
            status='active',
            started_at=datetime.now().isoformat(),
            next_billing_date=next_billing.isoformat(),
            amount=amount
        )

        self.subscriptions[subscription_id] = subscription
        self._save_subscriptions()

        return subscription

    def upgrade_tenant(self, tenant_id: str, new_tier: SubscriptionTier) -> bool:
        """
        Обновление тарифа тенанта

        Args:
            tenant_id: ID тенанта
            new_tier: Новый уровень подписки

        Returns:
            True если успешно
        """
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")

        tenant = self.tenants[tenant_id]
        old_tier = tenant.subscription_tier

        # Проверка апгрейда (нельзя даунгрейдить просто так)
        tier_order = [SubscriptionTier.FREE, SubscriptionTier.STARTER,
                     SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]

        if tier_order.index(new_tier) < tier_order.index(old_tier):
            raise ValueError("Use downgrade_tenant() for downgrading")

        # Обновление тенанта
        tenant.subscription_tier = new_tier
        tenant.status = TenantStatus.ACTIVE
        self._save_tenants()

        # Создание новой подписки
        self._create_subscription(tenant_id, new_tier)

        return True

    def check_quota(self, tenant_id: str, resource: str, amount: int = 1) -> bool:
        """
        Проверка квоты ресурса

        Args:
            tenant_id: ID тенанта
            resource: Тип ресурса
            amount: Количество

        Returns:
            True если в пределах квоты
        """
        if tenant_id not in self.tenants:
            return False

        tenant = self.tenants[tenant_id]
        plan = self.PRICING_PLANS[tenant.subscription_tier]
        limits = plan.limits

        # -1 означает unlimited
        if resource not in limits:
            return True

        limit = limits[resource]
        if limit == -1:
            return True

        # Проверка текущего использования
        current_usage = tenant.usage_stats.get(resource, 0)
        return (current_usage + amount) <= limit

    def track_usage(self, tenant_id: str, resource: str, amount: int = 1):
        """
        Отслеживание использования ресурса

        Args:
            tenant_id: ID тенанта
            resource: Тип ресурса
            amount: Количество
        """
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")

        # Проверка квоты
        if not self.check_quota(tenant_id, resource, amount):
            raise ValueError(f"Quota exceeded for {resource}")

        # Обновление статистики
        tenant = self.tenants[tenant_id]
        current = tenant.usage_stats.get(resource, 0)
        tenant.usage_stats[resource] = current + amount

        self._save_tenants()

    def get_tenant_analytics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Получение аналитики тенанта

        Args:
            tenant_id: ID тенанта

        Returns:
            Аналитика
        """
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")

        tenant = self.tenants[tenant_id]
        plan = self.PRICING_PLANS[tenant.subscription_tier]

        # Расчет использования в %
        usage_percentages = {}
        for resource, limit in plan.limits.items():
            if limit == -1:
                usage_percentages[resource] = 0.0  # unlimited
            else:
                current = tenant.usage_stats.get(resource, 0)
                usage_percentages[resource] = (current / limit * 100) if limit > 0 else 0.0

        return {
            'tenant_id': tenant_id,
            'organization': tenant.organization_name,
            'tier': tenant.subscription_tier.value,
            'status': tenant.status.value,
            'usage_stats': tenant.usage_stats,
            'usage_percentages': usage_percentages,
            'limits': plan.limits,
            'days_until_renewal': self._days_until_renewal(tenant_id)
        }

    def _days_until_renewal(self, tenant_id: str) -> Optional[int]:
        """Дни до обновления подписки"""
        # Поиск активной подписки
        for sub in self.subscriptions.values():
            if sub.tenant_id == tenant_id and sub.status == 'active':
                next_billing = datetime.fromisoformat(sub.next_billing_date)
                delta = next_billing - datetime.now()
                return delta.days

        return None

    def suspend_tenant(self, tenant_id: str, reason: str = ""):
        """Приостановка тенанта"""
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")

        self.tenants[tenant_id].status = TenantStatus.SUSPENDED
        self._save_tenants()

    def reactivate_tenant(self, tenant_id: str):
        """Реактивация тенанта"""
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")

        self.tenants[tenant_id].status = TenantStatus.ACTIVE
        self._save_tenants()

    def get_pricing_plans(self) -> List[Dict]:
        """Получение всех тарифных планов"""
        return [plan.to_dict() for plan in self.PRICING_PLANS.values()]

    def calculate_monthly_revenue(self) -> float:
        """Расчет месячного дохода"""
        revenue = 0.0

        for sub in self.subscriptions.values():
            if sub.status == 'active':
                if sub.billing_cycle == BillingCycle.MONTHLY:
                    revenue += sub.amount
                elif sub.billing_cycle == BillingCycle.YEARLY:
                    revenue += sub.amount / 12

        return revenue

    def get_platform_stats(self) -> Dict[str, Any]:
        """Получение общей статистики платформы"""
        total_tenants = len(self.tenants)
        active_tenants = sum(1 for t in self.tenants.values() if t.status == TenantStatus.ACTIVE)

        tenants_by_tier = {}
        for tenant in self.tenants.values():
            tier = tenant.subscription_tier.value
            tenants_by_tier[tier] = tenants_by_tier.get(tier, 0) + 1

        return {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'trial_tenants': sum(1 for t in self.tenants.values() if t.status == TenantStatus.TRIAL),
            'suspended_tenants': sum(1 for t in self.tenants.values() if t.status == TenantStatus.SUSPENDED),
            'tenants_by_tier': tenants_by_tier,
            'monthly_revenue': self.calculate_monthly_revenue(),
            'total_subscriptions': len(self.subscriptions),
            'active_subscriptions': sum(1 for s in self.subscriptions.values() if s.status == 'active')
        }
