import os
from datetime import time, datetime
from telegram import Update
from telegram.ext import ContextTypes

# Время начала и окончания работы (8:00 - 22:00)
START_TIME = time(8, 0)
END_TIME = time(22, 0) 

# Путь к папке с фотографиями
PHOTOS_DIR = "content/alex_posts"

# Глобальная переменная для хранения списка фотографий
photos = []

# Индекс текущей фотографии
current_photo_index = 0

async def start_sending_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для запуска публикации фотографий."""

    #Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    #Запускаем задачу
    job = context.job_queue.run_repeating(send_photo, interval=9000.0, first=0.1, chat_id=update.message.chat_id)
    context.chat_data['photo_job'] = job  # Сохраняем задачу в контексте
    print("Публикация фотографий начата!")

async def stop_sending_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для остановки публикации фотографий."""
    
    #Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    if 'photo_job' in context.chat_data:
        job = context.chat_data['photo_job']
        job.schedule_removal()  # Останавливаем задачу
        del context.chat_data['photo_job']  # Удаляем задачу из контекста
        print("Публикация фотографий остановлена.")
    else:
        print("Нет активной задачи для остановки.")

async def send_photo(context: ContextTypes.DEFAULT_TYPE):
    """Функция для отправки фотографии."""
    global current_photo_index

    # Проверяем текущее время
    now = datetime.now().time()
    if not (START_TIME <= now <= END_TIME):
        print("Время отдохнуть от публикации alex постов! Спокойной ночи!")
        return

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