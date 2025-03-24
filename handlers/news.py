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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    # Критически важные параметры для обхода защиты
    options.add_argument("--headless=new")  # Новый headless-режим Chrome
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Подменяем User-Agent и язык
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("accept-language=ru-RU,ru;q=0.9")
    
    # Отключаем автоматическое управление WebDriver
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        
        # Подменяем навигационные свойства
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Первый запрос для установки кук
        driver.get("https://news.google.com/?hl=ru&gl=RU&ceid=RU:ru")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Основной запрос
        driver.get(full_url)
        
        # Ожидание и обработка возможного согласия
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            if "consent.google.com" in driver.current_url:
                # Кликаем на кнопку согласия, если появилась
                driver.find_element(By.XPATH, "//button/div[contains(., 'Принять все')]").click()
                WebDriverWait(driver, 5).until_not(EC.url_contains("consent.google.com"))
        except:
            pass
        
        # Финализация URL
        final_url = driver.current_url
        
        # Очистка от трекеров
        for param in ['utm_', 'oq=', 'ved=', 'gs_lcp=']:
            if param in final_url:
                final_url = final_url.split(param)[0]
        
        return final_url.split('?')[0] if '?' in final_url else final_url
        
    except Exception as e:
        print(f"Ошибка при получении URL: {str(e)}")
        return ""
    finally:
        if 'driver' in locals():
            driver.quit()