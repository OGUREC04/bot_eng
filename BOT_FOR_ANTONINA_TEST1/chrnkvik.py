
from telegram import ParseMode
from telegram.utils.helpers import mention_html
import sys
import traceback
import logging
import psycopg2
from conf import host, user, password, db_name
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler, CallbackContext,
)

global password_from_login_nick_name
global user_data
global user_data2
global for_dict
for_dict = ['ID', 'nick_name', 'name', 'surname', 'password']
user_data = []
user_data2 = {}
password_from_login_nick_name = 0
# connect to exist database
global connection
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
connection.autocommit = True

# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора
REGISTRATION_FIRST, REGISTRATION_NICK_NAME, REGISTRATION_NAME, REGISTRATION_SURNAME, REGISTRATION_PASSWORD, LOGIN, LOGIN_NICK_NAME, LOGIN_PASSWORD, CANCEL = range(9)


# функция обратного вызова точки входа в разговор
def start(update, _):
    # Список кнопок для ответа

    reply_keyboard = [['/registration', '/login']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # Начинаем разговор с вопроса
    update.message.reply_text(
        'Меня зовут профессор Бот. Я проведу с вами беседу. '
        'Команда /cancel, чтобы прекратить разговор.\n\n'
        'Ты мальчик или девочка?',
        reply_markup=markup_key, )
    # переходим к этапу `GENDER`, это значит, что ответ
    # отправленного сообщения в виде кнопок будет список
    # обработчиков, определенных в виде значения ключа `GENDER`


def registration(update: Update, context: CallbackContext):
    # reply_keyboard = [['/start', '/help']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    print(update.message.text)
    ID = update.message.chat_id
    context.bot.send_message(chat_id=ID, text="Введите пароль", reply_markup=markup_key)
    return REGISTRATION_FIRST



def login(update: Update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id

    context.bot.send_message(chat_id=ID, text="Введите свой никнейм", reply_markup=markup_key)
    return LOGIN_NICK_NAME



def back(update: Update, context: CallbackContext):
    user = update.message.from_user
    reply_keyboard = [['/registration', '/login']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    logger.info("Юсер %s вернулся назад", user.first_name)
    ID = update.message.chat_id
    context.bot.send_message(ID,text='back',reply_markup=markup_key)
    return  ConversationHandler.END



def login_nick_name(update: Update, context: CallbackContext):
    ID = update.message.chat_id
    user_nick_name = update.message.text
    # print(update.update_id)
    try:
        reply_keyboard = [['/back']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        users_info = []
        for i in (cursor.fetchall()):
            for item in i:
                users_info.append(item)
        print(users_info)
        ###
        if user_nick_name in users_info:
            cursor.execute("""
                    SELECT password
                    FROM users
                    WHERE nick_name = %s;
                    """, (user_nick_name,))
            global password_from_login_nick_name
            password_from_login_nick_name = cursor.fetchone()[0]
            context.bot.send_message(chat_id=ID, text="Отлично теперь введите свой пароль",reply_markup=markup_key )
            return LOGIN_PASSWORD
        else:
            context.bot.send_message(chat_id=ID, text="Такого никнейма не существует, пожалуйста зарегиструйтесь или проверьте правильно ли вы ввели" ,reply_markup=markup_key)

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")


def login_password(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    ID = update.message.chat_id
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user_password = update.message.text
    try:
        reply_keyboard = [['/back']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
            SELECT password FROM users WHERE password = crypt(%s, password);""",
            (user_password,)
                       )

        ###
        if password_from_login_nick_name == cursor.fetchone()[0]:
            context.bot.send_message(chat_id=ID, text="Вы успешно вошли в аккаунт",reply_markup=markup_key )
            return back
        else:
            context.bot.send_message(chat_id=ID, text="Не верный пароль пожалуйста попробуйте еще раз" ,reply_markup=markup_key)

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")





def registration_first(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # определяем пользователя
    ID = update.message.chat_id
    user = update.message.from_user
    # Пишем в журнал пол пользователя
    logger.info("Пароль %s: %s", user.first_name, update.message.text)
    if update.message.text == '1234':
        context.bot.send_message(chat_id=ID,
                                 text="1/4"
                                      "Введите свой никнейм", reply_markup=markup_key)
        return REGISTRATION_NICK_NAME
    else:
        context.bot.send_message(chat_id=ID, text="ERROR")


def registration_nick_name(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал: %s", user.first_name, text) # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id # получаем id пользователя что бы отправлять ему сообщение а не всем
    user_nick_name = update.message.text
    print(user_nick_name)
    try:
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        users_info = []
        for i in (cursor.fetchall()):
            for item in i:
                users_info.append(item)
        print(users_info)
        ###

        ### если никнейм уже есть такой пишу типа пошел нахуй, меняй иначе перехожу дальше а никнейм сохр в глоб список который потом занесем в бд
        if user_nick_name in users_info:
            context.bot.send_message(chat_id=ID,
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему", reply_markup=markup_key)
        else:
            user_data.append(user_nick_name)
            context.bot.send_message(chat_id=ID,
                                     text="2/4"
                                          "Введите свое имя", reply_markup=markup_key)
            return REGISTRATION_NAME

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")




def registration_name(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал: %s", user.first_name,
                text)  # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id  # получаем id пользователя что бы отправлять ему сообщение а не всем
    user_name = update.message.text
    print(user_name)
    try:
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        users_info = []
        for i in (cursor.fetchall()):
            for item in i:
                users_info.append(item)
        print(users_info)
        ###

        ### если никнейм уже есть такой пишу типа пошел нахуй, меняй иначе перехожу дальше а никнейм сохр в глоб список который потом занесем в бд
        if user_name in users_info:
            context.bot.send_message(chat_id=ID,
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему", reply_markup=markup_key)
        else:
            user_data.append(user_name)
            context.bot.send_message(chat_id=ID,
                                     text="3/4"
                                          "Введите свою фамилию", reply_markup=markup_key)
            print(user_data)
            return REGISTRATION_SURNAME

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")



def registration_surname(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал: %s", user.first_name,
                text)  # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id  # получаем id пользователя что бы отправлять ему сообщение а не всем
    user_surname = update.message.text
    print(user_surname)
    try:
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        users_info = []
        for i in (cursor.fetchall()):
            for item in i:
                users_info.append(item)
        print(users_info)
        ###

        ### если никнейм уже есть такой пишу типа пошел нахуй, меняй иначе перехожу дальше а никнейм сохр в глоб список который потом занесем в бд
        if user_surname in users_info:
            context.bot.send_message(chat_id=ID,
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему", reply_markup=markup_key)
        else:
            user_data.append(user_surname)
            context.bot.send_message(chat_id=ID,
                                     text="4/4"
                                          "Введите свой пароль", reply_markup=markup_key)
            print(user_data)
            return REGISTRATION_PASSWORD

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")


def registration_password(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал: %s", user.first_name,
                text)  # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id  # получаем id пользователя что бы отправлять ему сообщение а не всем
    user_password = update.message.text
    print(user_password)
    try:
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        users_info = []
        for i in (cursor.fetchall()):
            for item in i:
                users_info.append(item)
        print(users_info)
        ###

        ### если никнейм уже есть такой пишу типа пошел нахуй, меняй иначе перехожу дальше а никнейм сохр в глоб список который потом занесем в бд
        if user_password in users_info:
            context.bot.send_message(chat_id=ID,
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",  reply_markup=markup_key)
        else:
            user_data.append(user_password)
            # context.bot.send_message(chat_id=ID,
            #                          text="4/4"
            #                               "Введите свой пароль")
            print(user_data)
            user_data.clear()
            print(user_data)
            return back

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")

# TODO: я сделал использованпие словаря в логин пассворд, теперь нужно везде заменить такой спсоб тк он удобнее и закончить функцию логин пассворд, заполнить бд еще \
# TODO: одним пользователем для норм тестов, сделать словарь  в словаре и выборку данных в соответствии

# TODO: добавить ввод данного списка (user_data) в базу данных, user_data это список в который мы добавляем все данные. \
#  Так же в файле main я создавал таблицы с хэшированными данными так что если что то забыл смотреть это там.


# TODO: почитать еще про хэш паролей и посмотреть как их могу узнавать я например для восстановления, \
#  так же если это не возможно записывать паролли и данные юзера в какой нибудь файл пока локальный


def cancel(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь не разговорчивый
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        ' Будет скучно - пиши.',
        reply_markup=ReplyKeyboardRemove()
    )
    # Заканчиваем разговор.
    return ConversationHandler.END

### error обработчик каких то ошибок как я понял свзанных с смим телеграмом или внешними показателяит не свазаными с программой по типу ошибки отпраки сообщения из за интернета
# это общая функция обработчика ошибок.
# Если нужна дополнительная информация о конкретном типе сообщения,
# добавьте ее в полезную нагрузку в соответствующем предложении `if ...`
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
###

if __name__ == '__main__':
    password = 1234
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater("1533304329:AAHVhvmtXETWT4eDJrjzmbMn7Ac1XScSbwM")
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler`
    # с состояниями GENDER, PHOTO, LOCATION и BIO
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("back", back))
    # dispatcher.add_handler(CommandHandler("login", login))
    conv_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[ CommandHandler('registration',registration), CommandHandler("login", login)],
    #MessageHandler(Filters.text & Filters.regex & (~ Filters.command)
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            REGISTRATION_FIRST: [MessageHandler(Filters.text & (~ Filters.command), registration_first)],
            REGISTRATION_NICK_NAME: [MessageHandler(Filters.text & (~ Filters.command), registration_nick_name)],
            REGISTRATION_NAME: [MessageHandler(Filters.text & (~ Filters.command), registration_name)],
            REGISTRATION_SURNAME: [MessageHandler(Filters.text & (~ Filters.command), registration_surname)],
            REGISTRATION_PASSWORD: [MessageHandler(Filters.text & (~ Filters.command), registration_password)],
            LOGIN: [MessageHandler(Filters.text & (~ Filters.command), login)],
            LOGIN_NICK_NAME: [MessageHandler(Filters.text & (~ Filters.command), login_nick_name)],
            LOGIN_PASSWORD: [MessageHandler(Filters.text & (~ Filters.command), login_password)]

        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('back', back), CommandHandler('cancel', cancel)],)

    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler,1)

    # Запуск бота
    updater.start_polling()
    updater.idle()