from telegram import Update
from telegram.ext import ContextTypes
from handlers.timer import start_timer

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ваш Telegram-бот.")
