from db import BotDB
class Register:

    def __init__(self, user_id, username, db):
        #print('Класс регистрации', user_id)
        if BotDB.user_exists(db, user_id):
            #print('Пользователь имеется в системе')
            BotDB.clear_user(db, user_id)
        else:
            BotDB.add_user(db, user_id, username)
            #print('Пользователь зарегистрирован в системе')
    # def registration(self, user_id, username):
    #     print('Класс регистрации', user_id)
    #     if BotDB.user_exists(user_id):
    #         print('Пользователь имеется в системе')
    #     else:
    #         BotDB.add_user(user_id, username)
    #         print('Пользователь зарегистрирован в системе')
    #     with db.cursor() as cursor:
    #         select_all_rows = "SELECT * FROM userdatas WHERE userid =" + str(user_id)
    #         cursor.execute(select_all_rows)
    #         rows = cursor.fetchall()
    #         if cursor.rowcount == 0:
    #             print('Регистрация нового пользователя')
    #             try:
    #                 with db.cursor() as cursor:
    #                     insert_query = "INSERT INTO userdatas (userid, username, process) VALUES (%s,%s,%s)"
    #                     data = (user_id, message.from_user.first_name, 'Registration')
    #                     cursor.execute(insert_query, data)
    #                     db.commit()
    #                     insert_query = "INSERT INTO itemdatas (amount,userid) VALUES ('0', " + str(user_id) + ")"
    #                     cursor.execute(insert_query)
    #                     db.commit()
    #                     return True
    #             except Exception as ex:
    #                 return ex
    #         return False