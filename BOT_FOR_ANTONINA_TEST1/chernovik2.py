from uuid import uuid4
from telegram import ParseMode
from telegram.utils.helpers import mention_html
from template_of_tasks import some_task
import sys
import traceback
import logging
import psycopg2
from config import host, user, password, db_name
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    JobQueue
)



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
REGISTRATION_FIRST, REGISTRATION_NICK_NAME, REGISTRATION_NAME, REGISTRATION_SURNAME, REGISTRATION_PASSWORD, \
LOGIN, LOGIN_DATA,  CANCEL = range(8)

RANDOM_TASK_ANSWER, DICTIONARY_WORD, TIME_FOR_TASK_ANSWER = range(3)


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

    context.bot.send_message(chat_id=ID, text="Введите свой никнейм и пароль через пробел"
                                              "Пример: Вацо 228", reply_markup=markup_key)
    return LOGIN_DATA


def back(update: Update, context: CallbackContext):
    user = update.message.from_user
    reply_keyboard = [['/registration', '/login']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    logger.info("Юсер %s вернулся назад", user.first_name)
    ID = update.message.chat_id
    context.bot.send_message(ID, text='back', reply_markup=markup_key)
    return ConversationHandler.END


def step_back(update: Update, context: CallbackContext):
    key = str(update.effective_user.id)
    key_for_step = key + 'step'
    print(key_for_step)
    for_stages = context.bot_data[key_for_step]
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    ID = update.message.chat_id
    context.bot.send_message(chat_id=ID, text="шаг назад", reply_markup=markup_key)
    if for_stages == REGISTRATION_NICK_NAME:
        print(context.bot_data[key])
        context.bot_data[key] = context.bot_data[key].replace(f'{context.bot_data[key]}','')
        print(context.bot_data[key])
        context.bot.send_message(chat_id=ID, text="1/4"
                                                  "Введите свой ник", reply_markup=markup_key)
    elif for_stages == REGISTRATION_NAME:
        context.bot_data[key].pop(1)
        context.bot.send_message(chat_id=ID,
                                 text="2/4"
                                      "Введите свое имя", reply_markup=markup_key)
    elif for_stages == REGISTRATION_SURNAME:
        context.bot_data[key].pop(2)
        context.bot.send_message(chat_id=ID,
                                 text="3/4"
                                      "Введите свою фамилию", reply_markup=markup_key)
    elif for_stages == REGISTRATION_PASSWORD:
        context.bot_data[key].pop(3)
        context.bot.send_message(chat_id=ID,
                                 text="4/4"
                                      "Введите свой пароль", reply_markup=markup_key)

    context.bot_data.pop(key_for_step)
    return for_stages


def login_data(update: Update, context: CallbackContext):
    log = True
    pas = True
    password_user_nick_name = None
    password_from_user = None
    ID = update.message.chat_id
    user_data = update.message.text.partition(' ')
    print(user_data)
    print('----------', context.bot_data)
    # print(update.update_id)
    try:
        reply_keyboard = [['/back']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        ###  Извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
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

        ### По заданному никнейму смотрю пароль от аккаунта с этим ником в первом execute, потом смотрю есть ли в бд хеш пароля введенного пользователeм\
        if user_data[0] in users_info:
            cursor.execute("""
                    SELECT password
                    FROM users
                    WHERE nick_name = %s;
                    """, (user_data[0],))
            password_user_nick_name = cursor.fetchone()[0]
            cursor.execute("""
                         SELECT password FROM users WHERE password = crypt(%s, password);""",
                           (user_data[2],)
                           )
            password_from_user = cursor.fetchone()[0]
        else:
            log = False
        ###

        ### пароль этого аккауниа, сравниваю первый хеш со вторым, если они равны - значит пароль верный
        if password_user_nick_name == password_from_user:
            print('coc')
        else:
            pas = False
        ###

        ### если то и то True то все супер
        if pas and log:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE nick_name = %s;
                """,(user_data[0],)
            )
            user_id = (cursor.fetchall()[0][0])
            print(user_id)
            key = str(update.effective_user.id)
            context.bot_data[key] =[ user_id, password_from_user, user_data[0], user_data[2], 'after_login']
            print(context.bot_data[key])
            markup_key = ReplyKeyboardRemove()  # удаление клавы

            context.bot.send_message(chat_id=ID, text="Отлично", reply_markup=markup_key)

            return ConversationHandler.END, after_login(update, context)
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Такого никнейма или пароля не существует, пожалуйста зарегиструйтесь или проверьте правильно ли вы ввели",
                                     reply_markup=markup_key)

        ###

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")
        ###

def registration_first(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # определяем пользователя
    ID = update.message.chat_id
    user = update.message.from_user
    # Пишем в журнал пол пользователя
    logger.info("Пароль %s: %s", user.first_name, update.message.text)
    print(update.message.text)
    if update.message.text == '1234':
        context.bot.send_message(chat_id=ID,
                                 text="1/4"
                                      "Введите свой никнейм", reply_markup=markup_key)
        return REGISTRATION_NICK_NAME
    else:
        context.bot.send_message(chat_id=ID, text="ERROR")


def registration_nick_name(update, context: CallbackContext):
    # print(update.effective_user.id)
    key = str(update.effective_user.id)
    key_for_step = key+'step'
    reply_keyboard = [['/back', '/step_back']]
    context.bot_data[key_for_step] = REGISTRATION_NICK_NAME
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал ник: %s", user.first_name,
                text)  # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id  # получаем id пользователя что бы отправлять ему сообщение а не всем
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
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",
                                     reply_markup=markup_key)
        else:
            context.bot_data[key] = user_nick_name # передаем контексту в словарь наш никнейм что бы сохранить промежуточные данные, с ключом-id user в телеге
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
    # print(update.effective_user.id)
    key = str(update.effective_user.id) # id user
    first_stage = context.bot_data.get(key, 'Not found') # забираем никнейм из предыдущего шага
    # print('--------------', first_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key+'step'
    context.bot_data[key_for_step] = REGISTRATION_NAME
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал имя: %s", user.first_name,
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
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",
                                     reply_markup=markup_key)
        else:
            context.bot_data[key] = [''.join(first_stage), user_name ] # помещаем так же в словарь контекста по ключю - id usera, тлько теперь список из имени и ника
            context.bot.send_message(chat_id=ID,
                                     text="3/4"
                                          "Введите свою фамилию", reply_markup=markup_key)
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
    # print(update.effective_user.id)
    key = str(update.effective_user.id) # user id
    second_stage = context.bot_data.get(key, 'Not found') # список имени и ника
    # print('--------------', second_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key+'step'
    context.bot_data[key_for_step] = REGISTRATION_SURNAME
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал фамилию: %s", user.first_name,
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
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",
                                     reply_markup=markup_key)
        else:
            context.bot_data[key] = second_stage+[user_surname] # помещаем так же в словарь контекста по ключю - id usera, список,\
            # хз почему выделяется если по человечески делать то не работает
            # print('--------',context.bot_data[key])
            context.bot.send_message(chat_id=ID,
                                     text="4/4"
                                          "Введите свой пароль", reply_markup=markup_key)
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
    # print(update.effective_user.id)
    print(context.bot_data)
    key = str(update.effective_user.id) # user id
    third_stage = context.bot_data.get(key, 'Not found') # список ник,имя,фамилия
    # print('--------------',third_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key+'step'
    context.bot_data[key_for_step] = REGISTRATION_PASSWORD
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал пароль: %s", user.first_name,
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
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",
                                     reply_markup=markup_key)
        else:
            markup_key = ReplyKeyboardRemove()  # удаление клавы
            context.bot_data[key] = third_stage + [user_password]# помещаем так же в словарь контекста по ключю - id usera, список,\
            # хз почему выделяется если по человечески делать то не работает
            print('--------', context.bot_data[key])
            print(context.bot_data)
            context.bot_data.pop(key)
            context.bot_data.pop(key_for_step)
            context.bot.send_message(chat_id=ID,
                                     text="вы успешно зарегались", reply_markup=markup_key)
            return login(update,context)

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")


def cancel(update, context: CallbackContext):
    pass


def after_login(update, context: CallbackContext):
    key = str(update.effective_user.id)
    print(context.bot_data[key])
    ID = update.message.chat_id
    if 'after_login'in context.bot_data[key]: # context.bot_data[key] where key = str(update.effective_user.id) хранит данные о пользователи после логина его изменять нельзя
        reply_keyboard = [['/random_task', '/dictionary', '/timer_task', '/unset'   ]]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=ID,
                                 text="выберите варианты",
                                 reply_markup=markup_key)
    else:
        context.bot.send_message(chat_id=ID,
                                 text="Сначала нужно войти или зарегистрироваться")
        return back(update,context)



def random_task(update, context: CallbackContext):
    markup_key = ReplyKeyboardRemove()
    ID = update.message.chat_id
    task = some_task()
    try:
        key = str(update.effective_user.id)
        print('-------',context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                        text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        print('000000000000',update.effective_user.id)
        key_1 = key+' answer'
        if 'after_login'in context.bot_data[key]:
            ID = update.message.chat_id
            print('=========',task[1])
            context.bot.send_message(chat_id=ID,
                                         text=task[0])
            context.bot_data[key_1] = task[1]
            return RANDOM_TASK_ANSWER


        else:
            context.bot.send_message(chat_id=ID,
                                     text="Сначала нужно войти или зарегистрироваться, /back",reply_markup=markup_key)
            return ConversationHandler.END


def random_task_answer(update, context: CallbackContext):
    reply_keyboard = [['/random_task', '/dictionary', '/timer_task', '/unset']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id
    ans = update.message.text
    key = str(update.effective_user.id)
    if 'after_login' in context.bot_data[key]:
        print(ans) #дописать обработку ответа
        print(context.bot_data)
        # TODO: написать сохранинние и подсчет результатов
        try:
            key_1 = (str(update.effective_user.id) + ' answer')
            if ans == context.bot_data[key_1]:
                context.bot.send_message(chat_id=ID,
                                         text="все правильно", reply_markup=markup_key)
                return ConversationHandler.END
            else:
                context.bot.send_message(chat_id=ID,
                                         text="что то пошло не так")
        except KeyError:
            context.bot.send_message(chat_id=ID,
                                     text="все хуево")
    else:
        context.bot.send_message(chat_id=ID,
                                 text="иди регайся xuylo3")
        return ConversationHandler.END


def dictionary(update, context: CallbackContext):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        print('-------',context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                        text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        if 'after_login' in context.bot_data[key]:
            print(context.bot_data[key])
            context.bot.send_message(chat_id=ID,
                                     text="введите слово и перевод, через пробел"
                                          "пример: Вацо Vaco")
            return DICTIONARY_WORD
        else:
            context.bot.send_message(chat_id=ID,
                                     text="иди регайся xuylo3")
            return ConversationHandler.END



def dictionary_word(update, context: CallbackContext):
    key = str(update.effective_user.id)
    ID = update.message.chat_id
    if 'after_login' in context.bot_data[key]:
        words = update.message.text.partition(' ')
        word = words[0]
        translate = words[2]
        user_id = context.bot_data[key][0]
        print(user_id)
        print(word, translate)
        print(words)  # дописать обработку ответа
        print(context.bot_data[key])
        try:
            cursor = connection.cursor()
            cursor.execute("""
                    SELECT  * FROM user_dictionary;
                    """)
            users_info = []
            for i in (cursor.fetchall()):
                for item in i:
                    users_info.append(item)
            print(users_info)


            ###
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                cursor.close()
                # connection.close()
                print("[INFO] PostgreSQL connection closed")
            ###
    else:
        context.bot.send_message(chat_id=ID,
                                 text="иди регайся xuylo2")
        return ConversationHandler.END



def unset(update, context):
    key_for_job_stop = str(update.effective_user.id) + 'stop_job'
    context.bot_data[key_for_job_stop] = True
    print(context.bot_data[key_for_job_stop])



def timer_task(update, context: CallbackContext):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        print('-------',context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                        text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        key_for_job_stop = key + 'stop_job'
        context.bot_data[key_for_job_stop] = False
        print(context.bot_data[key_for_job_stop])
        if key_for_job_stop == True:
            print('ахуеть я умный')
            return ConversationHandler.END
        else:
            if 'after_login' in context.bot_data[key]:
                key_1 = str(update.effective_user.id) + ' timer_task'
                context.bot_data[key_1] = ID
                job_queue = updater.job_queue
                context.bot.send_message(chat_id=ID,
                                             text="задание в пути")
                job_queue.run_repeating(time_for_task,context=[ID, str(ID)+' time'],interval=20.0,name=str(update.effective_user.id))
                return TIME_FOR_TASK_ANSWER
            else:
                context.bot.send_message(chat_id=ID,
                                             text="иди регайся xuylo")
                return ConversationHandler.END

def time_for_task(context: CallbackContext):
    task = some_task()
    print(context.job.context[0])
    ID = context.job.context[0]
    job = context.job.context[1]
    context.bot.send_message(chat_id=ID, text=task[0])
    context.bot_data[job] = task[1]
    print(context.bot_data[job])
    print(task[1])


def time_for_task_answer(update, context):
    key = str(update.effective_user.id)
    ID = update.message.chat_id
    if 'after_login' in context.bot_data[key]:
        reply_keyboard = [['/random_task', '/dictionary', '/timer_task', '/unset']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        ans = update.message.text
        key_1 = str(update.effective_user.id)+' time'
        print(context.args)
        print(context.bot_data[key_1])
        if ans == context.bot_data[key_1]:
            context.bot.send_message(chat_id=ID,
                                     text="все правильно", reply_markup=markup_key)
        else:
            context.bot.send_message(chat_id=ID,
                                     text="что то пошло не так")
    else:
        context.bot.send_message(chat_id=ID,
                                 text="иди регайся долбаеб")
        return ConversationHandler.END







# TODO: изменить бд что бы сохранять все результаты и тд

# TODO: написать ограничение на использование вызова команд после логина

# TODO: с регистрацией в общем плане все готово, остались толдько не большие доработки. Теперь
# 1) разобрать в связях бд \
# 2) придумать шаблоны заданий и реализовать пока хотя бы один
# 3) сделать добавления слов в словарь и парсить их с сайтов с преводам, так же записывать эти слова в свои файлы


# TODO: я сделал использованпие словаря в логин пассворд, теперь нужно везде заменить такой спсоб тк он удобнее и закончить функцию логин пассворд, заполнить бд еще \

# TODO: добавить ввод данного списка (user_data) в базу данных, user_data это список в который мы добавляем все данные. \
#  Так же в файле main я создавал таблицы с хэшированными данными так что если что то забыл смотреть это там.


# TODO: почитать еще про хэш паролей и посмотреть как их могу узнавать я например для восстановления, \
#  так же если это не возможно записывать паролли и данные юзера в какой нибудь файл пока локальный




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
        entry_points=[CommandHandler('registration', registration),
                      CommandHandler("login", login)],
        # MessageHandler(Filters.text & Filters.regex & (~ Filters.command)
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            REGISTRATION_FIRST: [
                MessageHandler(Filters.text & (~ Filters.command), registration_first)],
            REGISTRATION_NICK_NAME: [
                MessageHandler(Filters.text & (~ Filters.command), registration_nick_name)],
            REGISTRATION_NAME: [MessageHandler(Filters.text & (~ Filters.command), registration_name)],
            REGISTRATION_SURNAME: [
                MessageHandler(Filters.text & (~ Filters.command), registration_surname)],
            REGISTRATION_PASSWORD: [
                MessageHandler(Filters.text & (~ Filters.command), registration_password)],
            LOGIN: [MessageHandler(Filters.text & (~ Filters.command), login)],
            LOGIN_DATA: [MessageHandler(Filters.text & (~ Filters.command), login_data)],
            # LOGIN_PASSWORD: [MessageHandler(Filters.text & (~ Filters.command), login_password,run_async=True)],
            # AFTER_LOGIN: [MessageHandler(Filters.text & (~ Filters.command), after_login)]


        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('back', back), CommandHandler('cancel', cancel),
                   CommandHandler('step_back', step_back)]
    )

    conv_handler_2 = ConversationHandler(
        entry_points=[CommandHandler('random_task', random_task),
                      CommandHandler('dictionary', dictionary),
                      CommandHandler('timer_task', timer_task),
                      CommandHandler('unset', unset)],

        states={
            RANDOM_TASK_ANSWER: [MessageHandler(Filters.text & (~ Filters.command), random_task_answer)],
            DICTIONARY_WORD: [MessageHandler(Filters.text & (~ Filters.command), dictionary_word)],
            TIME_FOR_TASK_ANSWER: [MessageHandler(Filters.text & (~ Filters.command), time_for_task_answer)]
        },
        fallbacks=[]

    )
#  run_async=True
    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler, 1)
    dispatcher.add_handler(conv_handler_2,2)

    # Запуск бота
    updater.start_polling()
    updater.idle()
