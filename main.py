import pymysql
import telebot
import config
import asyncio
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from RegistrationService import Register
from parsing_specs import Parsing
from db import BotDB

BotDB = BotDB(config)

# try:
#     db = pymysql.connect(
#         host=config.host,
#         port=3306,
#         user=config.user,
#         password=config.password,
#         database=config.db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
# except Exception as ex:
#     print(ex)


# bot = telebot.AsyncTeleBot(config.telebot_key)
# db = BotDB(config)
bot = AsyncTeleBot(config.telebot_key)


async def keyboard_facults(userid):
    keyboard = types.InlineKeyboardMarkup()
    facults_datas = BotDB.get_facults()
    #print(facults_datas)

    for facult in facults_datas:
        # print(facult["facultName"],facult["facultId"])
        keyboard.add(types.InlineKeyboardButton(text=str(facult["facultName"]), callback_data=str(facult["id"])))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='back_to_itemskeyboard'))

    return keyboard


async def slct_items(userid):
    selected_items = BotDB.get_selected_items(userid)
    items_slct = []
    items_slct.append(selected_items[0]["item1"])
    items_slct.append(selected_items[0]["item2"])
    items_slct.append(selected_items[0]["item3"])
    items_slct.append(selected_items[0]["item4"])
    return items_slct

async def fclt_items(facultid):
    facult_items = BotDB.get_facultitems(facultid)
    items_fclt = []
    #print(facult_items)
    items_fclt.append(facult_items[0]["item1"])
    items_fclt.append(facult_items[0]["item2"])
    items_fclt.append(facult_items[0]["item3"])
    items_fclt.append(facult_items[0]["item4"])
    items_fclt.append(facult_items[0]["item5"])
async def keyboard_items(userid):
    keyboard = types.InlineKeyboardMarkup()
    items_select = await slct_items(userid)
    result = BotDB.get_school_items()
    for items in range(10):
        if result[items]["name"] in items_select:
            result[items]["name"] += "+"
    for i in range(12):
        if i % 2 == 0:
            # print(result[i]["name"],result[i+1]["name"])
            keyboard.add(types.InlineKeyboardButton(text=result[i]["name"], callback_data=result[i]["name"]),
                         types.InlineKeyboardButton(text=result[i + 1]["name"], callback_data=result[i + 1]["name"]))
            # keyboard.add(types.KeyboardButton(result[i]["name"]), types.KeyboardButton(result[i+1]["name"]))
        else:
            continue
    # keyboard.add(types.KeyboardButton(result[12]["name"]))
    # print(result[12]["name"])
    # keyboard.add(types.InlineKeyboardButton(text=result[12]["name"]), callback_data='готово')
    keyboard.add(types.InlineKeyboardButton(text=result[12]["name"], callback_data=result[12]["name"]))
    return keyboard


@bot.message_handler(commands=['start'])  # Обработчик команды старт
async def start(message):
    userid = message.from_user.id
    username = message.from_user.first_name
    # print('Регистрация нового пользователя')
    # print('Запускаю класс')
    Register(userid, username, BotDB)
    await bot.send_message(userid,
                           'Приветствую! Я смогу подобрать вам те специальности, на которые хватает баллов для поступления:)\nВ большенстве специальностей выбор идет на основе трёх предметов!')
    # msg_id = (await bot.send_message(user_id, 'Выберите предметы', reply_markup=keyboard_items())).message_id
    BotDB.update_userinline(userid, (
        await bot.send_message(userid, 'Выберите предметы', reply_markup=await keyboard_items(userid))).message_id)
    BotDB.change_user_process(userid, 'itemskeyboard')
    # await bot.send_message(user_id, 'Выберите предметы:', reply_markup=await keyboard_items())

    # with db.cursor() as cursor:
    #     select_all_rows = "SELECT * FROM userdatas WHERE userid =" + str(user_id)
    #     cursor.execute(select_all_rows)
    #     rows = cursor.fetchall()
    #     if cursor.rowcount == 0:
    #         print('Регистрация нового пользователя')
    #         try:
    #             with db.cursor() as cursor:
    #                 insert_query = "INSERT INTO userdatas (userid, username, process) VALUES (%s,%s,%s)"
    #                 data = (user_id,message.from_user.first_name,'Registration')
    #                 cursor.execute(insert_query, data)
    #                 db.commit()
    #                 insert_query = "INSERT INTO itemdatas (amount,userid) VALUES ('0', " + str(user_id) + ")"
    #                 cursor.execute(insert_query)
    #                 db.commit()
    #         except Exception as ex:
    #             print(ex)
    #         bot.send_message(user_id, 'Приветствую! Я смогу подобрать вам те специальности, на которые хватает баллов для поступления:)\nВ большенстве специальностей выбор идет на основе трёх предметов!')
    #         bot.send_message(user_id, 'Выберите предметы:')


@bot.message_handler(func=lambda message: True)  # Обработка входящих сообщений
async def echo_message(message):
    userid = message.from_user.id
    user_process = BotDB.get_userprocess(userid)
    # user_count_items = BotDB.get_usercountitems(userid)
    # user_inline_id = BotDB.get_inline_id(userid)
    if message.text == 'Парсинг':
        Parsing(BotDB)
    if user_process == 'entercount' and (message.text).isdigit():
        count_balls = message.text
        BotDB.set_usercountballs(userid, int(count_balls))
        BotDB.update_itemdatas_messageballs(userid, '1')
        BotDB.change_user_process(userid, 'selectfacult')
        BotDB.update_userinline(userid, (await bot.send_message(userid, 'Выберите факультет:',
                                                                reply_markup=await keyboard_facults(
                                                                    userid))).message_id)
    # if user_process == 'itemskeyboard' and user_inline_id != 0:
    #     if user_count_items <= 5:
    #         number_item = -1
    #         dictionary_items = BotDB.get_school_items()
    #         for items in dictionary_items:
    #             number_item += 1
    #             if items["name"] == message.text:
    #                 break
    #         if 0 <= number_item <= 9 and user_count_items < 5:
    #             for items in range(10):
    #                 if dictionary_items[items]["name"] == message.text:
    #                     BotDB.update_useritems(userid, message.text)
    #                     await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
    #                     break
    #         elif 0 <= number_item <= 9 and user_count_items == 5:
    #             await bot.send_message(userid, 'Выбрано максимальное количество предметов. Нажмите "готово"')
    #             await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
    #         elif 10 <= number_item <= 12:
    #             action = dictionary_items[number_item]["name"]
    #             if action == 'сбросить':
    #                 print('Сбросил')
    #                 BotDB.clear_items(userid)
    #                 try:
    #                     await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
    #                 except Exception as Ex:
    #                     print(f'Не удалось поменять клавиатуру пользователя {userid} , скорее всего ничего не изменилось')
    #             elif action == 'готово':
    #                 try:
    #                     await bot.delete_message(userid, user_inline_id)
    #                     BotDB.set_inline_id(userid, 0)
    #                 except Exception as Ex:
    #                     print(f'Не удалось удалить клавиатуру пользователя {userid}')
    #                     BotDB.set_inline_id(userid, 0)
    #                 await bot.send_message(userid, 'Введите суммарное количество баллов')
    #                 BotDB.change_user_process(userid, 'entercount')
    #                 #BotDB.update_userinline(userid, (await bot.send_message(userid, 'Выберите предметы', reply_markup= await keyboard_facults(userid))).message_id)
    #             elif action == 'отмена':
    #                 try:
    #                     await bot.delete_message(userid, user_inline_id)
    #                     BotDB.set_inline_id(userid, 0)
    #                 except Exception as Ex:
    #                     print(f'Не удалось удалить клавиатуру пользователя {userid}')
    #                     BotDB.set_inline_id(userid, 0)
    #                 BotDB.clear_user(userid)
    #                 print('he')
    # action = ''
    # for items in range(10, 13):
    #     if dictionary_items[items]["name"] == message.text:
    #         action = message.text
    #         break
    # if user_count_items < 5:
    #     flag = False
    #     k = 0
    #     for items in dictionary_items:
    #         if items["name"] == message.text:
    #             flag = True
    #             break
    # if flag or (user_count_items == 5):
    #     is_item = False
    #     for items in range(10):
    #         if dictionary_items[items]["name"] == message.text:
    #             BotDB.update_useritems(userid, message.text)
    #             is_item = True
    #             break
    #     if not is_item:
    #         action = ''
    #         for items in range(10, 13):
    #             if dictionary_items[items]["name"] == message.text:
    #                 action = message.text
    #                 break
    #         if action == 'сбросить':
    #             print('Сбросил')
    #             BotDB.clear_items(userid)
    #         elif action == 'готово':
    #             print('he')
    #         elif action == 'отмена':
    #             print('he')

    # elif (user_process == 'itemskeyboard') and (user_count_items == 5) and message.text != 'сбросить' and message.text != 'отмена' and message.text != 'готово' :
    #     await bot.send_message(userid, 'Выбрано максимальное количество предметов!\n "Нажмите готово"')

    # print(dictionary_items)
    # #print(message.text in dictionary_items["name"])
    # if message.text in dictionary_items:
    #     print('это предмет')

    # if (message.text == 'Кла'):
    #   bot.send_message(user_id, "Выберите предметы: ", reply_markup=keyboard_items())


@bot.callback_query_handler(func=lambda call: True)
async def callback_worker(call):
    userid = call.from_user.id
    user_process = BotDB.get_userprocess(userid)
    user_inline_id = BotDB.get_inline_id(userid)
    # print(call.data)
    if user_process == 'itemskeyboard':
        if call.data == 'сбросить':
            print('Сбросил')
            BotDB.clear_items(userid)
            try:
                await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
            except Exception as Ex:
                print(f'Не удалось поменять клавиатуру пользователя {userid} , скорее всего ничего не изменилось')
        elif call.data == 'отмена':
            try:
                await bot.delete_message(userid, user_inline_id)
                BotDB.set_inline_id(userid, 0)
            except Exception as Ex:
                print(f'Не удалось удалить клавиатуру пользователя {userid}')
                BotDB.set_inline_id(userid, 0)
            BotDB.clear_user(userid)
        elif call.data == 'готово':
            try:
                await bot.delete_message(userid, user_inline_id)
                BotDB.set_inline_id(userid, 0)
            except Exception as Ex:
                print(f'Не удалось удалить клавиатуру пользователя {userid}')
                BotDB.set_inline_id(userid, 0)
            await bot.send_message(userid, 'Введите суммарное количество баллов: ')
            BotDB.change_user_process(userid, 'entercount')
            # BotDB.update_userinline(userid, (await bot.send_message(userid, 'Выберите предметы',reply_markup=await keyboard_facults(userid))).message_id)
        else:
            user_count_items = BotDB.get_usercountitems(userid)
            if user_count_items < 5:
                # selected_items = await slct_items(userid)
                # print(selected_items)
                # print(call.data)
                # print('+' not in call.data)
                if ('+' not in call.data):
                    BotDB.update_useritems(userid, call.data)
                    try:
                        await bot.edit_message_reply_markup(userid, user_inline_id,
                                                            reply_markup=await keyboard_items(userid))
                    except Exception as Ex:
                        print('Не удалось изменить клавиатуру')
                        await BotDB.update_userinline(userid, await bot.send_message(userid, 'Выберите предметы:',
                                                                                     reply_markup=await(keyboard_items(
                                                                                         userid))).message_id)
            else:
                await bot.send_message(userid, 'Выбрано максимальное количество предметов. Нажмите "готово"')
    elif user_process == 'selectfacult' and bool(BotDB.get_itemdatas_messageballs(userid)):
        #print(call.data)
        if call.data == 'back_to_itemskeyboard':
            try:
                BotDB.change_user_process(userid, 'itemskeyboard')
                BotDB.update_itemdatas_messageballs(userid, '0')
                await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
            except Exception as ex:
                print(f'Не удалось обновить клавиатуру у пользователя {userid}, выслана новая')
                await BotDB.update_userinline(userid, await bot.send_message(userid, 'Выберите предметы:', reply_markup=await(keyboard_items(userid))).message_id)
        else:
            chet = BotDB.get_facultitems(call.data)
            items = await slct_items(userid)
            count_balls = BotDB.get_usercountballs(userid)
            print(count_balls)
            if (chet[0]["item1"] in items) and (chet[0]["item2"] in items) and ( (chet[0]["item3"] in items) or (chet[0]["item4"] in items) or (chet[0]["item5"] in items)):
                ans_msg = ''
                directions = BotDB.get_facults_itog(call.data)
                for direction in directions:
                   # print(int(direction["specballs"][:3]))
                    if (len(str(direction["specballs"])) < 2):
                        ans_msg += direction["specname"] + "\n" + "Новое направление" + "\n" + "Бюджетных мест: " + direction["specountbudgetplace"] + "\n\n"
                    elif count_balls >= int(direction["specballs"][:3]):
                        ans_msg += direction["specname"] + "\n" + "Проходной балл: " + direction["specballs"] + "\n" + "Бюджетных мест: " + direction["specountbudgetplace"] + "\n\n"
                if ans_msg == '':
                    await bot.send_message(userid, 'Ваших баллов недостаточно чтоб поступить на данный факультет:(')
                else:
                    await bot.send_message(userid, ans_msg)
            else:
                await bot.send_message(userid, 'С вашим набором предметов поступить на данный факультет невозможно')

            # for imer in chet:
            #     print(imer["facultid"], imer["item1"], imer["item2"], imer["item3"], imer["item4"], imer["item5"])
                # await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
                # number_item = -1
                # dictionary_items = BotDB.get_school_items()
                # for items in dictionary_items:
                #     number_item += 1
                #     if items["name"] == call.text:
                #         break
                # if 0 <= number_item <= 9 and user_count_items < 5:
                #     for items in range(10):
                #         if dictionary_items[items]["name"] == call.text:
                #             BotDB.update_useritems(userid, call.text)
                #             await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
                #             break
                # elif 0 <= number_item <= 9 and user_count_items == 5:
                #     await bot.send_message(userid, 'Выбрано максимальное количество предметов. Нажмите "готово"')
                #     await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
            # elif 10 <= number_item <= 12:
            #     action = dictionary_items[number_item]["name"]
            #     if action == 'сбросить':
            #         print('Сбросил')
            #         BotDB.clear_items(userid)
            #         try:
            #             await bot.edit_message_reply_markup(userid, user_inline_id, reply_markup=await keyboard_items(userid))
            #         except Exception as Ex:
            #             print(f'Не удалось поменять клавиатуру пользователя {userid} , скорее всего ничего не изменилось')
            #     elif action == 'готово':
            #         try:
            #             await bot.delete_message(userid, user_inline_id)
            #             BotDB.set_inline_id(userid, 0)
            #         except Exception as Ex:
            #             print(f'Не удалось удалить клавиатуру пользователя {userid}')
            #             BotDB.set_inline_id(userid, 0)
            #         BotDB.update_userinline(userid, (await bot.send_message(userid, 'Выберите предметы', reply_markup= await keyboard_facults(userid))).message_id)
            #     elif action == 'отмена':
            #         try:
            #             await bot.delete_message(userid, user_inline_id)
            #             BotDB.set_inline_id(userid, 0)
            #         except Exception as Ex:
            #             print(f'Не удалось удалить клавиатуру пользователя {userid}')
            #             BotDB.set_inline_id(userid, 0)
            #         BotDB.clear_items(userid)
            #         BotDB.change_user_process(userid, 'Отмена')
            #         print('he')



asyncio.run(bot.polling())
