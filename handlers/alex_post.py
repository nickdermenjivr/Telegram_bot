import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

# Путь к папке с фотографиями
PHOTOS_DIR = "content/alex_posts"

# Глобальная переменная для хранения списка фотографий
photos = []

# Индекс текущей фотографии
current_photo_index = 0

async def start_sending_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для запуска публикации фотографий."""
    context.job_queue.run_repeating(send_photo, interval=3600.0, first=1500, chat_id=update.message.chat_id)
    print("Публикация фотографий начата!")

async def send_photo(context: ContextTypes.DEFAULT_TYPE):
    """Функция для отправки фотографии."""
    global current_photo_index

    # Если список фотографий пуст, загружаем их из папки
    if not photos:
        load_photos()

    # Если фотографии есть, отправляем текущую
    if photos:
        photo_path = photos[current_photo_index]
        with open(photo_path, "rb") as photo_file:
            await context.bot.send_photo(chat_id=context.job.chat_id, photo=photo_file)
        print(f"Отправлена фотография: {photo_path}")

        # Переходим к следующей фотографии
        current_photo_index = (current_photo_index + 1) % len(photos)
    else:
        print("Нет фотографий в папке.")

def load_photos():
    """Загружает список фотографий из папки."""
    global photos
    photos = [
        os.path.join(PHOTOS_DIR, filename)
        for filename in os.listdir(PHOTOS_DIR)
        if filename.endswith((".jpg", ".jpeg", ".png", ".gif"))
    ]
    print(f"Загружено {len(photos)} фотографий.")