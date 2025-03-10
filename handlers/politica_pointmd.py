import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

async def politica_pointmd_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей."""
    await update.message.reply_text(format_news(parse_news()[0]))


def parse_news():
    """Парсит новости с сайта https://www.zr.ru/news/."""
    response = requests.get("https://point.md/ru/novosti/politika/")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    news_items = []

    # Парсим новостные блоки
    for item in soup.find_all("div", class_="sc-9d3f57-4 hGdKBB news_list_item__wrapper__side"):  # Новостной блок
        title = item.find("h3").text  # Заголовок (предполагаем, что заголовок внутри <a>)
        link = item.find("a")["href"]  # Ссылка
        news_items.append({"title": title, "link": link})

    return news_items

def format_news(news_item):
    """Форматирует новости в текстовый пост."""
    post = "📰 Таможенные новости:\n\n"
    post += f"🔹{news_item['title']}.\n[https://point.md{news_item['link']}]\n\n"
    return post