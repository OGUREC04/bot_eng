# Импортируем необходимые классы.
from value import funt, eur, dollar, btc
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import CallbackContext, CommandHandler
from datetime import *
import requests
import logging

TOKEN = '5143376368:AAGZZ3XG9FylgA8TsMOjWVtYQmt504DH0iQ'

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def start(update, bot):
    reply_keyboard = [['/registration', '/вход']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    # update.message.reply_text(
    #     "Привет! че как?", reply_markup=markup)
    # bot.send_message(chat_id=update.message.chat_id, text="Здравствуйте.", markup=markup)
    update.message.reply_text(
        "Привет! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!", reply_markup=markup)



def registration(update: Update, context: CallbackContext):
    # reply_keyboard = [['/start', '/help']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    ID = update.message.chat_id
    update.message.reply_text(
        "Введите пароль")
    print(update.message.text)
    context.bot.send_message(chat_id=ID, text=f'{ID}')


def reg1(update: Update, context: CallbackContext):





def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Создаём обработчик сообщений типа Filters.text
    # из описанной выше функции echo()
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    # text_handler = MessageHandler(Filters.text, echo)

    # Регистрируем обработчик в диспетчере.
    # dp.add_handler(text_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("registration", registration))
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()
    reply_keyboard = [['/start', '/help']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
