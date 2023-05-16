from db import BotDB
class Register:
    def __init__(self, user_id, username, db):
        if BotDB.user_exists(db, user_id):
            BotDB.clear_user(db, user_id)
        else:
            BotDB.add_user(db, user_id, username)
