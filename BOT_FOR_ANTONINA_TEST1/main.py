
import psycopg2

't.me/EnglishAntonina_bot'
from config import host, user, password, db_name
password_usr = '1234_test_ogurec_2'
nick_name = 'Ogurec_test_2'
user_name = 'Nickita_test_2'
user_surname = 'Char_test_2'
try:
    # connect to exist database
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True

    # the cursor for perfoming database operations
    # cursor = connection.cursor()

    # delete a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """DROP TABLE users;"""
    #     )

    #     print("[INFO] Table was deleted")

    # create a new table
#     with connection.cursor() as cursor:
#         cursor.execute(
#             """
#                 CREATE TABLE  (
#                   id serial PRIMARY KEY,
#                   first_name varchar(50) NOT NULL,
#                   password text NOT NULL
# );"""
#         )
#
#         connection.commit()
#         print("[INFO] Table created successfully")




    # insert data into a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """INSERT INTO users (nick_name, user_name, user_surname, password) VALUES
    #             (%s, %s, %s, crypt(%s, gen_salt('bf', 8)));""",
    #         (nick_name, user_name, user_surname,password_usr))
    #     print("[INFO] Data was succefully inserted")

    # get data from a table
    # with connection.cursor() as cursor:
    #     # cursor.execute(
    #     #     """SELECT password FROM users WHERE password = crypt(%s, password);""",
    #     #     (password_usr,)
    #     # )
    #     cursor.execute(
    #         """SELECT id FROM taskes ;"""
    #
    #     )
    #
    #     print(cursor.fetchall())



    # delete a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """DROP TABLE time_random_task;"""
    #     )
    #
    #     print("[INFO] Table was deleted")

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        # cursor.close()
        connection.close()
        print("[INFO] PostgreSQL connection closed")







#     создание таблиц
# CREATE TABLE users
# (
#  	id serial PRIMARY KEY,
# 	nick_name varchar(64) NOT NULL UNIQUE,
# 	user_name varchar(64) NOT NULL,
# 	user_surname varchar(64) NOT NULL,
# 	password text NOT NULL
# );
#
# CREATE TABLE user_dictionary
# (
# 	id serial PRIMARY KEY,
# 	word varchar(64) NOT NULL,
# 	word_translate varchar(64) NOT NULL,
# 	fk_user_dictionary_users int REFERENCES users(id)
# );
#
# CREATE TABLE task
# (
# 	id serial PRIMARY KEY,
# 	template_of_task_1	varchar(255) NOT NULL,
# 	fk_task_usres int REFERENCES users(id)
# );


##########################################################
# CREATE TABLE random_task
# (
# 	id serial PRIMARY KEY,
# 	result varchar(30),
# 	task varchar(100) NOT NULL,
# 	errors varchar(255),
# 	date_do_task DATE,
# 	fk_random_task_user int REFERENCES users(id)
# );
#
# CREATE TABLE time_random_task
# (
# 	id serial PRIMARY KEY,
# 	result varchar(30),
# 	task varchar(100) NOT NULL,
# 	errors varchar(255),
# 	date_do_task DATE,
# 	fk_random_task_user int REFERENCES users(id)
# );
#
# CREATE TABLE taskes
# (
# 	task varchar(300),
# 	answer varchar(100),
# 	unit_name varchar(50)
# );
###############################################################