#!/usr/bin/env python3
"""
Marketplace & Monetization Module

Монетизация через marketplace template и расширений.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path


class ListingType(Enum):
    """Тип листинга"""
    TEMPLATE = "template"
    PLUGIN = "plugin"
    INTEGRATION = "integration"
    THEME = "theme"


class PricingModel(Enum):
    """Модель ценообразования"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"


@dataclass
class MarketplaceListing:
    """Листинг в marketplace"""
    listing_id: str
    seller_id: str
    title: str
    description: str
    listing_type: ListingType
    pricing_model: PricingModel
    price: float
    commission_rate: float  # %
    downloads: int
    rating: float
    reviews_count: int
    created_at: str
    updated_at: str
    is_verified: bool = False
    is_featured: bool = False

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['listing_type'] = self.listing_type.value
        data['pricing_model'] = self.pricing_model.value
        return data


@dataclass
class Purchase:
    """Покупка"""
    purchase_id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    amount: float
    commission: float
    seller_payout: float
    timestamp: str
    status: str  # 'completed', 'pending', 'refunded'

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PayoutRequest:
    """Запрос на выплату"""
    payout_id: str
    seller_id: str
    amount: float
    status: str
    requested_at: str
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class MarketplaceManager:
    """
    Marketplace Manager

    Управление marketplace:
    - Листинги (templates, plugins, themes)
    - Транзакции и покупки
    - Комиссии и выплаты
    - Рейтинги и отзывы
    - Аналитика продаж
    """

    def __init__(self, storage_path: str = './marketplace'):
        """Инициализация"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.listings: Dict[str, MarketplaceListing] = {}
        self.purchases: Dict[str, Purchase] = {}
        self.payouts: Dict[str, PayoutRequest] = {}

        self._load_data()

    def _load_data(self):
        """Загрузка данных"""
        # Listings
        listings_file = self.storage_path / 'listings.json'
        if listings_file.exists():
            with open(listings_file, 'r') as f:
                data = json.load(f)
                for listing_data in data.values():
                    listing_data['listing_type'] = ListingType(listing_data['listing_type'])
                    listing_data['pricing_model'] = PricingModel(listing_data['pricing_model'])
                    self.listings[listing_data['listing_id']] = MarketplaceListing(**listing_data)

        # Purchases
        purchases_file = self.storage_path / 'purchases.json'
        if purchases_file.exists():
            with open(purchases_file, 'r') as f:
                data = json.load(f)
                for purchase_data in data.values():
                    self.purchases[purchase_data['purchase_id']] = Purchase(**purchase_data)

    def _save_listings(self):
        """Сохранение листингов"""
        listings_file = self.storage_path / 'listings.json'
        data = {lid: listing.to_dict() for lid, listing in self.listings.items()}
        with open(listings_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_purchases(self):
        """Сохранение покупок"""
        purchases_file = self.storage_path / 'purchases.json'
        data = {pid: purchase.to_dict() for pid, purchase in self.purchases.items()}
        with open(purchases_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_listing(
        self,
        seller_id: str,
        title: str,
        description: str,
        listing_type: ListingType,
        price: float,
        pricing_model: PricingModel,
        commission_rate: float = 30.0
    ) -> MarketplaceListing:
        """Создание листинга"""
        import uuid

        listing_id = str(uuid.uuid4())

        listing = MarketplaceListing(
            listing_id=listing_id,
            seller_id=seller_id,
            title=title,
            description=description,
            listing_type=listing_type,
            pricing_model=pricing_model,
            price=price,
            commission_rate=commission_rate,
            downloads=0,
            rating=0.0,
            reviews_count=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.listings[listing_id] = listing
        self._save_listings()

        return listing

    def purchase_listing(
        self,
        listing_id: str,
        buyer_id: str
    ) -> Purchase:
        """Покупка листинга"""
        import uuid

        if listing_id not in self.listings:
            raise ValueError(f"Listing {listing_id} not found")

        listing = self.listings[listing_id]

        # Расчет комиссии
        commission = listing.price * (listing.commission_rate / 100)
        seller_payout = listing.price - commission

        purchase = Purchase(
            purchase_id=str(uuid.uuid4()),
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            amount=listing.price,
            commission=commission,
            seller_payout=seller_payout,
            timestamp=datetime.now().isoformat(),
            status='completed'
        )

        # Обновление статистики
        listing.downloads += 1
        listing.updated_at = datetime.now().isoformat()

        self.purchases[purchase.purchase_id] = purchase
        self._save_purchases()
        self._save_listings()

        return purchase

    def get_seller_earnings(self, seller_id: str) -> Dict[str, Any]:
        """Получение заработка продавца"""
        seller_purchases = [p for p in self.purchases.values() if p.seller_id == seller_id]

        total_revenue = sum(p.amount for p in seller_purchases)
        total_commission = sum(p.commission for p in seller_purchases)
        total_payout = sum(p.seller_payout for p in seller_purchases)

        return {
            'seller_id': seller_id,
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'total_payout': total_payout,
            'total_sales': len(seller_purchases),
            'pending_payout': self._get_pending_payout(seller_id)
        }

    def _get_pending_payout(self, seller_id: str) -> float:
        """Получение pending выплат"""
        completed_purchases = [
            p for p in self.purchases.values()
            if p.seller_id == seller_id and p.status == 'completed'
        ]

        completed_payouts = [
            p for p in self.payouts.values()
            if p.seller_id == seller_id and p.status == 'completed'
        ]

        earned = sum(p.seller_payout for p in completed_purchases)
        paid_out = sum(p.amount for p in completed_payouts)

        return earned - paid_out

    def request_payout(self, seller_id: str) -> PayoutRequest:
        """Запрос на выплату"""
        import uuid

        pending_amount = self._get_pending_payout(seller_id)

        if pending_amount < 100:  # Minimum payout threshold
            raise ValueError(f"Minimum payout is $100. Current: ${pending_amount}")

        payout = PayoutRequest(
            payout_id=str(uuid.uuid4()),
            seller_id=seller_id,
            amount=pending_amount,
            status='pending',
            requested_at=datetime.now().isoformat()
        )

        self.payouts[payout.payout_id] = payout
        return payout

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Общая статистика marketplace"""
        total_listings = len(self.listings)
        total_purchases = len(self.purchases)
        total_revenue = sum(p.amount for p in self.purchases.values())
        total_commission = sum(p.commission for p in self.purchases.values())

        listings_by_type = {}
        for listing in self.listings.values():
            lt = listing.listing_type.value
            listings_by_type[lt] = listings_by_type.get(lt, 0) + 1

        return {
            'total_listings': total_listings,
            'total_purchases': total_purchases,
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'avg_purchase_value': total_revenue / total_purchases if total_purchases > 0 else 0,
            'listings_by_type': listings_by_type,
            'top_listings': self._get_top_listings(5)
        }

    def _get_top_listings(self, limit: int = 5) -> List[Dict]:
        """Топ листингов"""
        sorted_listings = sorted(
            self.listings.values(),
            key=lambda x: (x.downloads, x.rating),
            reverse=True
        )

        return [
            {
                'title': l.title,
                'downloads': l.downloads,
                'rating': l.rating,
                'price': l.price
            }
            for l in sorted_listings[:limit]
        ]

    def search_listings(
        self,
        query: Optional[str] = None,
        listing_type: Optional[ListingType] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None
    ) -> List[MarketplaceListing]:
        """Поиск листингов"""
        results = list(self.listings.values())

        if query:
            results = [l for l in results
                      if query.lower() in l.title.lower() or query.lower() in l.description.lower()]

        if listing_type:
            results = [l for l in results if l.listing_type == listing_type]

        if max_price is not None:
            results = [l for l in results if l.price <= max_price]

        if min_rating is not None:
            results = [l for l in results if l.rating >= min_rating]

        # Сортировка по популярности
        results.sort(key=lambda x: (x.downloads, x.rating), reverse=True)

        return results

    def add_review(
        self,
        listing_id: str,
        rating: float,
        review_text: str,
        user_id: str
    ):
        """Добавление отзыва"""
        if listing_id not in self.listings:
            raise ValueError(f"Listing {listing_id} not found")

        listing = self.listings[listing_id]

        # Обновление рейтинга (простое среднее)
        current_total = listing.rating * listing.reviews_count
        new_total = current_total + rating
        listing.reviews_count += 1
        listing.rating = new_total / listing.reviews_count

        self._save_listings()

    def generate_seller_dashboard(self, seller_id: str) -> Dict[str, Any]:
        """Генерация dashboard для продавца"""
        seller_listings = [l for l in self.listings.values() if l.seller_id == seller_id]
        earnings = self.get_seller_earnings(seller_id)

        return {
            'seller_id': seller_id,
            'total_listings': len(seller_listings),
            'active_listings': sum(1 for l in seller_listings if l.downloads > 0),
            'total_downloads': sum(l.downloads for l in seller_listings),
            'avg_rating': sum(l.rating for l in seller_listings) / len(seller_listings) if seller_listings else 0,
            'earnings': earnings,
            'top_listing': max(seller_listings, key=lambda x: x.downloads) if seller_listings else None
        }
