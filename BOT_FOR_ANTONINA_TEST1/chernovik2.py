from telegram import ParseMode
from telegram.utils.helpers import mention_html
import sys
import traceback
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler
import html
import json
import logging
import traceback

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
CHAT_ID = 713119906
logger = logging.getLogger(__name__)

# это общая функция обработчика ошибок.
# Если нужна дополнительная информация о конкретном типе сообщения,
# добавьте ее в полезную нагрузку в соответствующем предложении `if ...`


def error_handler(update, context):
    """
        Регистрирует ошибку и уведомляет
        разработчика сообщением telegram.
    """
    # Пишем ошибку, прежде чем что-то делать. Вдруг что-то сломается.
    logger.error(msg="Исключение при обработке сообщения:", exc_info=context.error)

    # `traceback.format_exception` возвращает обычное сообщение python
    # об исключении в виде списка строк, поэтому объединяем их вместе.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Создаем сообщение с некоторой разметкой и дополнительной
    # информацией о том, что произошло. Возможно, придется добавить некоторую
    # логику для работы с сообщениями длиной более 4096 символов.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'Возникло исключение при обработке сообщения.\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Отправляем сообщение разработчику
    context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML)

def bad_command(_, context):
    """Вызывает ошибку, чтобы вызвать обработчик ошибок."""
    context.bot.wrong_method_name()

def start(update, _):
    update.effective_message.reply_html(
        'Принудительный вызов ошибки `/bad_command`\n'
        f'Ваш идентификатор чата <code>{update.effective_chat.id}</code>.'
    )
# Функция-обработчик ошибок



def error(update, context):
    # добавьте все идентификаторы разработчиков в этот список.
    # Можно добавить идентификаторы каналов или групп.
    devs = [713119906]
   # Уведомление пользователя об этой проблеме.
   # Уведомления будут работать, только если сообщение НЕ является
   # обратным вызовом, встроенным запросом или обновлением опроса.
   # В случае, если это необходимо, то имейте в виду, что отправка
   # сообщения может потерпеть неудачу
    if update.effective_message:
        text = "К сожалению произошла ошибка в момент обработки сообщения. " \
               "Мы уже работаем над этой проблемой."
        update.effective_message.reply_text(text)
    # Трассировка создается из `sys.exc_info`, которая возвращается в
    # как третье значение возвращаемого кортежа. Затем используется
    # `traceback.format_tb`, для получения `traceback` в виде строки.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # попробуем получить как можно больше информации из обновления telegram
    payload = []
    # обычно всегда есть пользователь. Если нет, то это
    # либо канал, либо обновление опроса.
    if update.effective_user:
        bad_user = mention_html(update.effective_user.id, update.effective_user.first_name)
        payload.append(f' с пользователем {bad_user}')
    # есть ситуаций, когда что то с чатом
    if update.effective_chat:
        payload.append(f' внутри чата <i>{update.effective_chat.title}</i>')
        if update.effective_chat.username:
            payload.append(f' (@{update.effective_chat.username})')
    # полезная нагрузка - опрос
    if update.poll:
        payload.append(f' с id опроса {update.poll.id}.')
    # Поместим это в 'хорошо' отформатированный текст
    text = f"Ошибка <code>{context.error}</code> случилась{''.join(payload)}. " \
           f"Полная трассировка:\n\n<code>{trace}</code>"
    # и отправляем все разработчикам
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # Необходимо снова вызывать ошибку, для того, чтобы модуль `logger` ее записал.
    # Если вы не используете этот модуль, то самое время задуматься.
    raise



if __name__ == '__main__':

    updater = Updater("1533304329:AAHVhvmtXETWT4eDJrjzmbMn7Ac1XScSbwM")
    dispatcher = updater.dispatcher

    # Зарегистрируем команды...
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('bad_command', bad_command))

    # ...и обработчик ошибок
    dispatcher.add_error_handler(error_handler)

    # ...и обработчик ошибок


    # Запускаем бота
    updater.start_polling()
    updater.idle()