# на заметку: если не писать return ConversationHandler.END то функция являющаяся этапом диалога (Conversation) полность запуститься заново а не с какой то ее части
import prettytable as pt
import pandas
import datetime
from uuid import uuid4
import pytz
from telegram import ParseMode
from telegram.utils.helpers import mention_html
from template_of_tasks import some_task, taskes
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
global black_list
black_list = []
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
LOGIN, LOGIN_DATA, CANCEL = range(8)

RANDOM_TASK_ANSWER, DICTIONARY_WORD, TIME_FOR_TASK_ANSWER = range(3)


# функция обратного вызова точки входа в разговор
def start(update, _):
    # Список кнопок для ответа

    reply_keyboard = [['/registration', '/login']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # Начинаем разговор с вопроса
    update.message.reply_text('Привет! \n'
                              'Я телеграм бот, который поможет тебе выучить англиский ;)\n'
                              'Зарегистрируйся или войди в аккаунт, что бы перейти к моему функционалу',
                              reply_markup=markup_key, )
    # переходим к этапу `GENDER`, это значит, что ответ
    # отправленного сообщения в виде кнопок будет список
    # обработчиков, определенных в виде значения ключа `GENDER`

def administrator(update: Update, context: CallbackContext):
    ID = update.message.chat_id
    context.bot.send_message(chat_id=ID, text="Введите пароль ученика")
    pass


def registration(update: Update, context: CallbackContext):
    # reply_keyboard = [['/start', '/help']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    print(update.message.text)
    key = str(update.effective_user.id)
    ID = update.message.chat_id
    global black_list
    if key in black_list:
        context.bot.send_message(chat_id=ID, text="Вы уже регистрировались \n"
                                                  "Я отправлю вас на вход в аккаунт.\n"
                                                  "Если хотите восстановить пароль обратитесь к админу(к сожалению пока только так)", reply_markup=markup_key)
        return login(update, context)
    else:
        context.bot.send_message(chat_id=ID, text="Введите пароль ученика", reply_markup=markup_key)
        return REGISTRATION_FIRST


def login(update: Update, context: CallbackContext):
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    ID = update.message.chat_id

    context.bot.send_message(chat_id=ID, text="Введите свой никнейм и пароль через пробел \n"
                                              "Пример: Вацо 228 ", reply_markup=markup_key)
    return LOGIN_DATA


def back(update: Update, context: CallbackContext):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        if 'after_login' in context.bot_data[key]:
            context.bot.send_message(ID, text='Не возможно использовать после регистрации')

        else:
            user = update.message.from_user
            reply_keyboard = [['/registration', '/login']]
            markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            logger.info("Юсер %s вернулся назад", user.first_name)
            context.bot.send_message(ID, text='Вы вернулись в самое начало', reply_markup=markup_key)
            return ConversationHandler.END
    except Exception as _ex:
        user = update.message.from_user
        reply_keyboard = [['/registration', '/login']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        logger.info("Юсер %s вернулся назад", user.first_name)
        context.bot.send_message(ID, text='Вы вернулись в самое начало', reply_markup=markup_key)
        return ConversationHandler.END


def step_back(update: Update, context: CallbackContext):
    key = str(update.effective_user.id)
    key_for_step = key + 'step'
    print(key_for_step)
    for_stages = context.bot_data[key_for_step]
    reply_keyboard = [['/back']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id
    context.bot.send_message(chat_id=ID, text="шаг назад", reply_markup=markup_key)
    if for_stages == REGISTRATION_NICK_NAME:
        print(context.bot_data[key])
        context.bot_data[key] = context.bot_data[key].replace(f'{context.bot_data[key]}', '')
        print(context.bot_data[key])
        context.bot.send_message(chat_id=ID, text="Этап: 1/4 "
                                      "Введите свой никнейм", reply_markup=markup_key)
    elif for_stages == REGISTRATION_NAME:
        context.bot_data[key].pop(1)
        context.bot.send_message(chat_id=ID,
                                 text="Этап: 2/4 "
                                          "Введите свое имя", reply_markup=markup_key)
    elif for_stages == REGISTRATION_SURNAME:
        context.bot_data[key].pop(2)
        context.bot.send_message(chat_id=ID,
                                 text="Этап: 3/4 "
                                          "Введите свою фамилию", reply_markup=markup_key)
    elif for_stages == REGISTRATION_PASSWORD:
        context.bot_data[key].pop(3)
        context.bot.send_message(chat_id=ID,
                                 text="Этап: 4/4 "
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
        markup_key = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

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
                """, (user_data[0],)
            )
            user_id = (cursor.fetchall()[0][0])
            print(user_id)
            key = str(update.effective_user.id)
            context.bot_data[key] = [user_id, password_from_user, user_data[0], user_data[2], 'after_login']
            print(context.bot_data[key])
            markup_key = ReplyKeyboardRemove()  # удаление клавы
            global black_list
            if key in black_list:
                pass
            else:
                black_list = []
                black_list.append(key)
            context.bot.send_message(chat_id=ID, text="Все супер, такого вроде помню", reply_markup=markup_key)

            return ConversationHandler.END, after_login(update,
                                                        context)  # выдает предупреждение но работает нормально. Тут завенршается этап регистрации и входа
            # все предадущие функции должны быть заблокированы
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
                                 text="Этап: 1/4 "
                                      "Введите свой никнейм", reply_markup=markup_key)
        return REGISTRATION_NICK_NAME
    else:
        context.bot.send_message(chat_id=ID, text="ERROR")


def registration_nick_name(update, context: CallbackContext):
    # print(update.effective_user.id)
    key = str(update.effective_user.id)
    key_for_step = key + 'step'
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

        ### если никнейм уже есть такой , меняй иначе перехожу дальше а никнейм сохр
        if user_nick_name in users_info:
            context.bot.send_message(chat_id=ID,
                                     text="Такой никнейм уже занят, пожалуйста выберите другой или войдиете в систему",
                                     reply_markup=markup_key)
        else:
            context.bot_data[
                key] = user_nick_name  # передаем контексту в словарь наш никнейм что бы сохранить промежуточные данные, с ключом-id user в телеге
            context.bot.send_message(chat_id=ID,
                                     text="Этап: 2/4 "
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
    key = str(update.effective_user.id)  # id user
    first_stage = context.bot_data.get(key, 'Not found')  # забираем никнейм из предыдущего шага
    # print('--------------', first_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key + 'step'
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

        context.bot_data[key] = [''.join(first_stage),
                                     user_name]  # помещаем так же в словарь контекста по ключю - id usera, тлько теперь список из имени и ника
        context.bot.send_message(chat_id=ID,
                                     text="Этап: 3/4 "
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
    key = str(update.effective_user.id)  # user id
    second_stage = context.bot_data.get(key, 'Not found')  # список имени и ника
    # print('--------------', second_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key + 'step'
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

        context.bot_data[key] = second_stage + [user_surname]  # помещаем так же в словарь контекста по ключю - id usera, список,\
            # хз почему выделяется если по человечески делать то не работает
            # print('--------',context.bot_data[key])
        context.bot.send_message(chat_id=ID,
                                     text="Этап: 4/4 "
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
    key = str(update.effective_user.id)  # user id
    third_stage = context.bot_data.get(key, 'Not found')  # список ник,имя,фамилия
    # print('--------------',third_stage)
    reply_keyboard = [['/back', '/step_back']]
    key_for_step = key + 'step'
    context.bot_data[key_for_step] = REGISTRATION_PASSWORD
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user = update.message.from_user
    text = update.message.text
    logger.info("Пользователь %s рассказал пароль: %s", user.first_name,
                text)  # это какая то ересть котора выводит мне в панель что говорит юсер
    ID = update.message.chat_id  # получаем id пользователя что бы отправлять ему сообщение а не всем
    user_password = update.message.text
    cursor = connection.cursor()
    print(user_password)
    try:

        markup_key = ReplyKeyboardRemove()  # удаление клавы
        context.bot_data[key] = third_stage + [user_password]  # помещаем так же в словарь контекста по ключю - id usera, список,\
            # хз почему выделяется если по человечески делать то не работает
        print('--------', context.bot_data[key])
        nick_name = context.bot_data[key][0]
        user_name = context.bot_data[key][1]
        user_surname = context.bot_data[key][2]
        password_usr = context.bot_data[key][3]
        print(context.bot_data)
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor.execute(
            """INSERT INTO users (nick_name, user_name, user_surname, password) VALUES
                (%s, %s, %s, crypt(%s, gen_salt('bf', 8)));""",
            (nick_name, user_name, user_surname, password_usr))
        print("[INFO] Data was succefully inserted")
        ###
        context.bot_data.pop(key)
        context.bot_data.pop(key_for_step)
        context.bot.send_message(chat_id=ID,
                                     text="Вы успешно зарегистрировались, я сразу перенесу вас на вход в аккаунт\n"
                                          "Не благодорите ;}"
                                          "", reply_markup=markup_key)
        global black_list
        black_list = []
        black_list.append(key)
        return login(update, context)

        ###
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")


# посредник между окончанием регистрации и начлаом пользовтаельских возможностей, до входа запустить нельзя стоит защита
def after_login(update, context: CallbackContext):
    key = str(update.effective_user.id)
    print(context.bot_data[key])
    ID = update.message.chat_id
    if 'after_login' in context.bot_data[
        key]:  # context.bot_data[key] where key = str(update.effective_user.id) хранит данные о пользователи после логина его изменять нельзя
        reply_keyboard = [['/random_task', '/dictionary','/your_dictionary', '/exit']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=ID,
                                 text="Теперь вам доступен - /help\n"
                                      "Тут описаны все команды бота, возможные причины не работы некоторых из них а так же возможность удалить аккаунт\n"
                                      "Выберите чем хотите заняться",
                                 reply_markup=markup_key)
        return timer_task(update, context)
    else:
        context.bot.send_message(chat_id=ID,
                                 text="Сначала нужно войти или зарегистрироваться")
        return back(update, context)


# случайное задание
def random_task(update, context: CallbackContext):
    markup_key = ReplyKeyboardRemove()
    ID = update.message.chat_id
    task = taskes()  # из template_of_tasks берем случаное задание в которой функция с рандомом
    try:
        key = str(
            update.effective_user.id)  # ключ во всех функция это id пользователя, по этому ключю context содержит всю информацию о пользоваиеле
        print('-------', context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                                 text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        print('юзер id:', update.effective_user.id)
        key_1 = key + ' answer'  # передаем в ключ-посредник ответ что бы сверить его в след функции
        if 'after_login' in context.bot_data[key]:
            ID = update.message.chat_id
            print('ответ на задание', task[2])
            context.bot.send_message(chat_id=ID,
                                     text='Сейчас я пришлю вам случайное задания из одного из лучших учебников!\n'
                                          'На выполнение у тебя будет одна попытка, после ответа я пришлю ваши ошибки\n'
                                          'Если вы введете слишком много или мало ответов, то попытка не засчитается\n'
                                          'Ответ вводите в одно сообщение, через пробел, без знаков препинания.')
            context.bot.send_message(chat_id=ID,
                                     text=task[0])
            context.bot_data[key_1] = task[2]
            return RANDOM_TASK_ANSWER


        else:
            context.bot.send_message(chat_id=ID,
                                     text="Сначала нужно войти или зарегистрироваться, /back", reply_markup=markup_key)
            return ConversationHandler.END


def random_task_answer(update, context: CallbackContext):
    key = str(update.effective_user.id)  # ключ с данными юзера
    user_id = context.bot_data[key][0]  # id из базы данной
    reply_keyboard = [['/random_task', '/dictionary','/your_dictionary', '/exit']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id  # id чата в тг
    messege_from_user = update.message.text  # сообщение от юзера
    answer = messege_from_user.split()  # преобразуем сообщение в список
    key = str(
        update.effective_user.id)  # ключ во всех функция это id пользователя, по этому ключю context содержит всю информацию о пользоваиеле
    if 'after_login' in context.bot_data[key]:  # проверка на регистрацию
        # TODO: написать сохранинние и подсчет результатов
        try:
            task = 'unit39_1_Tick_the_words'  # задание юнит
            date = datetime.date.today()  # дата выполнения задания
            cursor = connection.cursor()  # отркываем соединение с базой данных
            key_1 = (str(update.effective_user.id) + ' answer')  # ключ посредник
            right_answer = (context.bot_data[key_1]).split()  # правильный ответ
            print('ответ на задание', right_answer)
            result = {}  # словарь гду будут храниться ошибки
            errors = []  # список что бы записать все ошибки в бд
            result_ratio = ''  # строка по типу 4/5 - соотношение результата для записи в бд
            if len(right_answer) == len(answer):  # проверка на недостаток или избыток ответов
                for i in range(len(right_answer)):
                    if right_answer[i] == answer[i]:
                        pass
                    else:
                        result[i + 1] = [answer[i], right_answer[i]]
                print(result)
                if len(result) == 0:  # если результат равен нулю соответственно ошибок нет
                    errors.append('нет ошибок')
                    result_ratio = f"{len(right_answer)}/{len(right_answer)}"
                    context.bot.send_message(chat_id=ID,
                                             text="все правильно", reply_markup=markup_key)
                else:  # смотрим какие ошибки в каком задании
                    count = 0
                    for i in result:
                        context.bot.send_message(chat_id=ID,
                                                 text=f"в задании {i} оишбка"
                                                      f"- {result[i][0]}, правильно будет - {result[i][1]}")
                        errors.append(
                            f"задние {str(i)}, оишбка {str(result[i][0])}, правильно {str(result[i][1])} ||| ")
                        count += 1
                    result_ratio = f"{len(right_answer) - count}/{len(right_answer)}"
                    context.bot.send_message(chat_id=ID,
                                             text=f"результат: {result_ratio}", reply_markup=markup_key)
                    print(user_id)
                print('result', result_ratio)
                print('task', task)
                print('errors', ' '.join(errors))
                print('date', date)
                print('id', int(user_id))
                ### добавляю бд все данные о выполненом задании
                cursor.execute(
                    """
                            INSERT INTO random_task(result, task, errors, date_do_task, fk_random_task_user) VALUES
                            (%s, %s, %s, %s, %s);
                    """,
                    (result_ratio, task, ' '.join(errors), date, int(user_id)))
                print("[INFO] Data was succefully inserted")
                return ConversationHandler.END
            else:
                context.bot.send_message(chat_id=ID,
                                         text="слишком много или мало ответов))", reply_markup=markup_key)
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
            context.bot.send_message(chat_id=ID,
                                     text="все плохо")
        finally:
            if connection:
                cursor.close()
                # connection.close()
                print("[INFO] PostgreSQL connection closed")
    else:
        context.bot.send_message(chat_id=ID,
                                 text="иди регайся xuylo3")
        return ConversationHandler.END


def dictionary(update, context: CallbackContext):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        print('-------', context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                                 text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        if 'after_login' in context.bot_data[key]:
            print(context.bot_data[key])
            context.bot.send_message(chat_id=ID,
                                     text="введите слово и перевод, через пробел\n"
                                          "пример: Кот Cat")
            return DICTIONARY_WORD
        else:
            context.bot.send_message(chat_id=ID,
                                     text="нужно пройти регистрацию")
            return ConversationHandler.END


def dictionary_word(update, context: CallbackContext):
    reply_keyboard = [['/random_task', '/dictionary','/your_dictionary', '/exit']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    key = str(update.effective_user.id)
    ID = update.message.chat_id
    if 'after_login' in context.bot_data[key]:
        words = (update.message.text).split()  # сделать строгий пррием ответа, пока делит сообщение на три части разделяя пробелом(одна из частей пробел)
        if len(words) != 2:
            context.bot.send_message(chat_id=ID,
                                     text="Проверьте правильно ли вы ввели слово и перевод(формат)", reply_markup=markup_key)
        else:
            try:
                word = words[0]
                translate = words[1]
                user_id = context.bot_data[key][0]
                print(user_id)
                print(word, translate)
                print(words)  # дописать обработку ответа
                print(context.bot_data[key])
                cursor = connection.cursor()
                cursor.execute("""
                        INSERT into  user_dictionary(word, word_translate, fk_user_dictionary_users) VALUES 
                        (%s, %s, %s);
                        """,
                        (word, translate, user_id)
                        )
                context.bot.send_message(chat_id=ID,
                                         text="word has been added", reply_markup=markup_key)
                return ConversationHandler.END

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
                                 text="Нужно пройти регистрацию")
        return ConversationHandler.END


######
def your_dictionary(update, context: CallbackContext):
    reply_keyboard = [['/random_task', '/dictionary','/your_dictionary', '/exit']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id
    cursor = connection.cursor()
    try:
        key = str(update.effective_user.id)
        if 'after_login' in context.bot_data[key]:
            user_id = context.bot_data[key][0]
            cursor.execute("""
            SELECT * FROM  user_dictionary WHERE fk_user_dictionary_users = (%s);
            """,
            (user_id,)
            )
            # в это блоке мы делаем табличку с пмощью pandas, колонки которые нам нужны превращаем в списки, делаем из них список \
            # со слов русским-английским и помещаем в таблицу с помощью какой то билблиотеки
            df = pandas.DataFrame(cursor.fetchall(),
                                  columns=['id', 'word', 'word_translate', 'fk_user_dictionary_users'])
            x = (df['word'].tolist())
            y = (df['word_translate'].tolist())
            # print(df.groupby(['word','word_translate' ], as_index=False))
            # dic = {'Рус': 'Eng'}
            # for i in range(len(x)):
            #     dic[x[i]] = f'{y[i]}'
            # print(dic)
            # print(*{f'{k} | {v}\n' for (k,v) in dic.items()})
            len_l = len(x)
            dic = []
            for i in range(len_l):
                dic.append([x[i],y[i]])
            print(dic)
            table = pt.PrettyTable(['Rus', 'Eng'])
            table.align['Rus'] = 'l'
            table.align['Eng'] = 'r'

            for r,e in dic:
                table.add_row([r, e])

            context.bot.send_message(chat_id=ID,
                                     text=f'```{table}```')
            return ConversationHandler.END
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Нужно пройти регистрацию")
            return ConversationHandler.END

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        context.bot.send_message(chat_id=ID,
                                 text="Нужно пройти регистрацию")
        return ConversationHandler.END
    finally:
        if connection:
            cursor.close()
            # connection.close()
            print("[INFO] PostgreSQL connection closed")


# начало мохголомки

# удаляет работку с именем которое ему присвоено(id) current_jobs - кортеж запланированных работ
def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# def unset(update: Update, context: CallbackContext) -> None:
#     """Remove the job if the user changed their mind."""
#     reply_keyboard = [['/random_task', '/dictionary']]
#     markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
#     chat_id = update.message.chat_id
#     job_removed = remove_job_if_exists(str(update.effective_user.id), context)
#     text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
#     context.bot.send_message(chat_id=chat_id,
#                              text=text, reply_markup=markup_key)
#     return ConversationHandler.END


def timer_task(update, context: CallbackContext):
    print('pusk')
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        print('-------', context.bot_data[key])
    except KeyError:
        context.bot.send_message(chat_id=ID,
                                 text="Сначала нужно войти или зарегистрироваться")  # почему то не всплывапет сообщение введите пароль
        return ConversationHandler.END
    else:
        if 'after_login' in context.bot_data[key]:
            key_1 = str(update.effective_user.id) + ' timer_task'
            attempt_counter_key = str(update.effective_user.id) + 'attempt'
            context.bot_data[attempt_counter_key] = 0
            context.bot_data[key_1] = ID
            context.bot.send_message(chat_id=ID,
                                     text="Задание в пути\n"
                                          "Прибудет в 20:05 по московскому времени")
            context.job_queue.run_daily(time_for_task,
                                        datetime.time(hour=20, minute=46, tzinfo=pytz.timezone('Europe/Moscow')),
                                        days=(0, 1, 2, 3, 4, 5, 6), context=[ID, str(ID) + 'time'],
                                        name=str(update.effective_user.id))  # вызов функции с заданием
            # context.job_queue.run_repeating(time_for_task,interval=20,context=[ID, str(ID)+'time'], name=str(update.effective_user.id))
            # передаем в context данные необходимое той функции тк update по дефолту передать нельзя
            print('задание дощло')
        else:
            context.bot.send_message(chat_id=ID,
                                     text="иди регайся xuylo")
            return ConversationHandler.END


def time_for_task(context: CallbackContext):
    print('ну хоть сюда то попало')
    task = taskes()
    print(context.job.context[0])
    ID = context.job.context[0]
    job = context.job.context[1]
    context.bot.send_message(chat_id=ID, text=f'{task[0]} /time_for_task_answer ....')  # отправляем задание
    context.bot_data[job] = [task[2], True] # передаем функции посреднику ответ
    print(context.bot_data[job])
    print(task[2])


# обработчик ответа
def time_for_task_answer(update, context):
    key = str(update.effective_user.id)
    user_id = context.bot_data[key][0]  # id из базы данной
    reply_keyboard = [['/random_task', '/dictionary','/your_dictionary', '/exit']]
    messege_from_user = update.message.text  # сообщение от юзера
    answer = (messege_from_user.split('/time_for_task_answer')[1]).split()  # преобразуем сообщение в список
    print('answer: ', answer)
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id  # id чата в тг
    attempt_counter_key = str(update.effective_user.id) + 'attempt'
    print('attemp: ', context.bot_data[attempt_counter_key])
    key_1 = str(update.effective_user.id) + 'time'
    print('key_1', key_1)
    if 'after_login' in context.bot_data[key]:
        if True in context.bot_data[key_1]:
            try:
                task = 'unit39_1_Tick_the_words'  # задание юнит
                date = datetime.date.today()  # дата выполнения задания
                cursor = connection.cursor()  # отркываем соединение с базой данных
                right_answer = (context.bot_data[key_1][0]).split()  # правильный ответ
                print('ответ на задание', right_answer)
                context.bot_data[attempt_counter_key] += 1  # попытки выполнения задания
                result = {}  # словарь гду будут храниться ошибки
                errors = []  # список что бы записать все ошибки в бд
                result_ratio = ''  # строка по типу 4/5 - соотношение результата для записи в бд
                all_right = True  # будем передаывать для понимания правиильно ои выполнены все задания
                if len(right_answer) == len(answer):  # проверка на недостаток или избыток ответов
                    for i in range(len(right_answer)):
                        if right_answer[i] == answer[i]:
                            pass
                        else:
                            result[i + 1] = [answer[i], right_answer[
                                i]]  # добавляем элемент словарю тк отчет начинается с 0 а наши здания с 1
                    print(result)
                    print(context.bot_data[attempt_counter_key])
                    if len(result) == 0:  # если результат равен нулю соответственно ошибок нет
                        all_right = True
                        errors.append('нет ошибок')
                        result_ratio = f"{len(right_answer)}/{len(right_answer)}"
                        context.bot.send_message(chat_id=ID,
                                                 text="все правильно", reply_markup=markup_key)
                    else:  # смотрим какие ошибки в каком задании
                        all_right = False
                        context.bot.send_message(chat_id=ID,
                                                 text=f"осталось попыток {context.bot_data[attempt_counter_key]}/3")
                        if context.bot_data[attempt_counter_key] == 3:
                            count = 0  # счетчик ошибок
                            for i in result:  # проходимся по ошибкам помощенным  в словарь (вместе с правильными ответами на них)
                                context.bot.send_message(chat_id=ID,
                                                         text=f"в задании {i} оишбка"
                                                              f"- {result[i][0]}, правильно будет - {result[i][1]}")
                                # добавляем в еррорс ошибки что бы записать их в базу данных
                                errors.append(
                                    f"задние {str(i)}, оишбка {str(result[i][0])}, правильно {str(result[i][1])} ||| ")
                                count += 1
                            result_ratio = f"{len(right_answer) - count}/{len(right_answer)}"
                            context.bot.send_message(chat_id=ID,
                                                     text=f"результат: {result_ratio}", reply_markup=markup_key)
                    if context.bot_data[attempt_counter_key] >= 3 or all_right:
                        print('result', result_ratio)
                        print('task', task)
                        print('errors', ' '.join(errors))
                        print('attempts:', context.bot_data[attempt_counter_key])
                        print('date', date)
                        print('id', int(user_id))
                        print(user_id)
                        ### добавляю бд все данные о выполненом задании
                        cursor.execute(
                            """
                                    INSERT INTO time_random_task(result, task, errors, attemps, date_do_task, fk_random_task_user) VALUES
                                    (%s, %s, %s, %s, %s, %s);
                            """,
                            (result_ratio, task, ' '.join(errors), context.bot_data[attempt_counter_key], date,
                             int(user_id)))
                        print("[INFO] Data was succefully inserted")
                        context.bot_data[attempt_counter_key] = 0
                        context.bot_data[key_1][1] = False
                        return ConversationHandler.END
                else:
                    context.bot.send_message(chat_id=ID,
                                             text="слишком много или мало ответов))", reply_markup=markup_key)
                    if context.bot_data[attempt_counter_key] >= 3:
                        context.bot.send_message(chat_id=ID,
                                                 text="вы исчерпали 3 попытки переизбытком ответов")
                        cursor.execute(
                            """
                                    INSERT INTO time_random_task(result, task, errors, attemps, date_do_task, fk_random_task_user) VALUES
                                    (%s, %s, %s, %s, %s, %s);
                            """,
                            (result_ratio, task, ' '.join(errors), context.bot_data[attempt_counter_key], date,
                             int(user_id)))
                        print("[INFO] Data was succefully inserted")
                        context.bot_data[attempt_counter_key] = 0
                        context.bot_data[key_1][1] = False
                        return ConversationHandler.END

            except Exception as _ex:
                print("[INFO] Error while working with PostgreSQL", _ex)
                context.bot.send_message(chat_id=ID,
                                         text="все плохо")
            finally:
                if connection:
                    cursor.close()
                    # connection.close()
                    print("[INFO] PostgreSQL connection closed")
        # обработчик - если присылают ответ с упоминанием функции пока задание не было отправлено
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Задание еще не было отправлено")
            return ConversationHandler.END
    # обработчик - не зарегистрирован
    else:
        context.bot.send_message(chat_id=ID,
                                 text="Надо зарегистрироваться")
        return ConversationHandler.END

def exit(update, context):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        chat_id = update.message.chat_id
        job_removed = remove_job_if_exists(str(update.effective_user.id), context)
        text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
        print(text)
        print(context.bot_data)
        global black_list
        ind = black_list.index(key)
        black_list.pop(ind)
        print(black_list)
        del context.bot_data[key+' timer_task']
        del context.bot_data[key]
        try:
            del context.bot_data[key+'attempt']
        except Exception as _ex:
            print('here')
            pass

        try:
            del context.bot_data[key + 'step']
        except Exception as _ex:
            print('here')
            pass

        try:
            del context.bot_data[key + ' answer']
        except Exception as _ex:
            print('here')
            pass
        # context.bot_data[key+' timer_task'].clear()
        # context.bot_data[key].clear()
        print(context.bot_data)
        context.bot.send_message(chat_id=ID,
                                 text="Вы успешно вышли из аккаунта, надеюсь еще увидемся -)\n"
                                      "Если хотите снова войти нажмите сюда - /back")
        return ConversationHandler.END
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        context.bot.send_message(chat_id=ID,
                                 text="Нужно пройти регистрацию")
        return ConversationHandler.END




def help(update, context):
    ID = update.message.chat_id
    reply_keyboard = [['/random_task', '/dictionary', '/your_dictionary', '/exit']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=ID,
                             text="/registration ,/login и /back не получиться вызвать после входа в акканут\n"
                                  "/delete - удаление вашего аккаунта", reply_markup=markup_key)

def delete(update, context):
    ID = update.message.chat_id
    try:
        reply_keyboard = [['/Yes', '/No']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        key = str(update.effective_user.id)
        if 'after_login' in context.bot_data[key]:
            context.bot.send_message(chat_id=ID,
                                     text="Вы точно хотите удалить аккаунт?", reply_markup=markup_key)
            context.bot_data[key+'delete'] = True
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Войдите в аккаунт, чтобы удалить его")
            return ConversationHandler.END
    except Exception as _ex:
        context.bot.send_message(chat_id=ID,
                                 text="Войдите в аккаунт, чтобы удалить его")
        return ConversationHandler.END

def delete_Yes(update, context):
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        if context.bot_data[key+'delete']:





            context.bot.send_message(chat_id=ID,
                                     text="Если хотите снова войти нажмите сюда - /back")
            return ConversationHandler.END
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Как ты умудрился сюда попасть?")
            return ConversationHandler.END
    except Exception as _ex:
        context.bot.send_message(chat_id=ID,
                                 text="Войдите в аккаунт, чтобы удалить его")
        return ConversationHandler.END

def delete_No(update, context):
    reply_keyboard = [['/random_task', '/dictionary', '/your_dictionary', '/exit']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    ID = update.message.chat_id
    try:
        key = str(update.effective_user.id)
        if context.bot_data[key+'delete']:
            context.bot.send_message(chat_id=ID,
                                     text="Тогда посмотри чем ты можешь заняться", reply_markup=markup_key)
        else:
            context.bot.send_message(chat_id=ID,
                                     text="Как ты умудрился сюда попасть?")
            return ConversationHandler.END
    except Exception as _ex:
        context.bot.send_message(chat_id=ID,
                                 text="Войдите в аккаунт, чтобы удалить его")
        return ConversationHandler.END



# TODO: дописать time_task - заполнение в бд, поменять юд добавить колонку attemps

# TODO: написать ограничение на использование вызова команд после логина

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
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater("1533304329:AAHVhvmtXETWT4eDJrjzmbMn7Ac1XScSbwM")
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler`
    # с состояниями GENDER, PHOTO, LOCATION и BIO
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(CommandHandler("time_for_task_answer", time_for_task_answer, run_async=True))
    dispatcher.add_handler(CommandHandler('exit', exit, run_async=True))
    dispatcher.add_handler(CommandHandler('help', help, run_async=True))
    dispatcher.add_handler(CommandHandler('Yes', delete_Yes, run_async=True))
    dispatcher.add_handler(CommandHandler('No', delete_No, run_async=True))

    # dispatcher.add_handler(CommandHandler('delete', delete, run_async=True))
    # dispatcher.add_handler(CommandHandler("back", back))
    # dispatcher.add_handler(CommandHandler("login", login))
    conv_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('registration', registration, run_async=True),
                      CommandHandler("login", login, run_async=True)],
        # MessageHandler(Filters.text & Filters.regex & (~ Filters.command)
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            REGISTRATION_FIRST: [
                MessageHandler(Filters.text & (~ Filters.command), registration_first, run_async=True)],
            REGISTRATION_NICK_NAME: [
                MessageHandler(Filters.text & (~ Filters.command), registration_nick_name, run_async=True)],
            REGISTRATION_NAME: [MessageHandler(Filters.text & (~ Filters.command), registration_name, run_async=True)],
            REGISTRATION_SURNAME: [
                MessageHandler(Filters.text & (~ Filters.command), registration_surname, run_async=True)],
            REGISTRATION_PASSWORD: [
                MessageHandler(Filters.text & (~ Filters.command), registration_password, run_async=True)],
            LOGIN: [MessageHandler(Filters.text & (~ Filters.command), login, run_async=True)],
            LOGIN_DATA: [MessageHandler(Filters.text & (~ Filters.command), login_data, run_async=True)],
            # LOGIN_PASSWORD: [MessageHandler(Filters.text & (~ Filters.command), login_password,run_async=True)],
            # AFTER_LOGIN: [MessageHandler(Filters.text & (~ Filters.command), after_login)]

        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('back', back, run_async=True),
                   CommandHandler('step_back', step_back, run_async=True),
                   CommandHandler('delete', delete, run_async=True)]
    )

    conv_handler_2 = ConversationHandler(
        entry_points=[CommandHandler('random_task', random_task, run_async=True),
                      CommandHandler('dictionary', dictionary, run_async=True),
                      CommandHandler('your_dictionary', your_dictionary, run_async=True)
                      ],

        states={
            RANDOM_TASK_ANSWER: [
                MessageHandler(Filters.text & (~ Filters.command), random_task_answer, run_async=True)],
            DICTIONARY_WORD: [MessageHandler(Filters.text & (~ Filters.command), dictionary_word, run_async=True)]
        },
        fallbacks=[]

    )

    conv_handler_admin = ConversationHandler(
        entry_points=[CommandHandler('Administrator',administrator , run_async=True)
                      ],

        states={

        },
        fallbacks=[]

    )

    #  run_async=True
    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler,1)
    dispatcher.add_handler(conv_handler_2,2)
    dispatcher.add_handler(conv_handler_admin)

    # Запуск бота
    updater.start_polling()
    updater.idle()
