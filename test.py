from yt_dlp import YoutubeDL

def get_video_count(channel_url):
    """
    Получает количество видео на канале TikTok.
    
    :param channel_url: Ссылка на канал TikTok.
    :return: Количество видео или None в случае ошибки.
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
                video_count = len(info_dict['entries'])
                return video_count
            else:
                return 0  # Если видео не найдено
    except Exception as e:
        print(f"Ошибка при получении количества видео: {e}")
        return None

# Пример использования
channel_url = "https://www.tiktok.com/@alexanderyur7"  # Замените на имя пользователя
video_count = get_video_count(channel_url)

if video_count is not None:
    print(f"Количество видео на канале: {video_count}")
else:
    print("Не удалось получить количество видео.")