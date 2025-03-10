import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

async def tamozhnya_noimd_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей."""
    await update.message.reply_text(format_news(parse_news()[0]))


def parse_news():
    """Парсит новости с сайта https://www.zr.ru/news/."""
    response = requests.get("https://noi.md/ru/news-by-tag/tamozhnya")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    news_items = []

    # Парсим новостные блоки
    for item in soup.find_all("a", class_="news-feed-item-hdr"):  # Новостной блок
        title = item["title"]  # Заголовок (предполагаем, что заголовок внутри <a>)
        link = item["href"]  # Ссылка
        news_items.append({"title": title, "link": link})

    return news_items

def format_news(news_item):
    """Форматирует новости в текстовый пост."""
    post = "📰 Таможенные новости:\n\n"
    post += f"🔹{news_item['title']}.\n[https://noi.md{news_item['link']}]\n\n"
    return post