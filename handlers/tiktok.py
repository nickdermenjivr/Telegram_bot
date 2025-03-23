import os
import shutil
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ContextTypes

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

async def tiktok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /mem. Скачивает последнее видео из TikTok канала и отправляет его в чат.
    """
    # Удаляем сообщение с командой из чата
    # await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    
    # Укажите ссылку на последнее видео TikTok
    video_url = "https://www.tiktok.com/@alexanderyur7/video/7451980859512556817"  # Замените на реальную ссылку
    
    # Скачиваем видео
    downloaded_video_path = await download_tiktok_video(video_url)
    
    if downloaded_video_path:
        try:
            # Открываем файл и отправляем видео в чат как новое сообщение
            with open(downloaded_video_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.message.chat_id,  # ID чата
                    video=video_file,  # Видеофайл
                    caption="@moldovabolgaria"  # Опциональный заголовок
                )
            print(f"Видео успешно отправлено: {downloaded_video_path}")
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
        await update.message.reply_text("Не удалось скачать видео из TikTok.")