from telegram import Update
from telegram.ext import ContextTypes
from .news_parser import parse_news, format_news  # Импортируем парсер

async def send_news_periodically(context: ContextTypes.DEFAULT_TYPE):
    """Функция, которая каждые 5 секунд отправляет следующую новость."""
    url = "https://www.zr.ru/news/"  # Замените на URL новостного сайта
    news = parse_news(url)
    
    # Получаем текущий индекс из context.job.data
    index = context.job.data.get("index", 0)
    
    # Если индекс превышает количество новостей, сбрасываем его
    if index >= len(news):
        index = 0
    
    # Форматируем и отправляем новость
    post = format_news(news, index)
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=post
    )
    
    # Увеличиваем индекс и сохраняем его в context.job.data
    context.job.data["index"] = index + 1

async def start_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для запуска таймера."""
    # Получаем chat_id пользователя
    chat_id = update.effective_chat.id
    
    # Запускаем периодическую задачу
    context.job_queue.run_repeating(
        callback=send_news_periodically,
        interval=10.0,  # Интервал в секундах
        first=0,  # Запуск сразу
        chat_id=chat_id,
        name=f"news_timer_{chat_id}",  # Уникальное имя для задачи
        data={"index": 0}  # Инициализируем индекс
    )


async def stop_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для остановки таймера."""
    # Получаем chat_id пользователя
    chat_id = update.effective_chat.id
    
    # Ищем задачу по имени
    job_name = f"news_timer_{chat_id}"
    jobs = context.job_queue.get_jobs_by_name(job_name)
    
    if jobs:
        # Удаляем задачу
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("Таймер остановлен.")
    else:
        await update.message.reply_text("Таймер не был запущен.")