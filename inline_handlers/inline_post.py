from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import CallbackContext, InlineQueryHandler, ApplicationBuilder
import hashlib

async def post(update: Update, context: CallbackContext):
    """Обрабатывает inline-запросы и предлагает отправку сообщения от бота."""
    query = update.inline_query.query

    # Проверяем, начинается ли запрос с команды "post"
    if query.startswith("post "):
        # Убираем команду "post" из запроса
        post_text = query[len("post "):].strip()

        if not post_text:
            return  # Если текст пустой, ничего не делаем

        # Генерация уникального ID для результата
        result_id = hashlib.md5(post_text.encode()).hexdigest()

        # Создание результата для inline-запроса
        results = [
            InlineQueryResultArticle(
                id=result_id,
                title="Опубликовать новость",
                input_message_content=InputTextMessageContent(post_text),
                description=post_text[:50] + ("..." if len(post_text) > 50 else ""),
            )
        ]

        # Ответ на inline-запрос
        await update.inline_query.answer(results, cache_time=0)


async def handle_chosen_result(update: Update, context: CallbackContext):
    """Обрабатывает выбранный inline-результат и отправляет сообщение от имени бота."""
    # Получаем текст сообщения из выбранного результата
    post_text = update.chosen_inline_result.result_id

    # Отправляем сообщение от имени бота
    await context.bot.send_message(
        chat_id=update.chosen_inline_result.from_user.id,  # Отправляем в тот же чат
        text=post_text,
    )


def inline_post_handler(dispatcher):
    """Регистрирует inline-обработчик и обработчик выбранного результата."""
    dispatcher.add_handler(InlineQueryHandler(post))