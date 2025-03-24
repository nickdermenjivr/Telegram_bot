from data.news_data import *
import requests
import time  # Добавляем импорт модуля time для time.sleep()
from datetime import time as datetime_time, datetime  # Переименовываем импортированный time из datetime
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

# Время начала и окончания работы (8:00 - 22:00)
START_TIME = datetime_time(8, 0)  # Используем переименованный datetime_time
END_TIME = datetime_time(22, 0)  # Используем переименованный datetime_time

# Словарь с источниками и их параметрами парсинга
sources = {
    1: {
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FuSjFHZ0pTVlNnQVAB?hl=ru&gl=RU&ceid=RU%3Aru",
        "parser": lambda soup: soup.find("a", class_="WwrzSb")["href"],
    },
    2: {
        "url": "https://nokta.md",
        "parser": lambda soup: soup.find("a", class_="list-item__link-inner")["href"],
    },
    3: {
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
    job = context.job_queue.run_repeating(
        post_news, 
        interval=7000, 
        first=0.1, 
        chat_id=update.message.chat_id
        )
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
            # Combine the caption with the message text
            message_text = f"🚨 Свежие новости от @moldovabolgaria — читайте прямо сейчас!\n\n{news.format_news()}"
            await context.bot.send_message(
                chat_id=context.job.chat_id, 
                text=message_text
            )
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
        link = source["parser"](soup)

        if not link.startswith("https"):
            print("GET REAL LINK")
            real_url = get_real_url(link)
            return NewsItem(real_url)

        return NewsItem(link)
    except Exception as e:
        print(f"Error parsing source {source_index}: {e}")
        return NewsItem("")



def get_real_url(relative_url):
    full_url = urljoin("https://news.google.com/", relative_url)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")  # Обязательно для Linux
    options.add_argument("--disable-dev-shm-usage")  # Важно для ограниченной памяти
    options.add_argument("--remote-debugging-port=9222")  # Фиксированный порт
    options.add_argument("--user-data-dir=/tmp/chrome_profile")  # Уникальная папка профиля
    
    try:
        # Для Linux явно укажите путь к chromedriver
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(full_url)
        driver.set_page_load_timeout(30)
        
        current_url = driver.current_url
        stable = False
        attempts = 0
        
        while not stable and attempts < 10:
            time.sleep(1)
            new_url = driver.current_url
            
            if new_url == current_url:
                stable = True
            else:
                current_url = new_url
            
            attempts += 1
        
        return driver.current_url
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return ""
    finally:
        if 'driver' in locals():
            driver.quit()