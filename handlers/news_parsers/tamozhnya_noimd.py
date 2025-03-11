import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from data.news_data import NewsItem

def parse_news():
    """Парсит новости с сайта"""
    response = requests.get("https://noi.md/ru/news-by-tag/tamozhnya")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    news_items = []

    # Парсим новостные блоки
    for item in soup.find_all("a", class_="news-feed-item-hdr"):  # Новостной блок
        link = item["href"]  # Ссылка
        news_items.append(NewsItem("https://noi.md", link))

    return news_items