#!/usr/bin/env python3
"""
Template Marketplace CLI

Command-line interface для работы с Template Marketplace:
- Поиск и установка шаблонов
- Публикация своих шаблонов
- Управление отзывами
- Fork шаблонов
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from template_marketplace import (
    TemplateMarketplace,
    TemplateMetadata
)


def create_marketplace(base_path: Optional[Path] = None) -> TemplateMarketplace:
    """Создание marketplace instance"""
    if base_path is None:
        # Default location
        base_path = Path.home() / '.ai_generator' / 'marketplace'

    return TemplateMarketplace(base_path)


def cmd_search(args):
    """Поиск шаблонов"""
    marketplace = create_marketplace(args.marketplace_path)

    results = marketplace.search_templates(
        query=args.query,
        category=args.category,
        tags=args.tags.split(',') if args.tags else None,
        language=args.language,
        min_rating=args.min_rating,
        sort_by=args.sort_by,
        limit=args.limit
    )

    if not results:
        print("❌ No templates found")
        return

    print(f"\n🔍 Found {len(results)} templates:\n")

    for i, template in enumerate(results, 1):
        print(f"{i}. {template.display_name}")
        print(f"   ID: {template.id}")
        print(f"   Category: {template.category} | Language: {template.language}")
        print(f"   Author: {template.author}")
        print(f"   ⭐ {template.rating:.1f}/5.0 ({template.reviews_count} reviews) | 📥 {template.downloads} downloads")
        print(f"   {template.description[:80]}...")

        if template.is_verified:
            print(f"   ✅ Verified")
        if template.is_featured:
            print(f"   ⭐ Featured")

        print()


def cmd_info(args):
    """Подробная информация о шаблоне"""
    marketplace = create_marketplace(args.marketplace_path)

    info = marketplace.get_template_info(args.template_id)

    if not info:
        print(f"❌ Template {args.template_id} not found")
        return

    metadata = TemplateMetadata(**info['metadata'])

    print("\n" + "="*70)
    print(f"📦 {metadata.display_name}")
    print("="*70)

    print(f"\nID: {metadata.id}")
    print(f"Category: {metadata.category}")
    print(f"Language: {metadata.language}")
    if metadata.framework:
        print(f"Framework: {metadata.framework}")

    print(f"\nAuthor: {metadata.author}")
    if metadata.author_email:
        print(f"Email: {metadata.author_email}")

    print(f"\nVersion: {metadata.version}")
    print(f"License: {metadata.license}")

    print(f"\nCreated: {metadata.created_at[:10]}")
    print(f"Updated: {metadata.updated_at[:10]}")

    if metadata.tags:
        print(f"\nTags: {', '.join(metadata.tags)}")

    print(f"\n📊 Statistics:")
    print(f"   Downloads: {metadata.downloads}")
    print(f"   Rating: {info['stats']['rating']:.1f}/5.0")
    print(f"   Reviews: {info['stats']['reviews_count']}")

    if metadata.github_url:
        print(f"\n🐙 GitHub: {metadata.github_url}")
    if metadata.homepage_url:
        print(f"🌐 Homepage: {metadata.homepage_url}")

    print(f"\nDescription:")
    print(f"{metadata.description}")

    # Reviews
    if info['reviews']:
        print(f"\n📝 Recent Reviews:")
        for review_data in info['reviews'][:3]:
            print(f"\n   {'⭐' * review_data['rating']} - {review_data['title']}")
            print(f"   by {review_data['author']} on {review_data['created_at'][:10]}")
            print(f"   {review_data['comment'][:100]}...")
            if review_data['helpful_count'] > 0:
                print(f"   👍 {review_data['helpful_count']} found helpful")

    print("\n" + "="*70)


def cmd_install(args):
    """Установка шаблона"""
    marketplace = create_marketplace(args.marketplace_path)

    output_dir = Path(args.output) if args.output else Path.cwd()

    try:
        project_path = marketplace.install_template(
            template_id=args.template_id,
            destination=output_dir,
            project_name=args.name
        )

        print(f"\n✅ Template installed successfully!")
        print(f"   Location: {project_path}")
        print(f"\nNext steps:")
        print(f"  cd {project_path}")
        print(f"  # Start coding!")

    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        sys.exit(1)


def cmd_publish(args):
    """Публикация шаблона"""
    marketplace = create_marketplace(args.marketplace_path)

    source_path = Path(args.source)

    if not source_path.exists():
        print(f"❌ Source path does not exist: {source_path}")
        sys.exit(1)

    metadata = {
        'name': args.name,
        'display_name': args.display_name or args.name,
        'description': args.description,
        'author': args.author,
        'author_email': args.email,
        'category': args.category,
        'language': args.language,
        'framework': args.framework,
        'version': args.version or '1.0.0',
        'license': args.license or 'MIT',
        'tags': args.tags.split(',') if args.tags else [],
        'github_url': args.github_url,
        'homepage_url': args.homepage_url
    }

    try:
        template_id = marketplace.publish_template(source_path, metadata)

        print(f"\n🎉 Template published successfully!")
        print(f"   Template ID: {template_id}")
        print(f"   Name: {metadata['name']}")
        print(f"\nOthers can now install it with:")
        print(f"  marketplace-cli install {template_id}")

    except Exception as e:
        print(f"❌ Publication failed: {str(e)}")
        sys.exit(1)


def cmd_fork(args):
    """Fork шаблона"""
    marketplace = create_marketplace(args.marketplace_path)

    new_metadata = {
        'name': args.name,
        'author': args.author,
        'description': args.description
    }

    if args.category:
        new_metadata['category'] = args.category
    if args.tags:
        new_metadata['tags'] = args.tags.split(',')

    try:
        new_template_id = marketplace.fork_template(args.template_id, new_metadata)

        print(f"\n🍴 Template forked successfully!")
        print(f"   New template ID: {new_template_id}")
        print(f"   Name: {args.name}")
        print(f"\nYou can now modify and publish it")

    except Exception as e:
        print(f"❌ Fork failed: {str(e)}")
        sys.exit(1)


def cmd_review(args):
    """Добавление отзыва"""
    marketplace = create_marketplace(args.marketplace_path)

    try:
        marketplace.add_review(
            template_id=args.template_id,
            author=args.author,
            rating=args.rating,
            title=args.title,
            comment=args.comment
        )

        print(f"\n✅ Review added successfully!")
        print(f"   Rating: {'⭐' * args.rating}")

    except Exception as e:
        print(f"❌ Review failed: {str(e)}")
        sys.exit(1)


def cmd_featured(args):
    """Показать featured шаблоны"""
    marketplace = create_marketplace(args.marketplace_path)

    featured = marketplace.registry.get_featured(limit=args.limit)

    if not featured:
        print("❌ No featured templates")
        return

    print(f"\n⭐ Featured Templates:\n")

    for i, template in enumerate(featured, 1):
        print(f"{i}. {template.display_name}")
        print(f"   ID: {template.id}")
        print(f"   {template.description[:80]}...")
        print(f"   ⭐ {template.rating:.1f}/5.0 | 📥 {template.downloads} downloads")
        print()


def cmd_popular(args):
    """Показать популярные шаблоны"""
    marketplace = create_marketplace(args.marketplace_path)

    popular = marketplace.registry.get_popular(limit=args.limit)

    if not popular:
        print("❌ No templates found")
        return

    print(f"\n🔥 Popular Templates:\n")

    for i, template in enumerate(popular, 1):
        print(f"{i}. {template.display_name}")
        print(f"   📥 {template.downloads} downloads | ⭐ {template.rating:.1f}/5.0")
        print(f"   {template.description[:80]}...")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Template Marketplace CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--marketplace-path',
        type=Path,
        help='Path to marketplace directory (default: ~/.ai_generator/marketplace)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search templates')
    search_parser.add_argument('--query', help='Search query')
    search_parser.add_argument('--category', help='Category filter')
    search_parser.add_argument('--tags', help='Tags filter (comma-separated)')
    search_parser.add_argument('--language', help='Language filter')
    search_parser.add_argument('--min-rating', type=float, default=0.0, help='Minimum rating')
    search_parser.add_argument('--sort-by', default='downloads',
                               choices=['downloads', 'rating', 'created_at', 'updated_at'])
    search_parser.add_argument('--limit', type=int, default=20, help='Max results')
    search_parser.set_defaults(func=cmd_search)

    # Info command
    info_parser = subparsers.add_parser('info', help='Template information')
    info_parser.add_argument('template_id', help='Template ID')
    info_parser.set_defaults(func=cmd_info)

    # Install command
    install_parser = subparsers.add_parser('install', help='Install template')
    install_parser.add_argument('template_id', help='Template ID')
    install_parser.add_argument('--name', help='Project name')
    install_parser.add_argument('--output', help='Output directory')
    install_parser.set_defaults(func=cmd_install)

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish template')
    publish_parser.add_argument('source', help='Source directory')
    publish_parser.add_argument('--name', required=True, help='Template name')
    publish_parser.add_argument('--display-name', help='Display name')
    publish_parser.add_argument('--description', required=True, help='Description')
    publish_parser.add_argument('--author', required=True, help='Author name')
    publish_parser.add_argument('--email', help='Author email')
    publish_parser.add_argument('--category', required=True, help='Category')
    publish_parser.add_argument('--language', required=True, help='Language')
    publish_parser.add_argument('--framework', help='Framework')
    publish_parser.add_argument('--version', help='Version (default: 1.0.0)')
    publish_parser.add_argument('--license', help='License (default: MIT)')
    publish_parser.add_argument('--tags', help='Tags (comma-separated)')
    publish_parser.add_argument('--github-url', help='GitHub URL')
    publish_parser.add_argument('--homepage-url', help='Homepage URL')
    publish_parser.set_defaults(func=cmd_publish)

    # Fork command
    fork_parser = subparsers.add_parser('fork', help='Fork template')
    fork_parser.add_argument('template_id', help='Template ID to fork')
    fork_parser.add_argument('--name', required=True, help='New template name')
    fork_parser.add_argument('--author', required=True, help='Your name')
    fork_parser.add_argument('--description', help='Description')
    fork_parser.add_argument('--category', help='Category')
    fork_parser.add_argument('--tags', help='Tags (comma-separated)')
    fork_parser.set_defaults(func=cmd_fork)

    # Review command
    review_parser = subparsers.add_parser('review', help='Add review')
    review_parser.add_argument('template_id', help='Template ID')
    review_parser.add_argument('--author', required=True, help='Your name')
    review_parser.add_argument('--rating', type=int, required=True, choices=[1,2,3,4,5],
                               help='Rating (1-5)')
    review_parser.add_argument('--title', required=True, help='Review title')
    review_parser.add_argument('--comment', required=True, help='Review comment')
    review_parser.set_defaults(func=cmd_review)

    # Featured command
    featured_parser = subparsers.add_parser('featured', help='Show featured templates')
    featured_parser.add_argument('--limit', type=int, default=10, help='Max results')
    featured_parser.set_defaults(func=cmd_featured)

    # Popular command
    popular_parser = subparsers.add_parser('popular', help='Show popular templates')
    popular_parser.add_argument('--limit', type=int, default=10, help='Max results')
    popular_parser.set_defaults(func=cmd_popular)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
