from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /chatid. Выводит chat_id в чат."""
    chat_id = update.effective_chat.id  # Получаем chat_id
    await update.message.reply_text(f"Ваш chat_id: {chat_id}")