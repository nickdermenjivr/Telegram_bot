import os
import shutil
import random
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ContextTypes
from datetime import time, datetime

# Время начала и окончания работы (8:00 - 22:00)
START_TIME = time(8, 0)
END_TIME = time(22, 0)

# Словарь для хранения последнего опубликованного видео для каждого канала
last_posted_videos = {}

# Список каналов TikTok
TIKTOK_CHANNELS = [
    "https://www.tiktok.com/@webstoremd",
    #"https://www.tiktok.com/@itz_comedy_official",
    #"https://www.tiktok.com/@alexanderyur7",
    # Добавьте другие каналы здесь
]

async def tiktok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /mem. Запускает периодическую задачу для публикации видео из TikTok.
    """
    # Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    # Запускаем задачу
    job = context.job_queue.run_repeating(
        post_tiktok_video,  # Функция, которая будет выполняться
        interval=10000,  # Интервал в секундах (20 секунд)
        first=0.1,  # Задержка перед первым запуском (0.1 секунды)
        chat_id=update.message.chat_id,  # ID чата
    )
    context.chat_data['tiktok_job'] = job  # Сохраняем задачу в контексте
    print("Публикация видео из TikTok начата!")

async def stop_tiktok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для остановки периодической задачи.
    """
    # Удаляем сообщение с командой из чата
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    if 'tiktok_job' in context.chat_data:
        job = context.chat_data['tiktok_job']
        job.schedule_removal()  # Останавливаем задачу
        del context.chat_data['tiktok_job']  # Удаляем задачу из контекста
        print("Публикация видео из TikTok приостановлена.")
    else:
        print("Нет активной задачи для остановки.")

async def post_tiktok_video(context: ContextTypes.DEFAULT_TYPE):
    """
    Периодическая задача для публикации видео из TikTok.
    """
    global last_posted_videos

    # Проверяем текущее время
    now = datetime.now().time()
    if not (START_TIME <= now <= END_TIME):
        print("Время отдохнуть от публикации видео! Спокойной ночи!")
        return

    # Перемешиваем список каналов для случайного порядка
    random.shuffle(TIKTOK_CHANNELS)

    # Перебираем каналы, пока не найдем новое видео
    for channel_url in TIKTOK_CHANNELS:
        print(f"Проверяем канал: {channel_url}")

        # Получаем ссылку на последнее видео
        latest_video_url = await get_latest_tiktok_video_url(channel_url)

        if latest_video_url:
            # Проверяем, было ли это видео уже опубликовано для данного канала
            if channel_url in last_posted_videos and latest_video_url == last_posted_videos[channel_url]:
                print(f"Видео из TikTok уже было опубликовано: {latest_video_url}")
                continue  # Переходим к следующему каналу

            # Скачиваем видео
            downloaded_video_path = await download_tiktok_video(latest_video_url)

            if downloaded_video_path:
                try:
                    # Открываем файл и отправляем видео в чат как новое сообщение
                    with open(downloaded_video_path, 'rb') as video_file:
                        await context.bot.send_video(
                            chat_id=context.job.chat_id,  # ID чата
                            video=video_file,  # Видеофайл
                            caption="🎬 Новый прикол! 🤣 Смотри 👉 @moldovabolgaria \n#ВирусноеВидео #Юмор #Тренды"  # Опциональный заголовок
                        )
                    # Обновляем последнее опубликованное видео для этого канала
                    last_posted_videos[channel_url] = latest_video_url
                    print(f"Видео успешно отправлено: {downloaded_video_path}")
                    break  # Выходим из цикла после успешной публикации
                except Exception as e:
                    print(f"Ошибка при отправке видео: {e}")
                finally:
                    # Удаляем видео после отправки (или в случае ошибки)
                    if os.path.exists(downloaded_video_path):
                        try:
                            os.remove(downloaded_video_path)
                            print(f"Видео удалено: {downloaded_video_path}")
                        except PermissionError:
                            print(f"Не удалось удалить файл: {downloaded_video_path}. Файл всё ещё используется.")

                    # Удаляем папку downloads, если она пуста
                    output_dir = os.path.dirname(downloaded_video_path)
                    if os.path.exists(output_dir) and not os.listdir(output_dir):
                        try:
                            shutil.rmtree(output_dir)
                            print(f"Папка удалена: {output_dir}")
                        except Exception as e:
                            print(f"Не удалось удалить папку: {e}")
            else:
                print("Не удалось скачать видео из TikTok.")
        else:
            print("Не удалось получить ссылку на последнее видео.")
    else:
        print("Нет новых видео на всех каналах.")

async def get_latest_tiktok_video_url(channel_url):
    """
    Получает ссылку на последнее видео TikTok канала.
    
    :param channel_url: Ссылка на канал TikTok.
    :return: Ссылка на последнее видео или None в случае ошибки.
    """
    try:
        # Настройки для yt-dlp
        ydl_opts = {
            'quiet': True,  # Отключаем лишние сообщения
            'extract_flat': True,  # Извлекаем информацию без скачивания
        }

        # Получаем информацию о канале
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(channel_url, download=False)
            if 'entries' in info_dict:  # Если это канал с несколькими видео
                latest_video_url = info_dict['entries'][0]['url']  # Ссылка на последнее видео
                return latest_video_url
            else:
                return None  # Если видео не найдено
    except Exception as e:
        print(f"Ошибка при получении ссылки на видео: {e}")
        return None

async def download_tiktok_video(video_url, output_dir="downloads"):
    """
    Скачивает видео с TikTok по ссылке и сохраняет его в указанную папку.
    
    :param video_url: Ссылка на видео TikTok.
    :param output_dir: Папка для сохранения видео (по умолчанию "downloads").
    :return: Путь к скачанному видео или None в случае ошибки.
    """
    try:
        # Создаем папку, если она не существует
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Настройки для yt-dlp
        ydl_opts = {
            'format': 'best',  # Скачиваем лучшее качество
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),  # Путь для сохранения
            'quiet': True,  # Отключаем лишние сообщения
        }

        # Скачиваем видео
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info_dict)  # Получаем путь к скачанному файлу
            return video_path

    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")
        return None