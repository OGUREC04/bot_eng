def login_password(update, context: CallbackContext):
    reply_keyboard = [['/back']]
    print(password_from_login_nick_name)
    ID = update.message.chat_id
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    user_password = update.message.text
    try:
        reply_keyboard = [['/back']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        ### извлекаю все данные из таблицы и смотрю есть ли в нем такой никнейм
        cursor = connection.cursor()
        cursor.execute("""
        SELECT  * FROM users;
        """)
        list_of_user_info = list(cursor.fetchall()[0])
        users_info = {}
        for i in range(5):
            users_info[f'{for_dict[i]}'] = f'{list_of_user_info[i]}'
        print(users_info)
        cursor.execute("""
        SELECT nick_name
        FROM users
        WHERE id = %s and  password = crypt(%s, password);
        """, (int(users_info['ID']),int(users_info['ID']) ))
        user_password_from_bd_id = (cursor.fetchone()[0])

        ###
        if user_password in users_info:
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