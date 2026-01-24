#!/usr/bin/env python3
"""
Export Validator (ЭТАП 7: Коллективный интеллект)

Валидация MEP v7.0 exports против JSON Schema.

Ключевые функции:
1. Загрузка JSON Schema из metrics_export_schema.json
2. Валидация export файлов
3. Детальные сообщения об ошибках
4. Проверка всех exports в collective_network/

Уровень абстракции: α=-4 (исполняемый код)
Статус: ⇓ ВНИЗ (валидация данных)

Вертикальные связи (⇑ к философии и концепциям):
    ⇑ ЭТАП-7-КОЛЛЕКТИВНЫЙ-ИНТЕЛЛЕКТ.md (α=+2) — концепция обмена знаниями
    ⇑ tools/metrics_export_schema.json (α=-2) — схема для валидации

Горизонтальные связи (↔ другие инструменты α=-4):
    ↔ collective_intelligence.py — создает exports
    ↔ pattern_matcher.py — использует validated exports
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Простой валидатор без внешних зависимостей
# (jsonschema требует pip install, используем минимальную валидацию)


class MEPValidator:
    """Валидатор MEP (Methodology Exchange Protocol) v7.0"""

    def __init__(self, schema_path: str = "tools/metrics_export_schema.json"):
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Загрузка JSON Schema"""
        if not self.schema_path.exists():
            print(f"⚠️  Schema not found: {self.schema_path}")
            return {}

        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        print(f"✅ Loaded schema: {self.schema_path}")
        return schema

    def validate_export(self, export_data: Dict) -> Tuple[bool, List[str]]:
        """
        Валидация export данных

        Returns:
            (is_valid, errors)
        """
        errors = []

        # Базовая структура
        required_fields = ['protocol_version', 'project_id', 'timestamp',
                          'project_type', 'metrics', 'privacy']

        for field in required_fields:
            if field not in export_data:
                errors.append(f"Missing required field: '{field}'")

        if errors:
            return False, errors

        # Проверка protocol_version
        if export_data['protocol_version'] != '7.0':
            errors.append(f"Invalid protocol_version: {export_data['protocol_version']} (expected: '7.0')")

        # Проверка project_type
        valid_types = ['library', 'webapp', 'datascience', 'methodology', 'other']
        if export_data['project_type'] not in valid_types:
            errors.append(f"Invalid project_type: {export_data['project_type']} (expected one of: {valid_types})")

        # Проверка метрик
        metrics = export_data['metrics']
        required_metrics = ['cd', 'vt', 'cr', 'db']

        for metric in required_metrics:
            if metric not in metrics:
                errors.append(f"Missing required metric: '{metric}'")
            elif not isinstance(metrics[metric], (int, float)):
                errors.append(f"Invalid metric type: '{metric}' must be a number")

        # Проверка privacy
        privacy = export_data['privacy']
        if 'anonymized' not in privacy:
            errors.append("Missing privacy.anonymized")
        if 'opt_in' not in privacy:
            errors.append("Missing privacy.opt_in")

        return len(errors) == 0, errors

    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Валидация export файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                export_data = json.load(f)

            return self.validate_export(export_data)

        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]

    def validate_directory(self, directory: Path) -> Dict[str, Tuple[bool, List[str]]]:
        """Валидация всех export_*.json в директории"""
        results = {}

        if not directory.exists():
            print(f"⚠️  Directory not found: {directory}")
            return results

        export_files = list(directory.glob("export_*.json"))

        if not export_files:
            print(f"⚠️  No export files found in: {directory}")
            return results

        print(f"\n🔍 Validating {len(export_files)} export files...")

        for export_file in export_files:
            is_valid, errors = self.validate_file(export_file)
            results[export_file.name] = (is_valid, errors)

        return results

    def display_results(self, results: Dict[str, Tuple[bool, List[str]]]):
        """Отображение результатов валидации"""
        print("\n" + "="*70)
        print("VALIDATION RESULTS")
        print("="*70)

        valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
        invalid_count = len(results) - valid_count

        for filename, (is_valid, errors) in sorted(results.items()):
            status = "✅ VALID" if is_valid else "❌ INVALID"
            print(f"\n{status}: {filename}")

            if errors:
                print("  Errors:")
                for error in errors:
                    print(f"    • {error}")

        print("\n" + "="*70)
        print(f"SUMMARY: {valid_count} valid, {invalid_count} invalid (total: {len(results)})")
        print("="*70)

        return invalid_count == 0


def main():
    """Главная функция"""
    print("="*70)
    print("MEP v7.0 EXPORT VALIDATOR")
    print("Methodology Exchange Protocol Validation")
    print("="*70)

    # Валидация collective_network/
    validator = MEPValidator()
    network_dir = Path("collective_network")

    results = validator.validate_directory(network_dir)

    if not results:
        print("\n❌ No exports to validate")
        return 1

    all_valid = validator.display_results(results)

    if all_valid:
        print("\n✅ All exports are valid!")
        return 0
    else:
        print("\n⚠️  Some exports have validation errors")
        return 1


if __name__ == "__main__":
    exit(main())
