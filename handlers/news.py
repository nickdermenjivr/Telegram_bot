import data.news_data
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

from handlers.news_parsers.politica_noimd import parse_news as politica_noimd_parseNews
from handlers.news_parsers.tamozhnya_noimd import parse_news as tamozhnya_noimd_parseNews
from handlers.news_parsers.bulgaria_tourism import parse_news as bulgaria_tourism_parseNews


# Текущая новость
news = {}
news_index = 5

async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей c периодичностью."""
    global news
    news = interleave_lists(politica_noimd_parseNews(), tamozhnya_noimd_parseNews(), bulgaria_tourism_parseNews())
    context.job_queue.run_repeating(post_news, interval=7200, first=0.1, chat_id=update.message.chat_id)
    print(f"Amount of parsed news: {len(news)}")


def interleave_lists(*lists):
    """Перемешивает элементы из N списков по очереди."""
    return [item for group in zip(*lists) for item in group] + [item for lst in lists for item in lst[len(min(lists, key=len)):]]


async def post_news(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет следующую новость."""
    global news, news_index

    if news_index + 1 >= len(news):
        return  # Если новости закончились, ничего не делаем

    await context.bot.send_message(chat_id=context.job.chat_id, text=news[news_index].format_news())
    news_index += 1