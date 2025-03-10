import nest_asyncio
nest_asyncio.apply()

from telegram.ext import ApplicationBuilder, CommandHandler
from config import TOKEN
from handlers.start import *
from handlers.chat_id_handler import chat_id
from handlers.news import news_handler

async def main():
    # Создаем Application с включенным JobQueue
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_handler))
    application.add_handler(CommandHandler("chatid", chat_id))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())