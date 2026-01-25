"""
Telegram бот для карточной системы

Пример интеграции карточной системы в Telegram бота.

Установка:
    pip install python-telegram-bot

Настройка:
    1. Создайте бота через @BotFather в Telegram
    2. Получите токен
    3. Установите переменную окружения: export BOT_TOKEN="ваш-токен"
    4. Запустите: python telegram_bot_example.py

Команды бота:
    /start - Начать работу
    /help - Помощь
    /create - Создать карточку
    /list - Список карточек
    /stats - Статистика
"""

import os
import sys
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Добавляем путь к card_system
sys.path.insert(0, str(Path(__file__).parent.parent / "card_system"))

from card import TaskCard, MedicineCard, ContactCard
from card_manager import CardManager

# Инициализация менеджера карточек
CARDS_DIR = Path(__file__).parent / "bot_cards"
CARDS_DIR.mkdir(exist_ok=True)
manager = CardManager(CARDS_DIR)

# States для ConversationHandler
CHOOSING_TYPE, TYPING_TITLE, TYPING_DETAILS = range(3)


# ============================================================================
# Команды бота
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Привет, {user.mention_html()}!\n\n"
        "Я помогу тебе организовать твои дела через карточки.\n\n"
        "Используй /help чтобы увидеть все команды."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
📚 *Доступные команды:*

/create - Создать новую карточку
/list - Показать все карточки
/today - Задачи на сегодня
/medicine - Напоминания о лекарствах
/stats - Статистика
/help - Эта справка

💡 *Типы карточек:*
• Задачи - для списков дел
• Лекарства - напоминания о приёме
• Контакты - врачи, друзья, родственники

_Выберите команду из меню внизу_ 👇
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /list - список всех карточек"""
    cards = manager.search()

    if not cards:
        await update.message.reply_text(
            "📭 У тебя пока нет карточек.\n"
            "Используй /create чтобы создать первую карточку."
        )
        return

    # Группируем по типам
    by_type = {}
    for card in cards:
        card_type = card.type.value
        if card_type not in by_type:
            by_type[card_type] = []
        by_type[card_type].append(card)

    # Формируем сообщение
    text = "📋 *Твои карточки:*\n\n"

    type_emoji = {
        'task': '✅',
        'medicine': '💊',
        'contact': '👤',
        'note': '📝'
    }

    for card_type, cards_list in by_type.items():
        emoji = type_emoji.get(card_type, '📄')
        text += f"{emoji} *{card_type.capitalize()}* ({len(cards_list)}):\n"
        for card in cards_list[:5]:  # Показываем первые 5
            text += f"  • {card.title}\n"
        if len(cards_list) > 5:
            text += f"  _...и ещё {len(cards_list) - 5}_\n"
        text += "\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /today - задачи на сегодня"""
    tasks = manager.search(card_type='task', status='pending')

    if not tasks:
        await update.message.reply_text("✨ На сегодня нет невыполненных задач!")
        return

    text = "📅 *Задачи на сегодня:*\n\n"
    for i, task in enumerate(tasks, 1):
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(task.priority, '⚪')
        text += f"{i}. {priority_emoji} {task.title}\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def medicine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /medicine - напоминания о лекарствах"""
    medicines = manager.search(card_type='medicine')

    if not medicines:
        await update.message.reply_text(
            "💊 Нет записей о лекарствах.\n"
            "Создай карточку лекарства через /create"
        )
        return

    text = "💊 *Твои лекарства:*\n\n"
    for med in medicines:
        text += f"• *{med.title}* - {med.dosage}\n"
        if hasattr(med, 'schedule') and med.schedule:
            text += f"  Расписание: {', '.join(med.schedule)}\n"
        text += "\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats - статистика"""
    stats = manager.get_stats()

    text = "📊 *Статистика:*\n\n"
    text += f"Всего карточек: *{stats['total']}*\n\n"

    if 'by_type' in stats:
        text += "По типам:\n"
        for card_type, count in stats['by_type'].items():
            emoji = {'task': '✅', 'medicine': '💊', 'contact': '👤', 'note': '📝'}.get(card_type, '📄')
            text += f"  {emoji} {card_type}: {count}\n"

    await update.message.reply_text(text, parse_mode='Markdown')


# ============================================================================
# Conversation Handler для создания карточек
# ============================================================================

async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания карточки"""
    reply_keyboard = [['Задача', 'Лекарство'], ['Контакт', 'Отмена']]

    await update.message.reply_text(
        "📝 *Создание новой карточки*\n\n"
        "Выбери тип карточки:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode='Markdown'
    )
    return CHOOSING_TYPE


async def create_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбран тип карточки"""
    text = update.message.text

    if text == 'Отмена':
        await update.message.reply_text(
            "❌ Отменено.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    type_map = {
        'Задача': 'task',
        'Лекарство': 'medicine',
        'Контакт': 'contact'
    }

    card_type = type_map.get(text)
    if not card_type:
        await update.message.reply_text("Пожалуйста, выбери тип из кнопок.")
        return CHOOSING_TYPE

    context.user_data['card_type'] = card_type

    emoji_map = {'task': '✅', 'medicine': '💊', 'contact': '👤'}
    emoji = emoji_map.get(card_type, '📄')

    await update.message.reply_text(
        f"{emoji} Хорошо! Как назовём карточку?\n\n"
        f"Например: {'Купить молоко' if card_type == 'task' else 'Эналаприл' if card_type == 'medicine' else 'Доктор Иванов'}",
        reply_markup=ReplyKeyboardRemove()
    )
    return TYPING_TITLE


async def create_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Введён заголовок"""
    title = update.message.text
    context.user_data['title'] = title

    card_type = context.user_data['card_type']

    if card_type == 'task':
        reply_keyboard = [['Высокий', 'Средний', 'Низкий'], ['Пропустить']]
        await update.message.reply_text(
            "Какой приоритет у задачи?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    elif card_type == 'medicine':
        await update.message.reply_text(
            "Напиши дозировку (например: 10 мг):",
            reply_markup=ReplyKeyboardRemove()
        )
    elif card_type == 'contact':
        await update.message.reply_text(
            "Напиши номер телефона (или отправь 'Пропустить'):",
            reply_markup=ReplyKeyboardRemove()
        )

    return TYPING_DETAILS


async def create_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Введены детали"""
    details = update.message.text
    card_type = context.user_data['card_type']
    title = context.user_data['title']

    # Создаём карточку
    try:
        if card_type == 'task':
            priority_map = {'Высокий': 'high', 'Средний': 'medium', 'Низкий': 'low', 'Пропустить': 'medium'}
            priority = priority_map.get(details, 'medium')
            card = TaskCard(title=title, priority=priority)

        elif card_type == 'medicine':
            card = MedicineCard(title=title, dosage=details)

        elif card_type == 'contact':
            phone = details if details != 'Пропустить' else None
            card = ContactCard(title=title, phone=phone)

        # Сохраняем
        created = manager.create(card)

        emoji_map = {'task': '✅', 'medicine': '💊', 'contact': '👤'}
        emoji = emoji_map.get(card_type, '📄')

        await update.message.reply_text(
            f"{emoji} Готово! Карточка создана.\n\n"
            f"*{created.title}*\n"
            f"ID: `{created.id}`\n\n"
            f"Используй /list чтобы увидеть все карточки.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при создании карточки: {e}",
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания карточки"""
    await update.message.reply_text(
        "❌ Отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ============================================================================
# Главная функция
# ============================================================================

def main():
    """Запуск бота"""
    # Получаем токен
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("❌ Ошибка: не установлена переменная окружения BOT_TOKEN")
        print("Создайте бота через @BotFather и установите токен:")
        print("  export BOT_TOKEN='ваш-токен'")
        return

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("medicine", medicine_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Conversation Handler для создания карточек
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create_start)],
        states={
            CHOOSING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_type)],
            TYPING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_title)],
            TYPING_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_details)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Запуск
    print("=" * 60)
    print("Telegram бот для карточной системы")
    print("=" * 60)
    print(f"Карточки хранятся в: {CARDS_DIR}")
    print("Бот запущен! Нажмите Ctrl+C для остановки.")
    print("=" * 60)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
