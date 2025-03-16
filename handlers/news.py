from data.news_data import *
import requests
from datetime import time, datetime
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

# Время начала и окончания работы (8:00 - 22:00)
START_TIME = time(8, 0)
END_TIME = time(22, 0) 

# Словарь с источниками и их параметрами парсинга
sources = {
    1: {
        "url": "https://nokta.md",
        "parser": lambda soup: soup.find("a", class_="list-item__link-inner")["href"],
    },
    2: {
        "url": "https://newsmaker.md/ru/category/news",
        "parser": lambda soup: soup.find("h3", class_="elementor-heading-title elementor-size-default").find("a")["href"],
    },
    # Добавьте остальные источники здесь
}

# Словарь для хранения последних новостей из каждого источника
last_news = {i: NewsItem("") for i in sources.keys()}

async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей c периодичностью."""
    
    #Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    #Запускаем задачу
    job = context.job_queue.run_repeating(post_news, interval=7000, first=0.1, chat_id=update.message.chat_id)
    context.chat_data['news_job'] = job  # Сохраняем задачу в контексте
    print(f"Публикация новостей начата!")

async def stop_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для остановки периодической задачи."""

    #Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    if 'news_job' in context.chat_data:
        job = context.chat_data['news_job']
        job.schedule_removal()  # Останавливаем задачу
        del context.chat_data['news_job']  # Удаляем задачу из контекста
        print("Публикация новостей приостановлена.")
    else:
       print("Нет активной задачи для остановки.")

async def post_news(context: ContextTypes.DEFAULT_TYPE):
    global last_news

    # Проверяем текущее время
    now = datetime.now().time()
    if not (START_TIME <= now <= END_TIME):
        print("Время отдохнуть от публикации рекламы! Спокойной ночи!")
        return

    for source_index in sources.keys():
        news = parse_news(source_index)
        if news != last_news[source_index]:
            last_news[source_index] = news
            await context.bot.send_message(chat_id=context.job.chat_id, text=news.format_news())
            print(f"News posted from source {source_index}: {news.link}")
            return  # Публикуем только одну новость за раз

    print("No new news from any source.")

def parse_news(source_index):
    source = sources.get(source_index)
    if not source:
        print(f"Source {source_index} not found!")
        return NewsItem("")

    try:
        response = requests.get(source["url"])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        link = source["parser"](soup)  # Используем лямбду для парсинга
        return NewsItem(link)
    except Exception as e:
        print(f"Error parsing source {source_index}: {e}")
        return NewsItem("")