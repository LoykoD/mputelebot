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

bot = AsyncTeleBot(config.telebot_key)


async def keyboard_facults(userid):
    keyboard = types.InlineKeyboardMarkup()
    facults_datas = BotDB.get_facults()

    for facult in facults_datas:
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
            keyboard.add(types.InlineKeyboardButton(text=result[i]["name"], callback_data=result[i]["name"]),
                         types.InlineKeyboardButton(text=result[i + 1]["name"], callback_data=result[i + 1]["name"]))
        else:
            continue
    keyboard.add(types.InlineKeyboardButton(text=result[12]["name"], callback_data=result[12]["name"]))
    return keyboard


@bot.message_handler(commands=['start'])  # Обработчик команды старт
async def start(message):
    userid = message.from_user.id
    username = message.from_user.first_name
    Register(userid, username, BotDB)
    await bot.send_message(userid,
                           'Приветствую! Я смогу подобрать вам те специальности, на которые хватает баллов для поступления:)\nВ большенстве специальностей выбор идет на основе трёх предметов!')
    BotDB.update_userinline(userid, (
        await bot.send_message(userid, 'Выберите предметы', reply_markup=await keyboard_items(userid))).message_id)
    BotDB.change_user_process(userid, 'itemskeyboard')

@bot.message_handler(func=lambda message: True)  # Обработка входящих сообщений
async def echo_message(message):
    userid = message.from_user.id
    user_process = BotDB.get_userprocess(userid)
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
 


@bot.callback_query_handler(func=lambda call: True)
async def callback_worker(call):
    userid = call.from_user.id
    user_process = BotDB.get_userprocess(userid)
    user_inline_id = BotDB.get_inline_id(userid)
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
        else:
            user_count_items = BotDB.get_usercountitems(userid)
            if user_count_items < 5:
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



asyncio.run(bot.polling())
