#!/usr/bin/env python3
"""
Template Metrics

Метрики популярности и успешности templates.
"""

from typing import Dict, List
from collections import defaultdict, Counter


class TemplateMetrics:
    """Template Metrics Analyzer"""

    def __init__(self):
        """Инициализация"""
        self.downloads: Dict[str, int] = defaultdict(int)
        self.ratings: Dict[str, List[float]] = defaultdict(list)
        self.success_rate: Dict[str, float] = {}

    def track_download(self, template_id: str):
        """Отслеживание скачивания"""
        self.downloads[template_id] += 1

    def add_rating(self, template_id: str, rating: float):
        """Добавление рейтинга"""
        self.ratings[template_id].append(rating)

    def set_success_rate(self, template_id: str, rate: float):
        """Установка success rate"""
        self.success_rate[template_id] = rate

    def get_top_templates(self, limit: int = 10) -> List[Dict]:
        """Топ templates"""
        sorted_templates = sorted(
            self.downloads.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {
                'template_id': tid,
                'downloads': count,
                'avg_rating': sum(self.ratings.get(tid, [0])) / len(self.ratings.get(tid, [1])),
                'success_rate': self.success_rate.get(tid, 0.0)
            }
            for tid, count in sorted_templates
        ]

    def get_trending(self, period_days: int = 7) -> List[str]:
        """Trending templates"""
        # Упрощенная версия
        return list(self.downloads.keys())[:5]

    def get_template_analytics(self, template_id: str) -> Dict:
        """Аналитика template"""
        ratings_list = self.ratings.get(template_id, [])
        return {
            'template_id': template_id,
            'total_downloads': self.downloads.get(template_id, 0),
            'avg_rating': sum(ratings_list) / len(ratings_list) if ratings_list else 0,
            'rating_count': len(ratings_list),
            'success_rate': self.success_rate.get(template_id, 0.0),
            'popularity_score': self._calculate_popularity(template_id)
        }

    def _calculate_popularity(self, template_id: str) -> float:
        """Расчет popularity score"""
        downloads = self.downloads.get(template_id, 0)
        ratings = self.ratings.get(template_id, [])
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        success = self.success_rate.get(template_id, 0)

        return (downloads * 0.4) + (avg_rating * 20 * 0.3) + (success * 100 * 0.3)
