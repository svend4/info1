#!/usr/bin/env python3
"""
Template Marketplace

Платформа для обмена и распространения проектных шаблонов:
- User-contributed templates
- Ratings и reviews
- Template discovery и search
- Fork & customize
- Version management
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil


@dataclass
class TemplateMetadata:
    """Метаданные шаблона"""
    id: str
    name: str
    display_name: str
    description: str
    author: str
    author_email: Optional[str]
    version: str
    created_at: str
    updated_at: str
    category: str  # web_app, ml_system, fintech, etc.
    tags: List[str]
    language: str  # python, javascript, java, etc.
    framework: Optional[str]  # django, react, spring, etc.
    license: str
    downloads: int
    rating: float
    reviews_count: int
    github_url: Optional[str]
    homepage_url: Optional[str]
    is_verified: bool  # Проверенный автором
    is_featured: bool  # Featured template


@dataclass
class TemplateReview:
    """Отзыв о шаблоне"""
    id: str
    template_id: str
    author: str
    rating: int  # 1-5
    title: str
    comment: str
    created_at: str
    helpful_count: int


@dataclass
class TemplateVersion:
    """Версия шаблона"""
    version: str
    changelog: str
    released_at: str
    download_url: str


class TemplateRegistry:
    """
    Реестр шаблонов

    Хранит метаданные всех доступных шаблонов.
    """

    def __init__(self, registry_path: Path):
        """
        Args:
            registry_path: Путь к файлу реестра (JSON)
        """
        self.registry_path = Path(registry_path)
        self.templates = self._load_registry()

    def _load_registry(self) -> Dict[str, TemplateMetadata]:
        """Загрузка реестра"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    tid: TemplateMetadata(**tmpl)
                    for tid, tmpl in data.items()
                }
        return {}

    def _save_registry(self):
        """Сохранение реестра"""
        data = {
            tid: asdict(tmpl)
            for tid, tmpl in self.templates.items()
        }

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def register_template(self, metadata: TemplateMetadata):
        """
        Регистрация нового шаблона

        Args:
            metadata: Метаданные шаблона
        """
        if metadata.id in self.templates:
            raise ValueError(f"Template {metadata.id} already registered")

        self.templates[metadata.id] = metadata
        self._save_registry()

        print(f"✅ Registered template: {metadata.name} ({metadata.id})")

    def update_template(self, template_id: str, updates: Dict):
        """
        Обновление метаданных шаблона

        Args:
            template_id: ID шаблона
            updates: Обновления (dict)
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]

        # Обновляем поля
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now().isoformat()

        self._save_registry()
        print(f"✅ Updated template: {template.name}")

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None,
        min_rating: float = 0.0,
        sort_by: str = "downloads",  # downloads, rating, created_at, updated_at
        limit: int = 20
    ) -> List[TemplateMetadata]:
        """
        Поиск шаблонов

        Args:
            query: Текстовый запрос
            category: Категория (web_app, ml_system, etc.)
            tags: Список тегов
            language: Язык программирования
            min_rating: Минимальный рейтинг
            sort_by: Сортировка
            limit: Максимум результатов

        Returns:
            Список подходящих шаблонов
        """
        results = list(self.templates.values())

        # Фильтры
        if query:
            query_lower = query.lower()
            results = [
                t for t in results
                if query_lower in t.name.lower()
                or query_lower in t.description.lower()
                or query_lower in t.display_name.lower()
            ]

        if category:
            results = [t for t in results if t.category == category]

        if tags:
            results = [
                t for t in results
                if any(tag in t.tags for tag in tags)
            ]

        if language:
            results = [t for t in results if t.language == language]

        if min_rating > 0:
            results = [t for t in results if t.rating >= min_rating]

        # Сортировка
        if sort_by == "downloads":
            results.sort(key=lambda t: t.downloads, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda t: t.rating, reverse=True)
        elif sort_by == "created_at":
            results.sort(key=lambda t: t.created_at, reverse=True)
        elif sort_by == "updated_at":
            results.sort(key=lambda t: t.updated_at, reverse=True)

        return results[:limit]

    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Получить шаблон по ID"""
        return self.templates.get(template_id)

    def get_featured(self, limit: int = 10) -> List[TemplateMetadata]:
        """Получить featured шаблоны"""
        featured = [t for t in self.templates.values() if t.is_featured]
        featured.sort(key=lambda t: t.rating, reverse=True)
        return featured[:limit]

    def get_popular(self, limit: int = 10) -> List[TemplateMetadata]:
        """Получить популярные шаблоны"""
        popular = list(self.templates.values())
        popular.sort(key=lambda t: t.downloads, reverse=True)
        return popular[:limit]

    def get_recent(self, limit: int = 10) -> List[TemplateMetadata]:
        """Получить недавние шаблоны"""
        recent = list(self.templates.values())
        recent.sort(key=lambda t: t.created_at, reverse=True)
        return recent[:limit]

    def increment_downloads(self, template_id: str):
        """Увеличить счётчик downloads"""
        if template_id in self.templates:
            self.templates[template_id].downloads += 1
            self._save_registry()


class ReviewManager:
    """
    Управление отзывами

    Handles ratings and reviews for templates.
    """

    def __init__(self, reviews_path: Path):
        """
        Args:
            reviews_path: Путь к файлу с отзывами (JSON)
        """
        self.reviews_path = Path(reviews_path)
        self.reviews = self._load_reviews()

    def _load_reviews(self) -> List[TemplateReview]:
        """Загрузка отзывов"""
        if self.reviews_path.exists():
            with open(self.reviews_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [TemplateReview(**review) for review in data]
        return []

    def _save_reviews(self):
        """Сохранение отзывов"""
        data = [asdict(review) for review in self.reviews]

        self.reviews_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.reviews_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_review(
        self,
        template_id: str,
        author: str,
        rating: int,
        title: str,
        comment: str
    ) -> TemplateReview:
        """
        Добавление отзыва

        Args:
            template_id: ID шаблона
            author: Автор отзыва
            rating: Оценка (1-5)
            title: Заголовок
            comment: Текст отзыва

        Returns:
            Созданный отзыв
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        review_id = hashlib.md5(
            f"{template_id}{author}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        review = TemplateReview(
            id=review_id,
            template_id=template_id,
            author=author,
            rating=rating,
            title=title,
            comment=comment,
            created_at=datetime.now().isoformat(),
            helpful_count=0
        )

        self.reviews.append(review)
        self._save_reviews()

        print(f"✅ Added review for template {template_id}")
        return review

    def get_reviews(self, template_id: str) -> List[TemplateReview]:
        """Получить все отзывы для шаблона"""
        return [r for r in self.reviews if r.template_id == template_id]

    def get_average_rating(self, template_id: str) -> Tuple[float, int]:
        """
        Получить средний рейтинг

        Returns:
            (average_rating, reviews_count)
        """
        template_reviews = self.get_reviews(template_id)

        if not template_reviews:
            return 0.0, 0

        avg_rating = sum(r.rating for r in template_reviews) / len(template_reviews)
        return round(avg_rating, 2), len(template_reviews)

    def mark_helpful(self, review_id: str):
        """Отметить отзыв как полезный"""
        for review in self.reviews:
            if review.id == review_id:
                review.helpful_count += 1
                self._save_reviews()
                break


class TemplateStorage:
    """
    Хранилище шаблонов

    Manages template files and directories.
    """

    def __init__(self, storage_path: Path):
        """
        Args:
            storage_path: Директория для хранения шаблонов
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_template_path(self, template_id: str) -> Path:
        """Получить путь к директории шаблона"""
        return self.storage_path / template_id

    def store_template(
        self,
        template_id: str,
        source_path: Path
    ):
        """
        Сохранение шаблона

        Args:
            template_id: ID шаблона
            source_path: Путь к исходной директории
        """
        template_path = self._get_template_path(template_id)

        if template_path.exists():
            shutil.rmtree(template_path)

        shutil.copytree(source_path, template_path)

        print(f"✅ Stored template: {template_id}")

    def get_template(self, template_id: str) -> Optional[Path]:
        """Получить путь к шаблону"""
        template_path = self._get_template_path(template_id)

        if template_path.exists():
            return template_path

        return None

    def fork_template(
        self,
        template_id: str,
        new_template_id: str
    ) -> Path:
        """
        Fork шаблона

        Args:
            template_id: ID исходного шаблона
            new_template_id: ID нового шаблона

        Returns:
            Путь к новому шаблону
        """
        source_path = self.get_template(template_id)
        if not source_path:
            raise ValueError(f"Template {template_id} not found")

        new_path = self._get_template_path(new_template_id)

        shutil.copytree(source_path, new_path)

        print(f"✅ Forked template: {template_id} → {new_template_id}")
        return new_path

    def delete_template(self, template_id: str):
        """Удаление шаблона"""
        template_path = self._get_template_path(template_id)

        if template_path.exists():
            shutil.rmtree(template_path)
            print(f"✅ Deleted template: {template_id}")


class TemplateMarketplace:
    """
    Главный класс Template Marketplace

    Объединяет все компоненты: registry, reviews, storage.
    """

    def __init__(self, base_path: Path):
        """
        Args:
            base_path: Базовая директория для marketplace
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.registry = TemplateRegistry(self.base_path / "registry.json")
        self.review_manager = ReviewManager(self.base_path / "reviews.json")
        self.storage = TemplateStorage(self.base_path / "templates")

    def publish_template(
        self,
        source_path: Path,
        metadata: Dict
    ) -> str:
        """
        Публикация нового шаблона

        Args:
            source_path: Путь к директории с шаблоном
            metadata: Метаданные (name, description, author, etc.)

        Returns:
            ID созданного шаблона
        """
        # Генерация ID
        template_id = hashlib.md5(
            f"{metadata['name']}{metadata['author']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Создание метаданных
        template_metadata = TemplateMetadata(
            id=template_id,
            name=metadata['name'],
            display_name=metadata.get('display_name', metadata['name']),
            description=metadata['description'],
            author=metadata['author'],
            author_email=metadata.get('author_email'),
            version=metadata.get('version', '1.0.0'),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            category=metadata['category'],
            tags=metadata.get('tags', []),
            language=metadata['language'],
            framework=metadata.get('framework'),
            license=metadata.get('license', 'MIT'),
            downloads=0,
            rating=0.0,
            reviews_count=0,
            github_url=metadata.get('github_url'),
            homepage_url=metadata.get('homepage_url'),
            is_verified=metadata.get('is_verified', False),
            is_featured=metadata.get('is_featured', False)
        )

        # Сохранение в реестр
        self.registry.register_template(template_metadata)

        # Сохранение файлов
        self.storage.store_template(template_id, source_path)

        print(f"🎉 Published template: {metadata['name']} ({template_id})")
        return template_id

    def install_template(
        self,
        template_id: str,
        destination: Path,
        project_name: Optional[str] = None
    ) -> Path:
        """
        Установка шаблона

        Args:
            template_id: ID шаблона
            destination: Куда установить
            project_name: Название проекта (опционально)

        Returns:
            Путь к установленному проекту
        """
        # Получаем шаблон
        template_path = self.storage.get_template(template_id)
        if not template_path:
            raise ValueError(f"Template {template_id} not found")

        # Метаданные
        metadata = self.registry.get_template(template_id)
        if not metadata:
            raise ValueError(f"Template metadata not found")

        # Определяем имя проекта
        if not project_name:
            project_name = metadata.name

        # Копируем
        project_path = destination / project_name
        shutil.copytree(template_path, project_path)

        # Увеличиваем счётчик downloads
        self.registry.increment_downloads(template_id)

        print(f"✅ Installed template: {metadata.display_name}")
        print(f"   Location: {project_path}")

        return project_path

    def fork_template(
        self,
        template_id: str,
        new_metadata: Dict
    ) -> str:
        """
        Fork существующего шаблона

        Args:
            template_id: ID исходного шаблона
            new_metadata: Метаданные нового шаблона

        Returns:
            ID нового шаблона
        """
        # Создаём новый ID
        new_template_id = hashlib.md5(
            f"{new_metadata['name']}{new_metadata['author']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Fork storage
        self.storage.fork_template(template_id, new_template_id)

        # Получаем оригинальные метаданные
        original = self.registry.get_template(template_id)
        if not original:
            raise ValueError(f"Template {template_id} not found")

        # Создаём новые метаданные (наследуем некоторые поля)
        forked_metadata = TemplateMetadata(
            id=new_template_id,
            name=new_metadata['name'],
            display_name=new_metadata.get('display_name', new_metadata['name']),
            description=new_metadata.get('description', f"Fork of {original.display_name}"),
            author=new_metadata['author'],
            author_email=new_metadata.get('author_email'),
            version='1.0.0',  # Новая версия
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            category=new_metadata.get('category', original.category),
            tags=new_metadata.get('tags', original.tags.copy()),
            language=original.language,
            framework=original.framework,
            license=original.license,
            downloads=0,
            rating=0.0,
            reviews_count=0,
            github_url=new_metadata.get('github_url'),
            homepage_url=new_metadata.get('homepage_url'),
            is_verified=False,
            is_featured=False
        )

        # Регистрация
        self.registry.register_template(forked_metadata)

        print(f"🍴 Forked template: {original.display_name} → {new_metadata['name']}")
        return new_template_id

    def add_review(
        self,
        template_id: str,
        author: str,
        rating: int,
        title: str,
        comment: str
    ):
        """
        Добавление отзыва и обновление рейтинга

        Args:
            template_id: ID шаблона
            author: Автор отзыва
            rating: Оценка (1-5)
            title: Заголовок
            comment: Текст
        """
        # Добавляем отзыв
        self.review_manager.add_review(
            template_id, author, rating, title, comment
        )

        # Обновляем рейтинг в метаданных
        avg_rating, reviews_count = self.review_manager.get_average_rating(template_id)

        self.registry.update_template(template_id, {
            'rating': avg_rating,
            'reviews_count': reviews_count
        })

        print(f"✅ Updated rating: {avg_rating:.2f}/5.0 ({reviews_count} reviews)")

    def search_templates(self, **kwargs) -> List[TemplateMetadata]:
        """Поиск шаблонов (проксирует к registry.search)"""
        return self.registry.search(**kwargs)

    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """
        Полная информация о шаблоне

        Returns:
            Dict с metadata, reviews, stats
        """
        metadata = self.registry.get_template(template_id)
        if not metadata:
            return None

        reviews = self.review_manager.get_reviews(template_id)
        avg_rating, reviews_count = self.review_manager.get_average_rating(template_id)

        return {
            'metadata': asdict(metadata),
            'reviews': [asdict(r) for r in reviews],
            'stats': {
                'downloads': metadata.downloads,
                'rating': avg_rating,
                'reviews_count': reviews_count
            }
        }


if __name__ == '__main__':
    print("="*70)
    print("TEMPLATE MARKETPLACE")
    print("="*70)
    print("\nCommunity-driven platform for project templates")
    print("\nUsage:")
    print("  from template_marketplace import TemplateMarketplace")
    print("  marketplace = TemplateMarketplace(Path('./marketplace'))")
    print("  results = marketplace.search_templates(category='web_app')")
    print("\nSee documentation for more examples")
