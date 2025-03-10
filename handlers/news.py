import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

from handlers.tamozhnya_noimd import parse_news as tamozhnya_noimd_parseNews, format_news as tamozhnya_noimd_formatNews

tamoznya_news_cache = tamozhnya_noimd_parseNews()  # Храним новости
tamoznya_news_index = 0  # Текущая новость

async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей c периодичностью."""

    context.job_queue.run_repeating(post_next_tamozhnya_news, interval=5, first=0.1, chat_id=update.message.chat_id)



async def post_next_tamozhnya_news(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет следующую новость каждый час."""
    global tamoznya_news_cache, tamoznya_news_index

    if tamoznya_news_index + 1 >= len(tamoznya_news_cache):
        return  # Если новости закончились, ничего не делаем

    await context.bot.send_message(chat_id=context.job.chat_id, text=tamozhnya_noimd_formatNews(tamoznya_news_cache[tamoznya_news_index]))
    tamoznya_news_index += 1

