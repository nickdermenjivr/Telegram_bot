from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ваш Telegram-бот.")



async def simulate_start(application):
    # Укажи реальный chat_id
    chat_id = -123456789  
    user_id = 987654321

    # Создаём "фейковый" update
    fake_update = Update(
        update_id=0,
        message=await application.bot.send_message(chat_id=chat_id, text="/start")
    )

    # Создаём "фейковый" context
    fake_context = ContextTypes.DEFAULT_TYPE(application=application)

    # Вызываем start() с поддельными данными
    await start(fake_update, fake_context)