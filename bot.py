import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN
from handlers.start import *
from handlers.chat_id_handler import chat_id
from handlers.news import news_handler, stop_news_handler
from handlers.alex_post import start_sending_posts, stop_sending_posts

async def main():
    # Создаем Application с включенным JobQueue
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news_handler))
    application.add_handler(CommandHandler("stopnews", stop_news_handler))
    application.add_handler(CommandHandler("chatid", chat_id))
    application.add_handler(CommandHandler("alexpost", start_sending_posts))
    application.add_handler(CommandHandler("stopalexpost", stop_sending_posts))


    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())