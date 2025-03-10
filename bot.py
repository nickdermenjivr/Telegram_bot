import nest_asyncio
nest_asyncio.apply()

from telegram.ext import ApplicationBuilder, CommandHandler
from config import TOKEN
from handlers.start import start
from handlers.timer import start_timer, stop_timer
from handlers.news_parser import parse_news, format_news, news_handler  # Импортируем парсер

async def main():
    # Создаем Application с включенным JobQueue
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("timer", start_timer))  # Запуск таймера
    application.add_handler(CommandHandler("stoptimer", stop_timer))  # Остановка таймера
    application.add_handler(CommandHandler("news", news_handler))  # Команда /news

    job_queue = application.job_queue
    job_queue.run_once(start_timer, when=0.0)

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())