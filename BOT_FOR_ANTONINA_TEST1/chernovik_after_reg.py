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


answer = [1,2,3,4,5,6]

def random_task(update, context: CallbackContext):
    ID = update.message.chat_id
    context.bot.send_message(chat_id=ID,
                             text=
                                '''
                                Complete the sentences.
                                1 She’s got straight hair .
                                2 Isabella is very good- .....
                                3 Beata’s got blonde .....
                                4 Her brother’s got very broad .....
                                5 That’s a nice suit: Jack’s very ......today.
                                6 I would say he was medium ......
                                7 Charlotte’s hair is fair but her brother’s is quite....... 
                            Введите ответы через пробел в одном сообщении
                                 '''
                             )
    print(update.message.text)
    # answer = list(((update.message.text).lower()).split(''))
    if answer == [1,2,3,4,5,6]:
        context.bot.send_message(chat_id=ID, text="Вы успешно завершили задание")



