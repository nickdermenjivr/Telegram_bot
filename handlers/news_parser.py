import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes


async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для отправки новостей."""
    url = "https://www.zr.ru/news/"  # Замените на URL новостного сайта
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
    for item in soup.find_all("div", class_="styled__Announcement-sc-d7096096-6 kXQUNL"):  # Новостной блок
        title = item.find("a", class_="styled__UiLink-sc-3f69b705-0 jRgABd styled__AnnouncementTitle-sc-d7096096-1 btMDVT").text.strip()  # Заголовок (предполагаем, что заголовок внутри <a>)
        link = item.find("a")["href"]  # Ссылка
        description = item.find("div", class_="styled__AnnouncementDescription-sc-d7096096-2 eZkTxD").text.strip()  
        news_items.append({"title": title, "link": link, "description": description})

    return news_items

def format_news(news_items, index):
    """Форматирует новости в текстовый пост."""
    post = "📰 Последние новости:\n\n"
    postItem = news_items[index]
    post += f"🔹{postItem['title']}. {postItem['description']}.\n[https://www.zr.ru{postItem['link']}]\n\n"
    return post