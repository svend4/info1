#!/usr/bin/env python3
"""
Metrics History Saver (ЭТАП 6: Самосовершенствование)

Сохраняет текущие метрики в историю для последующего анализа трендов.

Использование:
  python3 tools/save_metrics.py

История сохраняется в: tools/metrics_history.json

Уровень абстракции: α=-4 (исполняемый код)
"""

import json
import subprocess
import re
from datetime import datetime
from pathlib import Path


def get_current_metrics():
    """Получает текущие метрики из health_metrics.py"""
    try:
        result = subprocess.run(
            ["python3", "tools/health_metrics.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout
        metrics = {}

        # Парсинг метрик
        cd_match = re.search(r'CD.*?Value:\s+([\d.]+)%', output)
        if cd_match:
            metrics['cd'] = float(cd_match.group(1))

        vt_match = re.search(r'VT.*?Value:\s+([\d.]+)%', output)
        if vt_match:
            metrics['vt'] = float(vt_match.group(1))

        cr_match = re.search(r'CR.*?Value:\s+([\d.]+)', output)
        if cr_match:
            metrics['cr'] = float(cr_match.group(1))

        db_match = re.search(r'DB.*?Value:\s+([\d.]+)%', output)
        if db_match:
            metrics['db'] = float(db_match.group(1))

        docs_match = re.search(r'Total documents:\s+(\d+)', output)
        if docs_match:
            metrics['total_docs'] = int(docs_match.group(1))

        conn_match = re.search(r'Total connections:\s+(\d+)', output)
        if conn_match:
            metrics['total_connections'] = int(conn_match.group(1))

        cycles_match = re.search(r'Total cycles:\s+(\d+)', output)
        if cycles_match:
            metrics['cycle'] = int(cycles_match.group(1))

        metrics['timestamp'] = datetime.now().isoformat()

        return metrics

    except Exception as e:
        print(f"⚠️  Ошибка при получении метрик: {e}")
        return None


def save_to_history(metrics):
    """Сохраняет метрики в файл истории"""
    history_file = Path("tools/metrics_history.json")

    # Загрузка существующей истории
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    # Добавление новых метрик
    history.append(metrics)

    # Сохранение
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"✅ Метрики сохранены в историю")
    print(f"   Записей в истории: {len(history)}")
    print(f"   Файл: {history_file}")


def main():
    """Главная функция"""
    print("📊 Сохранение текущих метрик в историю...")
    print()

    metrics = get_current_metrics()

    if metrics:
        print("Текущие метрики:")
        print(f"  CYCLE: {metrics.get('cycle', 'N/A')}")
        print(f"  CD: {metrics.get('cd', 'N/A')}%")
        print(f"  VT: {metrics.get('vt', 'N/A')}%")
        print(f"  CR: {metrics.get('cr', 'N/A')}")
        print(f"  DB: {metrics.get('db', 'N/A')}%")
        print(f"  Документов: {metrics.get('total_docs', 'N/A')}")
        print(f"  Связей: {metrics.get('total_connections', 'N/A')}")
        print()

        save_to_history(metrics)
        return 0
    else:
        print("❌ Не удалось получить метрики")
        return 1


if __name__ == "__main__":
    exit(main())
