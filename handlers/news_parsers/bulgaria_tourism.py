import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from data.news_data import NewsItem

def parse_news():
    """Парсит новости с сайта"""
    response = requests.get("https://homeforyou.bg/ru/novosti-turizm-v-bolgarii")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    news_items = []

    # Парсим новостные блоки
    for item in soup.find_all("div", class_="col-md-10"):  # Новостной блок
        link = item.find("a")["href"]  # Ссылка
        news_items.append(NewsItem("", link))

    return news_items
