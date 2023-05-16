import pymysql

class BotDB:

    def __init__(self, config):
        self.db = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def user_exists(self, user_id):  #Есть ли юзер в бд
        select_all_rows = "SELECT * FROM userdatas WHERE userid =" + str(user_id)
        result = self.cursor.execute(select_all_rows)
        #print(result)
        return bool(result)
    def add_user(self, user_id, username):
        insert_query = "INSERT INTO userdatas (userid, username, process) VALUES (%s,%s,%s)"
        data = (user_id, username, 'Registration')
        self.cursor.execute(insert_query, data)
        #self.db.commit()
        insert_query = "INSERT INTO itemdatas (amount,userid) VALUES ('1', " + str(user_id) + ")"
        self.cursor.execute(insert_query)
        #self.db.commit()
        return self.db.commit()

    def change_user_process(self, userid, process):
        update_query = "UPDATE userdatas SET process = '" + str(process) + "' WHERE userid =" + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def update_userinline(self, userid, idmessage):
        update_query = "UPDATE userdatas SET idmessage_inline = '" + str(idmessage) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def get_userprocess(self, userid):
        select_query = "SELECT process from userdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["process"]
    def get_school_items(self):
        select_query = "SELECT name FROM schoolitemsdata"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
        #result = self.cursor.fetchall()

    def update_useritems(self, userid, item_name):
        amount = self.get_usercountitems(userid)
        update_query = "UPDATE itemdatas SET item" + str(amount) + " = '" + str(item_name) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        update_query = "UPDATE itemdatas SET amount = '" + str(int(amount+1)) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def clear_items(self, userid):
        update_query = "UPDATE itemdatas SET amount = '1', item1 = '', item2 = '', item3 = '', item4 = '', message_balls = '0' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def get_selected_items(self, userid):
        select_query = "SELECT item1,item2,item3,item4 FROM itemdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
    def get_usercountitems(self, userid):
        select_query = "SELECT amount FROM itemdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["amount"]

    def get_inline_id(self, userid):
        select_query = "SELECT idmessage_inline FROM userdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["idmessage_inline"]

    def set_inline_id(self, userid, inlineid):
        update_query = "UPDATE userdatas SET idmessage_inline = '" + str(inlineid) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def set_usercountballs(self,userid, count_balls):
        update_query = "UPDATE userdatas SET count_balls = '" + str(count_balls) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def get_usercountballs(self, userid):
        select_query = "SELECT count_balls FROM userdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["count_balls"]
    def clear_user(self, userid):
        self.clear_items(userid)
        self.change_user_process(userid, 'itemskeyboard')
        self.set_inline_id(userid, 0)
        self.set_usercountballs(userid, 0)
        self.update_itemdatas_messageballs(userid, '0')

    def get_facults(self):
        select_query = "SELECT id, facultName FROM facultdatas"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def update_itemdatas_messageballs(self, userid, cnt_balls):
        update_query = "UPDATE itemdatas SET message_balls = '" + str(cnt_balls) + "' WHERE userid = " + str(userid)
        self.cursor.execute(update_query)
        self.db.commit()

    def get_itemdatas_messageballs(self, userid):
        select_query = "SELECT message_balls FROM itemdatas WHERE userid = " + str(userid)
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["message_balls"]

    def get_facultitems(self, faculid):
        select_query = "SELECT facultid, item1, item2, item3, item4, item5 FROM podfacults WHERE facultid = "+str(faculid)
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def get_facultid(self, facultname):
        select_query = "SELECT id FROM facultdatas WHERE facultName = '" +str(facultname)+ "'"
        self.cursor.execute(select_query)
        return self.cursor.fetchone()["id"]

    def add_specdata(self,facultname, specname, specballs, speccountbudget):

        facultid = self.get_facultid(facultname)
        print(facultid)
        insert_query = "INSERT into specsdatas (facultsid, facultname, specname, specballs, specountbudgetplace) VALUES (%s, %s, %s, %s, %s)"
        data = (facultid, facultname, specname, specballs, speccountbudget)
        self.cursor.execute(insert_query, data)
        self.db.commit()

    def add_facults(self, facultname):
        select_query = "SELECT * FROM facultdatas WHERE facultName = '" + str(facultname) + "'"
        result = self.cursor.execute(select_query)
        if not(bool(result)):
            insert_query = "INSERT into facultdatas (facultName) VALUES ('" + str(facultname) +"')"
            self.cursor.execute(insert_query)
            self.db.commit()
        #print(result)
        #return bool(result)

    def get_facults_itog(self, facultid):
        select_query = "SELECT facultname, specname, specballs, specountbudgetplace FROM specsdatas WHERE facultsid = '" + str(facultid) + "'"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def close(self):
        self.connect.close()
