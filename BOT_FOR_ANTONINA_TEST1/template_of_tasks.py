import random
import psycopg2

't.me/EnglishAntonina_bot'
from config import host, user, password, db_name
global connection
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
connection.autocommit = True

def some_task():
    unit39_1_Tick_the_words = """
    
    Write the words which refer to people.
    For example: employee
    headquarters, branches, expert, bakery,
    accountant, quality, client, contacts, variety
    Пяснение: вводить слова без запятых через пробел
    
    """
    unit39_1_Tick_the_words_anwser = '1 2 3 4 5'

    unit39_2_Tick_the_words = """
    
    Choose the best word to complete the sentences.
    1 They’re experts in / on farming.
    2 When did you set up / take up tennis?
    3 Her law firm has many famous clients / customers.
    4 She’s actually my ex- / former wife; we got divorced last year.
    5 When did they set up / take up the company?
    6 The shop assistant was serving a client / customer.
    7 Marcel used to work here, but he’s currently / actually working abroad.
    8 Are they planning to take up / take over the company?
    9 George Bush is a former / an ex- president of America.
    Пяснение: вводить предлоги без запятых через пробел
    """
    unit39_2_Tick_the_words_answer = '5 4 3 2 1'
    lis = [[unit39_1_Tick_the_words, unit39_1_Tick_the_words_anwser], [unit39_2_Tick_the_words, unit39_2_Tick_the_words_answer]]
    return random.choice(lis)




def taskes():
    x = random.randint(1,2)
    cursor = connection.cursor()
    try:
            # cursor.execute(
            #     """SELECT password FROM users WHERE password = crypt(%s, password);""",
            #     (password_usr,)
            # )
        cursor.execute(
                """SELECT task, unit_name, answer FROM taskes WHERE id = (%s);""",
                (x,)

            )
        lis = (cursor.fetchone())
        task = (lis[0])
        unit = (lis[1])
        answer = (lis[2])
        return  task, unit, answer


    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL_taskes()", _ex)
    # finally:
    #     if connection:
    #         # cursor.close()
    #         connection.close()
    #         print("[INFO] PostgreSQL connection closed")

