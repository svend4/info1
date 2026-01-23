#!/usr/bin/env python3
"""
Модуль автоматизации для системы карточек

Реализует автоматические задачи и напоминания для карточной системы.
Уровень абстракции: α=-4 (исполняемый код)

Функционал:
- Автоматическая проверка просроченных задач
- Генерация напоминаний о приёме лекарств
- Автоматическое создание повторяющихся задач
- Архивирование старых завершённых карточек
- Генерация еженедельных/ежемесячных отчётов
- Автоматическое создание резервных копий

Связи:
- ⇑ УНИВЕРСАЛЬНЫЕ-ЗАКОНЫ.md — реализует Закон автоматизации рутины
- ⇑ ЗАКОНЫ-В-КОДЕ.md — автоматизация через код
- ⇑ 04-Бытовые-циклы/ — автоматизация циклических задач
- ↔ card_manager.py — использует CardManager для операций
- ↔ export_import.py — использует для backup
"""

from pathlib import Path
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
import json
import logging
from enum import Enum

from card import Card, TaskCard, MedicineCard, CardStatus, Priority, CardType
from card_manager import CardManager
from export_import import CardExporter


# ============================================================================
# Настройка логирования
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Типы и настройки автоматизации
# ============================================================================

class AutomationFrequency(Enum):
    """Частота выполнения автоматических задач"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReminderType(Enum):
    """Типы напоминаний"""
    MEDICINE = "medicine"          # Напоминание о лекарстве
    TASK_DUE = "task_due"         # Задача подходит к сроку
    TASK_OVERDUE = "task_overdue"  # Задача просрочена
    APPOINTMENT = "appointment"    # Предстоящая встреча
    SHOPPING = "shopping"          # Время делать покупки


@dataclass
class Reminder:
    """Напоминание для пользователя"""
    type: ReminderType
    card_id: str
    title: str
    message: str
    priority: Priority
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Строковое представление напоминания"""
        icon = {
            Priority.LOW: "📋",
            Priority.MEDIUM: "⚠️",
            Priority.HIGH: "🔥",
            Priority.URGENT: "🚨"
        }.get(self.priority, "📋")

        return f"{icon} [{self.type.value.upper()}] {self.title}: {self.message}"


@dataclass
class AutomationTask:
    """Автоматическая задача"""
    name: str
    frequency: AutomationFrequency
    action: Callable
    last_run: Optional[datetime] = None
    enabled: bool = True

    def should_run(self) -> bool:
        """Проверить, нужно ли запускать задачу"""
        if not self.enabled:
            return False

        if self.last_run is None:
            return True

        now = datetime.now()
        delta = now - self.last_run

        if self.frequency == AutomationFrequency.HOURLY:
            return delta >= timedelta(hours=1)
        elif self.frequency == AutomationFrequency.DAILY:
            return delta >= timedelta(days=1)
        elif self.frequency == AutomationFrequency.WEEKLY:
            return delta >= timedelta(weeks=1)
        elif self.frequency == AutomationFrequency.MONTHLY:
            return delta >= timedelta(days=30)

        return False


# ============================================================================
# Класс автоматизации
# ============================================================================

class CardAutomation:
    """
    Менеджер автоматизации для карточной системы

    Реализует законы:
    - Закон автоматизации рутины (избавление от повторяющихся действий)
    - Закон предсказуемости (детерминированные автоматические действия)
    - Закон сохранения информации (автоматические backup)
    """

    def __init__(self, card_dir: Path, backup_dir: Optional[Path] = None):
        """
        Инициализация менеджера автоматизации

        Args:
            card_dir: Директория с карточками
            backup_dir: Директория для резервных копий (опционально)
        """
        self.card_manager = CardManager(card_dir)
        self.backup_dir = backup_dir or card_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.reminders: List[Reminder] = []
        self.tasks: List[AutomationTask] = []

        # Регистрация стандартных задач автоматизации
        self._register_default_tasks()

        logger.info(f"Автоматизация инициализирована для {card_dir}")

    def _register_default_tasks(self):
        """Регистрация стандартных задач автоматизации"""
        # Ежечасная проверка просроченных задач
        self.tasks.append(AutomationTask(
            name="check_overdue_tasks",
            frequency=AutomationFrequency.HOURLY,
            action=self.check_overdue_tasks
        ))

        # Ежедневная проверка лекарств
        self.tasks.append(AutomationTask(
            name="check_medicine_reminders",
            frequency=AutomationFrequency.DAILY,
            action=self.check_medicine_reminders
        ))

        # Ежедневное архивирование завершённых карточек
        self.tasks.append(AutomationTask(
            name="archive_completed_cards",
            frequency=AutomationFrequency.DAILY,
            action=self.archive_old_completed_cards
        ))

        # Еженедельная резервная копия
        self.tasks.append(AutomationTask(
            name="weekly_backup",
            frequency=AutomationFrequency.WEEKLY,
            action=self.create_backup
        ))

    # ========================================================================
    # Напоминания и проверки
    # ========================================================================

    def check_overdue_tasks(self) -> List[Reminder]:
        """
        Проверить просроченные и подходящие к сроку задачи

        Returns:
            Список напоминаний о задачах
        """
        logger.info("Проверка просроченных задач...")
        reminders = []
        now = datetime.now()

        # Получить все активные задачи
        all_cards = self.card_manager.search()
        tasks = [c for c in all_cards if c.type == CardType.TASK and c.status != CardStatus.ARCHIVED]

        for task in tasks:
            if not isinstance(task, TaskCard) or not task.due_date:
                continue

            # Проверить просроченные
            if task.due_date < now and task.status != CardStatus.COMPLETED:
                reminder = Reminder(
                    type=ReminderType.TASK_OVERDUE,
                    card_id=task.id,
                    title=task.title,
                    message=f"Задача просрочена на {(now - task.due_date).days} дн.",
                    priority=Priority.HIGH
                )
                reminders.append(reminder)
                logger.warning(f"Просроченная задача: {task.title}")

            # Проверить задачи, до которых осталось меньше 24 часов
            elif 0 < (task.due_date - now).total_seconds() < 86400:  # 24 часа
                reminder = Reminder(
                    type=ReminderType.TASK_DUE,
                    card_id=task.id,
                    title=task.title,
                    message=f"Срок выполнения: {task.due_date.strftime('%H:%M')}",
                    priority=task.priority
                )
                reminders.append(reminder)
                logger.info(f"Задача близка к сроку: {task.title}")

        self.reminders.extend(reminders)
        return reminders

    def check_medicine_reminders(self) -> List[Reminder]:
        """
        Проверить напоминания о приёме лекарств

        Returns:
            Список напоминаний о лекарствах
        """
        logger.info("Проверка напоминаний о лекарствах...")
        reminders = []
        now = datetime.now()
        current_time = now.time()

        # Получить все карточки лекарств
        all_cards = self.card_manager.search()
        medicines = [c for c in all_cards if c.type == CardType.MEDICINE]

        for med in medicines:
            if not isinstance(med, MedicineCard):
                continue

            # Проверить расписание (если есть)
            if hasattr(med, 'schedule') and med.schedule:
                for schedule_time_str in med.schedule:
                    # Парсинг времени из строки (формат: "HH:MM")
                    try:
                        hour, minute = map(int, schedule_time_str.split(':'))
                        schedule_time = time(hour, minute)

                        # Проверить, близко ли время приёма (в пределах 30 минут)
                        time_diff = abs(
                            (current_time.hour * 60 + current_time.minute) -
                            (schedule_time.hour * 60 + schedule_time.minute)
                        )

                        if time_diff <= 30:  # В пределах 30 минут
                            reminder = Reminder(
                                type=ReminderType.MEDICINE,
                                card_id=med.id,
                                title=med.title,
                                message=f"Время приёма: {schedule_time_str}. Дозировка: {med.dosage}",
                                priority=Priority.HIGH
                            )
                            reminders.append(reminder)
                            logger.info(f"Напоминание о лекарстве: {med.title}")
                    except (ValueError, AttributeError):
                        continue

        self.reminders.extend(reminders)
        return reminders

    def get_reminders(self, clear: bool = True) -> List[Reminder]:
        """
        Получить все накопленные напоминания

        Args:
            clear: Очистить список после получения

        Returns:
            Список напоминаний
        """
        reminders = self.reminders.copy()
        if clear:
            self.reminders.clear()
        return reminders

    # ========================================================================
    # Архивирование и очистка
    # ========================================================================

    def archive_old_completed_cards(self, days_old: int = 30) -> int:
        """
        Архивировать старые завершённые карточки

        Args:
            days_old: Возраст карточки в днях для архивирования

        Returns:
            Количество архивированных карточек
        """
        logger.info(f"Архивирование карточек старше {days_old} дней...")
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_old)

        # Получить все завершённые карточки
        all_cards = self.card_manager.search()
        completed_cards = [
            c for c in all_cards
            if c.status == CardStatus.COMPLETED and c.updated_at < cutoff_date
        ]

        archived_count = 0
        for card in completed_cards:
            try:
                self.card_manager.delete(card.id)
                archived_count += 1
                logger.debug(f"Архивирована карточка: {card.title}")
            except Exception as e:
                logger.error(f"Ошибка архивирования {card.id}: {e}")

        logger.info(f"Архивировано карточек: {archived_count}")
        return archived_count

    # ========================================================================
    # Резервное копирование
    # ========================================================================

    def create_backup(self, prefix: str = "auto") -> Optional[Path]:
        """
        Создать резервную копию всех карточек

        Args:
            prefix: Префикс имени файла backup

        Returns:
            Путь к созданному backup-файлу или None при ошибке
        """
        logger.info("Создание резервной копии...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{prefix}_backup_{timestamp}.zip"

        try:
            exporter = CardExporter(self.card_manager)
            count = exporter.export_to_archive(backup_file)
            logger.info(f"Резервная копия создана: {backup_file} ({count} карточек)")
            return backup_file
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return None

    # ========================================================================
    # Генерация повторяющихся задач
    # ========================================================================

    def create_recurring_tasks(self) -> int:
        """
        Создать повторяющиеся задачи на основе шаблонов

        Ищет задачи с тегом "recurring" и создаёт их копии для следующего периода

        Returns:
            Количество созданных задач
        """
        logger.info("Создание повторяющихся задач...")
        all_cards = self.card_manager.search(tags=["recurring"])
        created_count = 0

        for card in all_cards:
            if not isinstance(card, TaskCard):
                continue

            # Проверить, нужно ли создавать новую задачу
            if card.status == CardStatus.COMPLETED and card.due_date:
                # Создать новую задачу на следующий период
                new_task = TaskCard(
                    title=card.title,
                    description=card.description,
                    tags=card.tags,
                    priority=card.priority,
                    due_date=card.due_date + timedelta(weeks=1)  # Еженедельная задача
                )

                try:
                    self.card_manager.create(new_task)
                    created_count += 1
                    logger.info(f"Создана повторяющаяся задача: {new_task.title}")
                except Exception as e:
                    logger.error(f"Ошибка создания задачи: {e}")

        logger.info(f"Создано повторяющихся задач: {created_count}")
        return created_count

    # ========================================================================
    # Отчёты и статистика
    # ========================================================================

    def generate_weekly_report(self) -> Dict:
        """
        Сгенерировать еженедельный отчёт

        Returns:
            Словарь со статистикой за неделю
        """
        logger.info("Генерация еженедельного отчёта...")
        now = datetime.now()
        week_ago = now - timedelta(weeks=1)

        all_cards = self.card_manager.search()

        # Фильтровать карточки за последнюю неделю
        week_cards = [c for c in all_cards if c.created_at >= week_ago]

        report = {
            "period": f"{week_ago.strftime('%Y-%m-%d')} — {now.strftime('%Y-%m-%d')}",
            "total_created": len(week_cards),
            "by_type": {},
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "active_medicines": 0
        }

        # Статистика по типам
        for card in week_cards:
            card_type = card.type.value if hasattr(card.type, 'value') else str(card.type)
            report["by_type"][card_type] = report["by_type"].get(card_type, 0) + 1

            if card.type == CardType.TASK:
                if card.status == CardStatus.COMPLETED:
                    report["completed_tasks"] += 1
                elif isinstance(card, TaskCard) and card.due_date and card.due_date < now:
                    report["overdue_tasks"] += 1

            elif card.type == CardType.MEDICINE:
                if card.status != CardStatus.ARCHIVED:
                    report["active_medicines"] += 1

        logger.info(f"Отчёт сгенерирован: {report['total_created']} карточек за неделю")
        return report

    # ========================================================================
    # Запуск автоматизации
    # ========================================================================

    def run_automation_cycle(self) -> Dict[str, any]:
        """
        Запустить один цикл автоматизации

        Выполняет все задачи, для которых пришло время

        Returns:
            Результаты выполнения задач
        """
        logger.info("=== Запуск цикла автоматизации ===")
        results = {
            "timestamp": datetime.now(),
            "tasks_run": [],
            "reminders": []
        }

        for task in self.tasks:
            if task.should_run():
                logger.info(f"Выполнение задачи: {task.name}")
                try:
                    result = task.action()
                    task.last_run = datetime.now()
                    results["tasks_run"].append({
                        "name": task.name,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Ошибка выполнения задачи {task.name}: {e}")
                    results["tasks_run"].append({
                        "name": task.name,
                        "success": False,
                        "error": str(e)
                    })

        # Собрать все напоминания
        results["reminders"] = [str(r) for r in self.get_reminders()]

        logger.info(f"=== Цикл завершён: {len(results['tasks_run'])} задач, {len(results['reminders'])} напоминаний ===")
        return results

    def enable_task(self, task_name: str):
        """Включить задачу автоматизации"""
        for task in self.tasks:
            if task.name == task_name:
                task.enabled = True
                logger.info(f"Задача {task_name} включена")
                return
        logger.warning(f"Задача {task_name} не найдена")

    def disable_task(self, task_name: str):
        """Отключить задачу автоматизации"""
        for task in self.tasks:
            if task.name == task_name:
                task.enabled = False
                logger.info(f"Задача {task_name} отключена")
                return
        logger.warning(f"Задача {task_name} не найдена")


# ============================================================================
# CLI для тестирования
# ============================================================================

def main():
    """Демонстрация автоматизации"""
    import sys

    if len(sys.argv) < 2:
        print("Использование: python automation.py <cards_dir>")
        sys.exit(1)

    cards_dir = Path(sys.argv[1])
    automation = CardAutomation(cards_dir)

    print("🤖 Система автоматизации карточек")
    print("=" * 50)

    # Запустить цикл автоматизации
    results = automation.run_automation_cycle()

    print(f"\n📊 Выполнено задач: {len(results['tasks_run'])}")
    for task in results['tasks_run']:
        status = "✅" if task['success'] else "❌"
        print(f"  {status} {task['name']}")

    print(f"\n🔔 Напоминания: {len(results['reminders'])}")
    for reminder in results['reminders']:
        print(f"  {reminder}")

    # Сгенерировать еженедельный отчёт
    print("\n📈 Еженедельный отчёт:")
    report = automation.generate_weekly_report()
    print(f"  Период: {report['period']}")
    print(f"  Создано карточек: {report['total_created']}")
    print(f"  Завершено задач: {report['completed_tasks']}")
    print(f"  Просроченных задач: {report['overdue_tasks']}")
    print(f"  Активных лекарств: {report['active_medicines']}")


if __name__ == "__main__":
    main()
