import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes


async def tamozhnya_noimd_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей."""
    url = "https://noi.md/ru/news-by-tag/tamozhnya"  # Замените на URL новостного сайта
    news = parse_news(url)
    post = format_news(news, 0)
    await update.message.reply_text(post)


def parse_news(url):
    """Парсит новости с сайта https://www.zr.ru/news/."""
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    news_items = []

    # Парсим новостные блоки
    for item in soup.find_all("a", class_="news-feed-item-hdr"):  # Новостной блок
        title = item["title"]  # Заголовок (предполагаем, что заголовок внутри <a>)
        link = item["href"]  # Ссылка
        news_items.append({"title": title, "link": link})

    return news_items

def format_news(news_items, index):
    """Форматирует новости в текстовый пост."""
    post = "📰 Таможенные новости:\n\n"
    postItem = news_items[index]
    post += f"🔹{postItem['title']}.\n[https://noi.md{postItem['link']}]\n\n"
    return post