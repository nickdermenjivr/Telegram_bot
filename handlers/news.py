import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

from handlers.tamozhnya_noimd import parse_news as tamozhnya_noimd_parseNews, format_news as tamozhnya_noimd_formatNews
from handlers.politica_pointmd import parse_news as politica_pointmd_parseNews, format_news as politica_pointmd_formatNews

# Храним новости
tamozhnya_noimd_cache = tamozhnya_noimd_parseNews() 
politica_pointmd_cahce = politica_pointmd_parseNews()

# Текущая новость
tamozhnya_noimd_index = 0
politica_pointmd_index = 0  

async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей c периодичностью."""

    #context.job_queue.run_repeating(post_next_tamozhnya_noimd_news, interval=5, first=0.1, chat_id=update.message.chat_id)
    context.job_queue.run_repeating(post_next_politica_pointmd_news, interval=8, first=0.1, chat_id=update.message.chat_id)



async def post_next_tamozhnya_noimd_news(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет следующую новость каждый час."""
    global tamozhnya_noimd_cache, tamozhnya_noimd_index

    if tamozhnya_noimd_index + 1 >= len(tamozhnya_noimd_cache):
        return  # Если новости закончились, ничего не делаем

    await context.bot.send_message(chat_id=context.job.chat_id, text=tamozhnya_noimd_formatNews(tamozhnya_noimd_cache[tamozhnya_noimd_index]))
    tamozhnya_noimd_index += 1

async def post_next_politica_pointmd_news(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет следующую новость каждый час."""
    global politica_pointmd_cahce, politica_pointmd_index

    if politica_pointmd_index + 1 >= len(politica_pointmd_cahce):
        return  # Если новости закончились, ничего не делаем

    await context.bot.send_message(chat_id=context.job.chat_id, text=tamozhnya_noimd_formatNews(politica_pointmd_cahce[politica_pointmd_index]))
    politica_pointmd_index += 1
