################################################# 
# Кагуя-бот
# version хуй знает
# by Timka & Ganka
# license: да мне пох
#################################################
# девиз проекта: 
# работает - не трогай, не работает - похуй
#################################################

# база
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import telegram, telegram.ext

# для погоды
from pyowm import OWM
from pyowm.utils import config as cfg

# для привода слов к стандартной форме
import pymorphy2

# для чтения расписания
import xlrd

# для рандомного выбирания картинок и ответов
from random import choice
import random
from glob import glob

# для того, чтобы Кагуя рассказала, что сегодня
from datetime import date
import datetime
import time

# для записи юзеров в файлик
import json
import io

# секретная функция для админов
import os

WORDS = dict()    # словарь с эмоциональными окрасками
HOLIDAYS = dict() # праздники на каждый день
USERS = dict()    # пользователи

#############################
# Псевдо ИИ

HELP_TEXT = """
Привет, меня зовут Кагуя!
Можешь потыкать на кнопки или написать мне обычное сообщение, я отвечу.
Если у тебя не отображаются какие-то функции, пропиши ещё раз /start.

Основные команды:
/stat - статистика по использованию бота
/set_group [группа] - установить свою группу (для студентов МИРЭА)
/set_wakeup_time [время] - установить время подъёма к первой паре
/disable_groups - отключить подсказки об указании своей группы

Остальные функции ты найдёшь на нижней панели после прописывания команды /start.
Если у тебя возникли какие-либо вопросы по использованию бота, пиши @laxzzz :)
"""

POSITIVE_QUESTION_ANSWERS = ['Да, сенпай!', 'Да)', 'Ага', 'Согласна))', 'Так точно!', 'Может быть)', 'Проверь и узнаешь)', 'Скорее да',
                             'Нет, сенпай', 'Нет!', 'Неа', 'Не-не-не', 'Я стесняюсь отвечать на такие вопросы//', 'Нет, ты что)']
NEGATIVE_QUIESTION_ANSWERS = ['Да и что', 'Ну да.', 'Ага.', 'Чел...', 'Нет', 'Сходи нахуй', 'Еблан...', 
                              'Как такое вообще могло прийти тебе в голову??', 'Ты поехавший ублюдок...', 'Ашалеть']
POSITIVE_REPLIES = ['Ты такой милашка', 'Desu-desu :3', 'Буду твоей вайфу)', 'Так', 'А что было дальше?', 'Мм', 'Интересно', 'Здорово!', 'Класс',
                    'Капец ты няшный <3', 'Мур)', 'Приятненько)', 'Ничего себе...', 'Вот и отлично', 'Прекрасно', 'Круто)', 'Блин, так бы и слушала тебя целыми днями))',
                    'А с тобой очень приятно общаться)', 'А можешь еще что-нибудь рассказать', 'Ня)']
NEGATIVE_REPLIES = ['Чеел', 'Иди нахуй', 'Эмм', 'Лол', 'Не пиши сюда больше, ебло', 'Ты подзалупное чудовище, как тебя вообще мать родила на свет', 
                    'Просто пиздец...', 'Ну ты и еблан', 'Бака!!!', 'Дурачье', 'Пипец', 'Совсем афигевший?', 'Делбич ты(', 'Обидно', 'Сам придумал, или мама подсказала',
                    'Да? А я вчера могилу твоей матери навещала', 'Эммм, тебя не научили общаться нормально?', 'Ну ты и ебло ебаное)',
                    'Про таких как ты говорят: мама не хотела, папа не старался']

NEGATIVE_WHOAMI_REPLIES = ['долбаеб', 'сын шалавы ебаной', 'уебан сраный', 'гандон штопаный', 'ублюдок недоебаный', 'блядский мудак',
                           'пидорас', 'уёбак', 'конченный хуесос', 'дифичент ебаный', 'хуепутало']
POSITIVE_WHOAMI_REPLIES = ['норм чел', 'котик', 'милаха', 'няша', 'классный', 'приятный', 'хороший', 'крутой' , 'классный', 'офигенный']

BYE = ['споки', 'спокойной ночи', 'а ну спать', 'до завтра', 'пока', 'сладких снов']
HI = ['привет', 'ку', 'здарова', 'доброе утро']

GOOD_MORNING = ['Привет!', 'Доброе утро! Я вот только проснулась)', 'Ку :3', 'Как настроение?', 'Охае', 'Шалом))0)', 'Э, салам алейкум, брат', 'Выспался?',
            'Приветик)', 'Надеюсь, ты хорошо поспал', 'Утречко)']
GOOD_DAY = ['Привет!', 'Добрый день!', 'Ку :3', 'Как настроение?', 'Охае', 'Шалом))0)', 'Э, салам алейкум, брат', 'Приветик)']
GOOD_EVENING = ['Привет!', 'Добрый вечер!', 'Ку :3', 'Как настроение?', 'Охае', 'Шалом))0)', 'Э, салам алейкум, брат', 'Приветик)']

HAVE_A_GOOD_NIGHT = ['Споки)', 'Спокойной ночи <3', 'Сладких снов)', 'Буду ждать твоего сообщения завтра утром)', 'Споки ноки', 'Я тоже иду спать. До завтра',
              'Выспись хорошо. И не проспи будильник))']
HAVE_A_GOOD_DAY = ['Покич', 'Хорошего дня)', 'Удачи тебе)', 'Буду ждать твоего сообщения)', 'Я буду скучать(', 'Удачи тебе сегодня']

WHATSUP_QUESTIONS = ['как дела?', 'как настроение?', 'как жизнь?', 'как твои дела?', 'что нового?', 'как ты?']
POSITIVE_WAHATSUP_ANSWERS = ['У меня все хорошо. А у тебя как настроение?)', 'Нормально. А у тебя как настроение?)', 'Все ок. А у тебя как настроение?)',
                             'Все отлично. А у тебя как настроение?)']
NEGATIVE_WAHATSUP_ANSWERS = ['Отвратительно', 'Ужасно(', 'Плоха, ты бака(', 'Не твое дело!']

APPEALS = ['кагуя', 'слушай', 'эй бейба', 'девка']
POSITIVE_APPEALS_ANSWERS = ['Да', 'А', 'Слушаю тебя, сенпай', 'Слушаю)', 'Что такое?']
NEGATIVE_APPEALS_ANSWERS = ['Чего тебе', 'Да.', 'С мамой своей поговори, а меня не трогай', 'Чего тебе, ебло?', 'Иди нахуй сразу', 'В мут с нулевой']

WHY = ['почему', 'зачем', 'схуяли']
POSITIVE_WHY_ANSWERS = ['Потому что)', 'Звёзды так сошлись', 'Потому что у меня такая классная жопа', 'Сенат США так решил', 'Ну прост', 'А почему бы и нет)']
NEGATIVE_WHY_ANSWERS = ['Потому что иди нахуй', 'Тя ебать не должно', 'Это инфа не для тебя', 'Потому что.']

MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

OR_ANSWERS = ['Ну разумеется', 'Конечно же', 'Я думаю', 'Мне кажется', 'Я выбираю', 'Мне больше нравится']

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

PAIRS_TIME = {
    1 : {'start': datetime.time(9,  0),  'end' : datetime.time(10, 30)},
    2 : {'start': datetime.time(10, 40), 'end' : datetime.time(12, 10)},
    3 : {'start': datetime.time(12, 40), 'end' : datetime.time(14, 10)},
    4 : {'start': datetime.time(14, 20), 'end' : datetime.time(15, 50)},
    5 : {'start': datetime.time(16, 20), 'end' : datetime.time(17, 50)},
    6 : {'start': datetime.time(18, 0),  'end' : datetime.time(19, 30)}
}

#############################
# ЧАСТЬ СО СЛУЖЕБНЫМ ГОВНОМ

ADMINS_ID = ['441875037', '635725092'] # админы - Тимка и Ганька
QUIT_TEXT = 'Вырубайся нахуй'

MOOD_FADING = 0.6816901138162094 # коэффициент затухания настроения
MESSAGE_RATING_FADING = 0.6 # коэффициент затухания рейтинга сообщения
REPLY_WITH_USR_MSG = 0.35 # вероятность ответа сообщением пользователя (из top_messages)
TOP_MESSAGES_SIZE = 500 # количество сообщений в топе
MAX_RATING_POS_MSGS_SIZE = 20
MAX_RATING_NEG_MSGS_SIZE = 20
DEFAULT_RATING = 100 # рейтинг сообщения по умолчанию
CRITICAL_LAST_USAGE_TIME = 1209600 # (в секундах) две недели
CRITICAL_LAST_TIMETABLE_UPDATE_TIME = 43200 # (в секундах) 12 часов
SLEEP_TIME = 0.6 # задержка в отправке сообщений, шобы на человека было похоже (в секундах)
DEFAULT_DATE_FORMAT = "%y.%m.%d"
NIGHT_LIMIT = 5 # текущее число считается "завтра" до 5 утра

MORNING_START = 6  #
DAY_START = 12     # начало дня, вечера и ночи
EVENING_START = 20 # (в часах)
NIGHT_START = 22   # от этого заисит, что скажет Кагуя на приветствие и прощание

MORPH = pymorphy2.MorphAnalyzer()
CONTROL_MSGS = dict() # контрольное сообщение, на которое можно ответить, если юзер нихуя не написал
                      # по-хорошему нужно исправить, так как это лютый костыль

def log(msg):
    #print('-------------------------')
    #print('MESSAGE: ', msg.text)
    #print('USER: ', msg.from_user['first_name'])
    #print('MOOD: ', USERS[get_id_bymsg(msg)]['mood'])
    #print('-------------------------')
    return

def read_words():
    f = io.open('words.txt', mode='r', encoding='utf-8')
    for line in f:
        tmp = line.split()
        if tmp[1] != '0' and tmp[0] not in WORDS:
            WORDS[tmp[0]] = int(tmp[1])
    f.close()

def read_holidays():
    f = io.open('holidays.txt', mode='r', encoding='utf-8')
    for line in f:
        tmp = line.split()
        holiday = ''
        for i in range(3, len(tmp)):
            holiday += tmp[i] + ' '
        HOLIDAYS[tmp[0] + ' ' + tmp[1]] = holiday
    f.close()

def read_users():
    global USERS
    try:
        f = io.open('users.json', mode='r', encoding='utf-8')
        USERS = json.loads(f.read())
        f.close()
        for usr_id in USERS:
            if 'pair_skips' not in USERS[usr_id]:
                USERS[usr_id]['pair_skips'] = []
        #    if 'max_rating_pos_msgs' not in USERS[id]:
        #        USERS[id]['max_rating_pos_msgs'] = []
        #    if 'max_rating_neg_msgs' not in USERS[id]:
        #        USERS[id]['max_rating_neg_msgs'] = []
        #    if 'top_messages' not in USERS[id]:
        #        USERS[id]['top_messages'] = dict()
        #    if 'waiting_for_random' not in USERS[id]:
        #        USERS[id]['waiting_for_random'] = False
        #    if 'rand_max' not in USERS[id]:
        #        USERS[id]['rand_max'] = 0
        #    if 'last_usage' not in USERS[id]:
        #        USERS[id]['last_usage'] = 0.0
    except Exception:
        f = io.open('users.json', mode='w', encoding='utf-8')
        f.write('{}')
        f.close()
        USERS = dict()
    #print(USERS)

def write_users():
    f = io.open('users.json', mode='w', encoding='utf-8')
    json_string = json.dumps(USERS)
    f.write(json_string)
    f.close()

def register_user(msg): # пажилая регистрация...
    global USERS
    id = str(msg.from_user['id'])
    first_name = msg.from_user['first_name']
    last_name = msg.from_user['last_name']
    username = msg.from_user['username']
    USERS[id] = {
        'first_name' : first_name,
        'last_name' : last_name,
        'username' : username,
        'mood' : 0,
        'city' : '',
        'rand_max': 0,
        'waiting_for_city' : False,
        'waiting_for_random' : False,
        'msg_count' : 0,
        'pics_unlocked' : 0,
        'pics' : [False] * len(glob('LEGS/*')),
        'max_rating_pos_msgs': [],
        'max_rating_neg_msgs': [],
        'top_messages' : dict(), # топ сообщений челика
        'last_usage' : time.time(), # время последнего использования
        'group': '',
        'last_timetable_update' : None,
        'timetable': dict(), 
        'base_get_up_time_hour' : None,
        'base_get_up_time_minute': None,
        'waiting_for_get_up_time' : False,
        'show_set_group_notice' : True,
        'pair_skips' : []
    }

def check_registration(bot):
    usr_id = get_id(bot)
    if usr_id not in USERS:
        register_user(msg) # тут хуйня написана, но трогать лень
        #print('NEW USER: ', USERS[usr_id])

def check_registration_bymsg(msg):
    usr_id = get_id_bymsg(msg)
    if usr_id not in USERS:
        register_user(msg)
        #print('NEW USER: ', USERS[usr_id])
    else:
        first_name = msg.from_user['first_name']
        last_name = msg.from_user['last_name']
        username = msg.from_user['username']
        if USERS[usr_id]['first_name'] != first_name:
            USERS[usr_id]['first_name'] = first_name
        if USERS[usr_id]['last_name'] != last_name:
            USERS[usr_id]['last_name'] = last_name
        if USERS[usr_id]['username'] != username:
           USERS[usr_id]['username'] = username

def get_id(bot):
    return str(bot.effective_user['id'])

def get_id_bymsg(msg):
    return str(msg.from_user['id'])

def update_timetable(msg, force=False):
    usr_id = get_id_bymsg(msg)

    if not force and (USERS[usr_id]['group'] == None or USERS[usr_id]['group'] == ''):
        return 

    if not force and USERS[usr_id]['last_timetable_update'] != None and time.time() - USERS[usr_id]['last_timetable_update'] < CRITICAL_LAST_TIMETABLE_UPDATE_TIME:
        return
    
    workbook = xlrd.open_workbook('IIT-1-kurs_27.09.2022.xlsx', on_demand=True)

    for sheet_num in range(len(workbook.sheet_names())):
        worksheet = workbook.sheet_by_index(sheet_num)
        if USERS[usr_id]['group'] == worksheet.cell_value(1, 5):
            USERS[usr_id]['timetable'] = {i : [] for i in WEEKDAYS}
            base_column = 5
            base_row = 3

            for day in WEEKDAYS:
                for row in range(base_row, base_row + 12, 2):
                    row1 = clear_timetable_row(worksheet.cell_value(row, base_column))
                    row2 = clear_timetable_row(worksheet.cell_value(row + 1, base_column))
                    USERS[usr_id]['timetable'][day].append((row1, row2))
                base_row += 12
            break
        elif USERS[usr_id]['group'] == worksheet.cell_value(1, 10):
            USERS[usr_id]['timetable'] = {i : [] for i in WEEKDAYS}
            base_column = 10
            base_row = 3

            for day in WEEKDAYS:
                for row in range(base_row, base_row + 12, 2):
                    row1 = clear_timetable_row(worksheet.cell_value(row, base_column))
                    row2 = clear_timetable_row(worksheet.cell_value(row + 1, base_column))
                    USERS[usr_id]['timetable'][day].append((row1, row2))
                base_row += 12
            break

    workbook.release_resources()
    del workbook
    USERS[usr_id]['last_timetable_update'] = time.time()
    write_users()

def clear_timetable_row(row):
    del_list = ['кр.', 'н.', ',']
    del_list += [str(i) for i in range(10)]
    new_row = row.strip()
    for i in del_list:
        new_row = new_row.replace(i, '')
    return new_row.strip()

def get_pairs(msg, dt):
    usr_id = get_id_bymsg(msg)
    update_timetable(msg)
    weekday = dt.strftime('%A')

    if USERS[usr_id]['timetable'] == {}:
        return list()

    pairs = USERS[usr_id]['timetable'][weekday]
    weeknum = dt.isocalendar()[1] - datetime.date(dt.year, 9, 1).isocalendar()[1] + 1
    if weeknum % 2 == 1:
        return [i[0] for i in pairs]
    else:
        return [i[1] for i in pairs]

def get_today_pairs(msg):
    return get_pairs(msg, datetime.datetime.today())

def get_pairs_nums(msg, dt):
    pairs = get_pairs(msg, dt)
    if pairs == []:
        return None
    else:
        res = []
        for i in range(len(pairs)):
            if pairs[i] != '':
                res.append(i + 1)
        return res

def get_today_pairs_nums(msg):
    return get_pairs_nums(msg, datetime.datetime.today())

def get_nearest_pair_time(msg, dt): # dt ОБЯЗАТЕЛЬНО типа datetime.date, иначе пизды получишь
    delta = datetime.timedelta(days=1)
    i = 0
    while dt.month == (dt + delta * i).month:
        pairs = get_pairs_nums(msg, dt)
        if pairs != None and len(pairs) > 0:
            for p in pairs:
                if datetime.datetime.now() < datetime.datetime.combine(dt + delta * i, PAIRS_TIME[pairs[p]]['start']):
                    return datetime.datetime.combine(dt + delta * i, PAIRS_TIME[pairs[p]]['start'])
        i += 1
    return None

def norm_word(x): # приводит слово к начальной форме
    global MORPH
    p = MORPH.parse(x)[0]
    return p.normal_form

def clear_msg(msg): # удаляет говно из сообщения
    del_list = '.,;:`()' 
    p_msg = msg.strip().lower()
    trantab = p_msg.maketrans('', '', del_list)
    p_msg = p_msg.translate(trantab)
    if len(p_msg) >= 1:
        p_msg = p_msg[0].upper() + p_msg[1:]
    else:
        p_msg = msg
    return p_msg

def compute_emo_rate(msg): # вычисляет эмоциональную окраску сообщения (пытается)
    del_list = '.,;!?:`()' 
    p_msg = msg.strip().lower()
    trantab = p_msg.maketrans('', '', del_list)
    p_msg = p_msg.translate(trantab)

    if p_msg == 'прости': # ульта
        return 1

    if p_msg == 'ёб твой рот': # ульта
        return -1

    msg_words = p_msg.split()
    rate = 0
    for word in msg_words:
        norm = norm_word(word)
        if norm in WORDS:
            rate += WORDS[norm]
    if len(msg_words) == 0:
        if ')' in msg and '(' not in msg: # ульта 2
            return 1
        else:
            return 0
    return rate / len(msg_words)

def get_minutes_declension(x):
    x_last = x % 10
    if x_last == 0 or x_last >= 5 or 10 <= x <= 20:
        return 'минут'
    elif x_last == 1:
        return 'минута'
    else:
        return 'минуты'

def get_seconds_declension(x):
    x_last = x % 10
    if x_last == 0 or x_last >= 5 or 10 <= x <= 20:
        return 'секунд'
    elif x_last == 1:
        return 'секунда'
    else:
        return 'секунды'

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None): # это я вообще на каком-то форуме подрезал
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def get_stat(usr_id): # выдаёт пользователю стату
    res = ''
    res += 'Отправлено сообщений: ' + str(USERS[usr_id]['msg_count']) + '\n'
    res += 'Картинок открыто: ' + str(USERS[usr_id]['pics_unlocked']) + '/' + str(len(glob('LEGS/*'))) + '\n'
    res += 'Настроение твоей Кагуи: ' + str(round(USERS[usr_id]['mood'], 2))[:5] + '\n'
    return res

def get_admin_stat(usr_id): # выдаёт админам личные данные пользователей
    if USERS[usr_id]['username'] is not None:
        res = 'username: @' + USERS[usr_id]['username'] + '\n'
    else:
        res = 'username: NULL' + '\n'
    res += 'Имя: ' + USERS[usr_id]['first_name']
    if USERS[usr_id]['last_name'] != None:
        res += ' ' + USERS[usr_id]['last_name']
    res += '\n-----------------------------------------\n'
    res += 'Отправлено сообщений: ' + str(USERS[usr_id]['msg_count']) + '\n'
    res += 'Картинок открыто: ' + str(USERS[usr_id]['pics_unlocked']) + '/' + str(len(glob('LEGS/*'))) + '\n'
    res += 'Настроение: ' + str(round(USERS[usr_id]['mood'], 2))[:5] + '\n'
    return res


#############################
# А ВОТ ТУТ УЖЕ РЕАЛ БОТИК

def greeting_to_unseen_user(msg): # тебя давно не было в уличных гонках
    msg.reply_text('Я давно тебя не видела, сенпай!\nНа всякий случай, пропиши ещё раз\n/start - вдруг у меня появились новые функции!')

def sms(bot, update): # отвечает на /start
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    keyboard = ReplyKeyboardMarkup([['Скинь ножки', 'Какой сегодня день?'], ['Кто я сегодня?', 'Сколько до перекура?'], ['Какая погода сейчас?', 'Рандомчик'], ['Во сколько мне завтра вставать?']], resize_keyboard=True)
    bot.message.reply_text('Охае, {}!'.format(bot.message.chat.first_name))
    time.sleep(SLEEP_TIME)
    bot.message.reply_text("Меня зовут Кагуя Синомия. Давай поболтаем (чтобы увидеть всё, что я могу, напиши /help)", reply_markup=keyboard)
    #update.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAADAgADOQADfyesDlKEqOOd72VKAg')
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def help_user(bot, update): # отвечает на /help
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    bot.message.reply_text(HELP_TEXT)
    USERS[usr_id]['last_usage'] = time.time()
    write_users()    

def stat(bot, update): # отвечает на /stat
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    if usr_id in ADMINS_ID:
        for u in USERS:
            bot.message.reply_text(get_admin_stat(u))
    else:
        bot.message.reply_text(get_stat(usr_id))
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def exec_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    if usr_id in ADMINS_ID:
        cmd = bot.message.text[5:]
        stream = os.popen(cmd)
        output = stream.read()
        bot.message.reply_text(output)
    else:
        bot.message.reply_text('Иди нах')
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def set_group_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    USERS[usr_id]['group'] = bot.message.text[11:].strip()

    update_timetable(bot.message, force=True)
    bot.message.reply_text(str(USERS[usr_id]['group']) + '\nПринято!')
    #bot.message.reply_text(str(USERS[usr_id]['timetable']))

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def set_wakeup_time_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    inp_str = bot.message.text[17:].strip()

    base_get_up_time = datetime.time(0, 0)
    try:
        base_get_up_time = datetime.datetime.strptime(inp_str, "%H:%M").time()
    except:
        try:
            base_get_up_time = datetime.datetime.strptime(inp_str, "%H %M").time()
        except:
            try:
                base_get_up_time = datetime.datetime.strptime(inp_str, "%H").time()
            except:
                time.sleep(SLEEP_TIME)
                bot.message.reply_text('Эммм...')
                return
    USERS[usr_id]['base_get_up_time_hour'] = base_get_up_time.hour
    USERS[usr_id]['base_get_up_time_minute'] = base_get_up_time.minute

    time.sleep(SLEEP_TIME)
    bot.message.reply_text('{}\nГотово'.format(base_get_up_time.strftime("%H:%M")))

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def disable_groups_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    USERS[usr_id]['show_set_group_notice'] = False

    time.sleep(SLEEP_TIME)
    bot.message.reply_text('Успешно')

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def add_skip_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    inp = bot.message.text[10:].strip().split()

    try:
        dt = inp[0]
        if len(inp) > 1:
            pair_num = inp[1]
        else:
            pair_num = -1
    except:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Эмм...')
        return

    try:
        dt = datetime.datetime.strptime(dt, "%d.%m")
    except:
        try:
            dt = datetime.datetime.strptime(dt, "%d.%m.%Y")
        except:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Эмм...')
            return

    try:
        pair_num = int(pair_num)
    except:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Эмм...')
        return
    
    if not (6 >= pair_num >= 1) and pair_num != -1:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Нет таких пар, дэбил')
        return
    
    dt_pairs = get_pairs(bot.message, dt)
    if dt_pairs == [] or pair_num == -1:
        skip = {
            'type': ('undefined', 'single'),
            'date': datetime.datetime.strftime(dt, DEFAULT_DATE_FORMAT)
        }
    else:
        if dt_pairs[pair_num - 1] == '':
            skip = {
                'type': ('defined', 'single'),
                'date': datetime.datetime.strftime(dt, DEFAULT_DATE_FORMAT),
                'pair_num': pair_num,
                'pair_name': 'Нет информации'
            }
        else:
            skip = {
                'type': ('defined', 'single'),
                'date': datetime.datetime.strftime(dt, DEFAULT_DATE_FORMAT),
                'pair_num': pair_num,
                'pair_name': dt_pairs[pair_num - 1]
            }

    USERS[usr_id]['pair_skips'].append(skip)

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def add_skips_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    inp = bot.message.text[11:].strip().split()
    try:
        begin_date = inp[0]
        end_date = inp[1]
        amount = inp[2]
    except:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Эмм...')
        return
    
    try:
        begin_date = datetime.datetime.strptime(begin_date, "%d.%m")
    except:
        try:
            begin_date = datetime.datetime.strptime(begin_date, "%d.%m.%y")
        except:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Эмм...')
            return
    
    try:
        end_date = datetime.datetime.strptime(end_date, "%d.%m")
    except:
        try:
            end_date = datetime.datetime.strptime(end_date, "%d.%m.%y")
        except:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Эмм...')
            return

    try:
        amount = int(amount)
    except:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Эмм...')
        return

    skip = {
        'type': ('undefined', 'multi'),
        'begin_date': datetime.datetime.strftime(begin_date, DEFAULT_DATE_FORMAT),
        'end_date': datetime.datetime.strftime(end_date, DEFAULT_DATE_FORMAT),
        'amount': amount
    }

    USERS[usr_id]['pair_skips'].append(skip)

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def skips_cmd(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    bot.message.reply_text(USERS[usr_id]['pair_skips'])

    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def reply(bot, update): # ответ на обычное сообщение
    global USERS
    global MOOD_FADING
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if bot.message.text == QUIT_TEXT and usr_id in ADMINS_ID:
        quit()
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['city'] = bot.message.text
        USERS[usr_id]['waiting_for_city'] = False
        sendweather(bot, update)
        return
    if USERS[usr_id]['waiting_for_random']:
        try:
            USERS[usr_id]['rand_max'] = int(bot.message.text)
        except Exception:
            USERS[usr_id]['rand_max'] = -1
        if USERS[usr_id]['rand_max'] == 0:
            USERS[usr_id]['rand_max'] = -1
        USERS[usr_id]['waiting_for_random'] = False
        dorandom(bot, update)
        return
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
        base_get_up_time = datetime.time(0, 0)
        try:
            base_get_up_time = datetime.datetime.strptime(bot.message.text, "%H:%M").time()
        except:
            try:
                base_get_up_time = datetime.datetime.strptime(bot.message.text, "%H %M").time()
            except:
                try:
                    base_get_up_time = datetime.datetime.strptime(bot.message.text, "%H").time()
                except:
                    time.sleep(SLEEP_TIME)
                    bot.message.reply_text('Эммм...')
                    return
        USERS[usr_id]['base_get_up_time_hour'] = base_get_up_time.hour
        USERS[usr_id]['base_get_up_time_minute'] = base_get_up_time.minute
        whentogetup(bot, update)
        return
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    emo_rate = compute_emo_rate(bot.message.text)
    USERS[usr_id]['mood'] = MOOD_FADING * USERS[usr_id]['mood'] + emo_rate
    if -0.1 < USERS[usr_id]['mood'] < 0 and emo_rate >= 0: # если Кагуя не сильно злится, а чел не сильно злит
        USERS[usr_id]['mood'] = 0                          # прощаем ему всю хуйню
    log(bot.message)
    if random.random() <= 0.01: # имба, редкость
        bot.message.reply_text('Когда ты мне пишешь...')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Твоё сообщение')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('И я просто выхожу на хаха')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Это так забавно мне')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Я просто ссу себе в штаныыы')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Ссу себе в штаны')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Это невероятно')
    else:
        is_why = False
        for q in WHY:
            if q in bot.message.text.lower():
                is_why = True
                break
        # Сюда лучше не лезть без должной подготовки
        #print(clear_msg(bot.message.text))
        if clear_msg(bot.message.text)[:5] == 'Скажи':
            rep = bot.message.text[6:]
        elif clear_msg(bot.message.text) == 'Как там блин блинский' or clear_msg(bot.message.text) == 'Как там блин блинский?':
            cmd = 'ps | grep python3 | grep Blin.py'
            stream = os.popen(cmd)
            output = stream.read()
            if output.count('Blin.py') > 1:
                rep = 'Норм'
            else:
                bot.message.reply_text('Лёг нахуй, делаем ребут')
                os.popen('reboot -f')
        elif ' или' in bot.message.text.lower() and bot.message.text.lower().split(' или ')[0] != ' ' and bot.message.text.lower().split(' или ')[0] != '':
            ch = bot.message.text.split(' или ')[random.randint(0, 1)].lower()
            if ch[-1] == '?' or ch[-1] == '.':
                ch = ch[:-1]
            rep = OR_ANSWERS[random.randint(0, len(OR_ANSWERS) - 1)] + ' ' + ch
        elif is_why:
            if USERS[usr_id]['mood'] < 0:
                rep = NEGATIVE_WHY_ANSWERS[random.randint(0, len(NEGATIVE_WHY_ANSWERS) - 1)]
            else:
                rep = POSITIVE_WHY_ANSWERS[random.randint(0, len(POSITIVE_WHY_ANSWERS) - 1)]
        elif bot.message.text.lower() in APPEALS:
            if USERS[usr_id]['mood'] < 0:
                rep = NEGATIVE_APPEALS_ANSWERS[random.randint(0, len(NEGATIVE_APPEALS_ANSWERS) - 1)]
            else:
                rep = POSITIVE_APPEALS_ANSWERS[random.randint(0, len(POSITIVE_APPEALS_ANSWERS) - 1)]
        elif bot.message.text.lower() in HI:
            hour = datetime.datetime.now().hour
            if hour >= EVENING_START or hour < MORNING_START:
                rep = GOOD_EVENING[random.randint(0, len(GOOD_EVENING) - 1)]
            elif hour < DAY_START:
                rep = GOOD_MORNING[random.randint(0, len(GOOD_MORNING) - 1)]
            else:
                rep = GOOD_DAY[random.randint(0, len(GOOD_DAY) - 1)]
        elif bot.message.text.lower() in BYE:
            hour = datetime.datetime.now().hour
            if hour < NIGHT_START and hour >= MORNING_START:
                rep = HAVE_A_GOOD_DAY[random.randint(0, len(HAVE_A_GOOD_DAY) - 1)]
            else:
                rep = HAVE_A_GOOD_NIGHT[random.randint(0, len(HAVE_A_GOOD_NIGHT) - 1)]
        elif bot.message.text.lower() in WHATSUP_QUESTIONS or bot.message.text.lower() + '?' in WHATSUP_QUESTIONS:
            if USERS[usr_id]['mood'] < 0:
                rep = NEGATIVE_WAHATSUP_ANSWERS[random.randint(0, len(NEGATIVE_WAHATSUP_ANSWERS) - 1)]
            else:
                rep = POSITIVE_WAHATSUP_ANSWERS[random.randint(0, len(POSITIVE_WAHATSUP_ANSWERS) - 1)]
        elif USERS[usr_id]['mood'] < 0:
            if '?' in bot.message.text:
                rep = NEGATIVE_QUIESTION_ANSWERS[random.randint(0, len(NEGATIVE_QUIESTION_ANSWERS) - 1)]
            else:
                if random.random() <= REPLY_WITH_USR_MSG and len(USERS[usr_id]['top_messages']) > 0 and len(USERS[usr_id]['max_rating_neg_msgs']) > 0:
                    attempts = 0
                    rep = USERS[usr_id]['max_rating_neg_msgs'][random.randint(0, len(USERS[usr_id]['max_rating_neg_msgs']) - 1)]
                    while attempts <= 5 and time.time() - USERS[usr_id]['top_messages'][rep]['time'] <= 30:
                        rep = USERS[usr_id]['max_rating_neg_msgs'][random.randint(0, len(USERS[usr_id]['max_rating_neg_msgs']) - 1)]
                        attempts += 1
                    if rep == '':
                        rep = NEGATIVE_REPLIES[random.randint(0, len(NEGATIVE_REPLIES) - 1)]
                else:
                    rep = NEGATIVE_REPLIES[random.randint(0, len(NEGATIVE_REPLIES) - 1)]
        else:
            if '?' in bot.message.text:
                rep = POSITIVE_QUESTION_ANSWERS[random.randint(0, len(POSITIVE_QUESTION_ANSWERS) - 1)]
            else:
                if random.random() <= REPLY_WITH_USR_MSG and len(USERS[usr_id]['top_messages']) > 0 and len(USERS[usr_id]['max_rating_pos_msgs']) > 0:
                    attempts = 0
                    rep = USERS[usr_id]['max_rating_pos_msgs'][random.randint(0, len(USERS[usr_id]['max_rating_pos_msgs']) - 1)]
                    while attempts <= 5 and time.time() - USERS[usr_id]['top_messages'][rep]['time'] <= 30:
                        rep = USERS[usr_id]['max_rating_pos_msgs'][random.randint(0, len(USERS[usr_id]['max_rating_pos_msgs']) - 1)]
                        attempts += 1
                    if rep == '':
                        rep = POSITIVE_REPLIES[random.randint(0, len(POSITIVE_REPLIES) - 1)]
                else:
                    rep = POSITIVE_REPLIES[random.randint(0, len(POSITIVE_REPLIES) - 1)]
        time.sleep(SLEEP_TIME)
        bot.message.reply_text(rep)
    for m in USERS[usr_id]['top_messages']:
        USERS[usr_id]['top_messages'][m]['rating'] *= 1 - MESSAGE_RATING_FADING
    msg = clear_msg(bot.message.text)
    mrp_m = USERS[usr_id]['max_rating_pos_msgs']
    mrn_m = USERS[usr_id]['max_rating_neg_msgs']
    if msg not in USERS[usr_id]['top_messages'] and 'кагуя' not in msg.lower():
        while len(USERS[usr_id]['top_messages']) >= TOP_MESSAGES_SIZE:
            min_r = float('inf')
            del_m = ''
            for m in USERS[usr_id]['top_messages']:
                if USERS[usr_id]['top_messages'][m]['rating'] < min_r:
                    min_r = USERS[usr_id]['top_messages'][m]['rating']
                    del_m = m
            USERS[usr_id]['top_messages'].pop(del_m)
        USERS[usr_id]['top_messages'][msg] = {
            'text' : msg,
            'emo_rate' : compute_emo_rate(bot.message.text),
            'rating' : DEFAULT_RATING,
            'time' : time.time()
        }
        
        if USERS[usr_id]['top_messages'][msg]['emo_rate'] >= 0 and (len(mrp_m) < MAX_RATING_POS_MSGS_SIZE or USERS[usr_id]['top_messages'][msg]['rating'] > USERS[usr_id]['top_messages'][mrp_m[-1]]['rating']):
            if len(mrp_m) >= MAX_RATING_POS_MSGS_SIZE:
                mrp_m.pop(-1)
            mrp_m.append(msg)
            i = len(mrp_m) - 1
            while i > 0 and USERS[usr_id]['top_messages'][mrp_m[i]]['rating'] > USERS[usr_id]['top_messages'][mrp_m[i - 1]]['rating']:
                mrp_m[i], mrp_m[i - 1] = mrp_m[i - 1], mrp_m[i]
                i -= 1
            USERS[usr_id]['max_rating_pos_msgs'] = mrp_m
        if USERS[usr_id]['top_messages'][msg]['emo_rate'] < 0 and (len(mrn_m) < MAX_RATING_NEG_MSGS_SIZE or USERS[usr_id]['top_messages'][msg]['rating'] > USERS[usr_id]['top_messages'][mrn_m[-1]]['rating']):
            if len(mrn_m) >= MAX_RATING_NEG_MSGS_SIZE:
                mrn_m.pop(-1)
            mrn_m.append(msg)
            i = len(mrn_m) - 1
            while i > 0 and USERS[usr_id]['top_messages'][mrn_m[i]]['rating'] > USERS[usr_id]['top_messages'][mrn_m[i - 1]]['rating']:
                mrn_m[i], mrn_m[i - 1] = mrn_m[i - 1], mrn_m[i]
                i -= 1
            USERS[usr_id]['max_rating_neg_msgs'] = mrn_m
    elif 'кагуя' not in msg.lower():
        USERS[usr_id]['top_messages'][msg]['rating'] += 1
        if USERS[usr_id]['top_messages'][msg]['emo_rate'] >= 0 and (len(mrp_m) < MAX_RATING_POS_MSGS_SIZE or USERS[usr_id]['top_messages'][msg]['rating'] > USERS[usr_id]['top_messages'][mrp_m[-1]]['rating']):
            if len(mrp_m) >= MAX_RATING_POS_MSGS_SIZE:
                mrp_m.pop(-1)
            mrp_m.append(msg)
            i = len(mrp_m) - 1
            while i > 0 and USERS[usr_id]['top_messages'][mrp_m[i]]['rating'] > USERS[usr_id]['top_messages'][mrp_m[i - 1]]['rating']:
                mrp_m[i], mrp_m[i - 1] = mrp_m[i - 1], mrp_m[i]
                i -= 1
            USERS[usr_id]['max_rating_pos_msgs'] = mrp_m
        if USERS[usr_id]['top_messages'][msg]['emo_rate'] < 0 and (len(mrn_m) < MAX_RATING_NEG_MSGS_SIZE or USERS[usr_id]['top_messages'][msg]['rating'] > USERS[usr_id]['top_messages'][mrn_m[-1]]['rating']):
            if len(mrn_m) >= MAX_RATING_NEG_MSGS_SIZE:
                mrn_m.pop(-1)
            mrn_m.append(msg)
            i = len(mrn_m) - 1
            while i > 0 and USERS[usr_id]['top_messages'][mrn_m[i]]['rating'] > USERS[usr_id]['top_messages'][mrn_m[i - 1]]['rating']:
                mrn_m[i], mrn_m[i - 1] = mrn_m[i - 1], mrn_m[i]
                i -= 1
            USERS[usr_id]['max_rating_neg_msgs'] = mrn_m
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def whoami(bot, update): # отвечает на "Кто я сегодня?"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    if USERS[usr_id]['mood'] < 0:
        rep = NEGATIVE_WHOAMI_REPLIES[random.randint(0, len(NEGATIVE_WHOAMI_REPLIES) - 1)]
    else:
        rep = POSITIVE_WHOAMI_REPLIES[random.randint(0, len(POSITIVE_WHOAMI_REPLIES) - 1)]
    time.sleep(SLEEP_TIME)
    bot.message.reply_text('{}, ты сегодня такой {}'.format(bot.message.chat.first_name, rep))
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def dorandom(bot, update): # отвечает на "Рандомчик"
    global CONTROL_MSGS
    global USERS
    try:
        usr_id = get_id_bymsg(bot.message)
        check_registration_bymsg(bot.message)
    except Exception:
        usr_id = get_id_bymsg(CONTROL_MSGS[get_id(bot)])
        check_registration_bymsg(CONTROL_MSGS[get_id(bot)])
    if bot.message != None:
        USERS[usr_id]['msg_count'] += 1
        CONTROL_MSGS[get_id(bot)] = bot.message
        log(bot.message)
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    
    if USERS[usr_id]['rand_max'] == 0:
        bot.message.reply_text('Хорошо, я должна назвать рандомное число от 1 до .. ?')
        USERS[usr_id]['waiting_for_random'] = True
    else:
        try:
            rand = random.randint(1, USERS[usr_id]['rand_max'])
            CONTROL_MSGS[get_id(bot)].reply_text('Не знаю, зачем тебе это, но пусть будет ' + str(rand) + '.')
        except Exception:
            CONTROL_MSGS[get_id(bot)].reply_text('Эмм...')
        USERS[usr_id]['rand_max'] = 0
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def sendlegs(bot, update): # отвечает на "Скинь ножки"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    if USERS[usr_id]['mood'] < 0:
        rep = NEGATIVE_QUIESTION_ANSWERS[random.randint(0, len(NEGATIVE_QUIESTION_ANSWERS) - 1)]
        bot.message.reply_text(rep)
    else:
        list = glob('LEGS/*')
        pic = choice(list)
        num = int(pic[5:-4]) # получаем номер пикчи просто, не пугайся
        while num > len(USERS[usr_id]['pics']) - 1:
            USERS[usr_id]['pics'].append(False)
        if USERS[usr_id]['pics'][num] == False:
            USERS[usr_id]['pics'][num] = True
            USERS[usr_id]['pics_unlocked'] += 1
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Ну.... Хорошо')
        time.sleep(SLEEP_TIME)
        if pic == 'LEGS\\0.png' or pic == 'LEGS/0.png':
            text = 'Хаха, я тебя затроллила)'
        else:
            text = 'Надеюсь, тебе понравилось)'
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
        time.sleep(SLEEP_TIME)
        bot.message.reply_text(text)
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def sendday(bot, update): # отвечает на "Какой сегодня день?"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)
    bot.message.reply_text('Хммм, дай-ка подумать')
    pic = ''
    weekday = datetime.datetime.today().weekday()
    if weekday == 0:
        pic = 'DAY/monday.jpg'
    elif weekday == 1:
        pic = 'DAY/tuesday.jpg'
    elif weekday == 2:
        pic = 'DAY/wednesday.jpg'
    elif weekday == 3:
        pic = 'DAY/thursday.jpg'
    elif weekday == 4:
        pic = 'DAY/friday.jpg'
    elif weekday == 5:
        pic = 'DAY/saturday.jpg'
    elif weekday == 6:
        pic = 'DAY/sunday.jpg'

    time.sleep(SLEEP_TIME)
    update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
    time.sleep(SLEEP_TIME)
    bot.message.reply_text('Сегодня:\n' + HOLIDAYS[str(date.today().day) + ' ' + MONTHS[date.today().month-1]])
    time.sleep(SLEEP_TIME)
    if USERS[usr_id]['mood'] < 0:
        rep = 'Хуёвого дня'
    else:
        rep = 'Хорошего дня'
    bot.message.reply_text('Это, кстати, {} {}. {}, {})'.format(date.today().day, MONTHS[date.today().month-1], rep, bot.message.chat.first_name))
    USERS[usr_id]['last_usage'] = time.time()
    write_users()


def whensmoketime(bot, update): #когда там перекур
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    time.sleep(SLEEP_TIME)
    bot.message.reply_text('Нууу ладно, сейчас посчитаю')

    today_pairs_nums = get_today_pairs_nums(bot.message)
    curr_time = datetime.datetime.now().time()
    curr_state = 'не на парах' # возможные состояния: не на парах, на паре, перекур
    time_to_smoke = 0
    time_to_smoke_minutes = 0
    time_to_smoke_seconds = 0
    time_to_next_pair = -1  # -1 значит что следующей пары нет
    time_to_next_pair_minutes = 0
    time_to_next_pair_seconds = 0
    pair_num = 0

    if USERS[usr_id]['group'] == '' or today_pairs_nums == None:
        if USERS[usr_id]['show_set_group_notice']:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('(Кстати, ты можешь указать свою группу при помощи команды /set_group [группа] и я буду показывать тебе более точную информацию о перекурах)')
        today_pairs_nums = PAIRS_TIME.keys()

    for p_num in today_pairs_nums:
        p_start = PAIRS_TIME[p_num]['start']
        p_end = PAIRS_TIME[p_num]['end']

        if p_end >= curr_time >= p_start:
            curr_state = 'на паре'
            pair_num = p_num
            time_to_smoke = datetime.datetime.combine(datetime.date.today(), p_end) - datetime.datetime.combine(datetime.date.today(), curr_time)
            time_to_smoke_seconds = time_to_smoke.seconds + round(time_to_smoke.microseconds/10**6)
            time_to_smoke_minutes = round((time_to_smoke.seconds + round(time_to_smoke.microseconds/10**6)) / 60)
            # получается время в минутах
        elif p_num + 1 in today_pairs_nums:
            next_p_start = PAIRS_TIME[p_num + 1]['start']
            if next_p_start >= curr_time >= p_end:
                curr_state = 'перекур'
                time_to_next_pair = datetime.datetime.combine(datetime.date.today(), next_p_start) - datetime.datetime.combine(datetime.date.today(), curr_time)
                time_to_next_pair_seconds = time_to_next_pair.seconds + round(time_to_next_pair.microseconds/10**6)
                time_to_next_pair_minutes = round((time_to_next_pair.seconds + round(time_to_next_pair.microseconds/10**6)) / 60)

    if curr_state == 'на паре':
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Так, сейчас у тебя {} пара'.format(pair_num))
        
        if time_to_smoke_minutes >= 60:
            time_to_smoke_minutes -= 60
            if time_to_smoke_minutes == 0:
                bot.message.reply_text('До перекура 1 час')
            else:
                bot.message.reply_text('До перекура 1 час {} {}'.format(time_to_smoke_minutes, get_minutes_declension(time_to_smoke_minutes)))
        elif time_to_smoke_seconds < 60:
            bot.message.reply_text('До перекура {} {}'.format(time_to_smoke_seconds, get_seconds_declension(time_to_smoke_seconds)))
        else:  
            bot.message.reply_text('До перекура {} {}'.format(time_to_smoke_minutes, get_minutes_declension(time_to_smoke_minutes)))

        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Учись усерднее, {}'.format(bot.message.chat.first_name))

        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('SMOKETIME/learntime.jpg', 'rb'))
    elif curr_state == 'перекур':

        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Ура, бегом на перекур!!!')
        
        if time_to_next_pair != -1:
            if time_to_next_pair_seconds < 60:
                bot.message.reply_text('До начала пары {} {}'.format(time_to_next_pair_seconds, get_seconds_declension(time_to_next_pair_seconds)))
            else:
                bot.message.reply_text('До начала пары {} {}'.format(time_to_next_pair_minutes, get_minutes_declension(time_to_next_pair_minutes)))
        
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('SMOKETIME/smoketime.jpg', 'rb'))
    else:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Чел, ты не на парах')

        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('SMOKETIME/notyet.png', 'rb'))

        nearest_pair = get_nearest_pair_time(bot.message, datetime.date.today())
        if nearest_pair != None:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Ближайшая пара {}'.format(nearest_pair.strftime("%d.%m в %H:%M")))

    USERS[usr_id]['last_usage'] = time.time()
    write_users()    

def whentogetup(bot, update):
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        greeting_to_unseen_user(bot.message)

    
    if USERS[usr_id]['base_get_up_time_hour'] == None or USERS[usr_id]['base_get_up_time_minute'] == None:
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Во сколько ты встаёшь к первой паре?')
        USERS[usr_id]['waiting_for_get_up_time'] = True
    else:
        base_get_up_time = datetime.time(USERS[usr_id]['base_get_up_time_hour'], USERS[usr_id]['base_get_up_time_minute'])
        if datetime.datetime.now().hour < NIGHT_LIMIT:
            tomorrow_pairs_nums = get_pairs_nums(bot.message, datetime.date.today())
        else:
            tomorrow_pairs_nums = get_pairs_nums(bot.message, datetime.date.today() + datetime.timedelta(days=1))
        if tomorrow_pairs_nums == None:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Я не знаю, какие пары у тебя завтра. Похуй, вставай в {}'.format(base_get_up_time.strftime("%H:%M")))
            if USERS[usr_id]['show_set_group_notice']:
                time.sleep(SLEEP_TIME)
                bot.message.reply_text('(Если хочешь, чтобы я знала, когда у тебя пары, укажи свою группу через команду /set_group [группа])')
        elif len(tomorrow_pairs_nums) == 0:
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Завтра нет пар!!')

            nearest_pair = get_nearest_pair_time(bot.message, datetime.date.today())
            if nearest_pair != None:
                time.sleep(SLEEP_TIME)
                bot.message.reply_text('Ближайшая пара {}'.format(nearest_pair.strftime("%d.%m в %H:%M")))
        else:
            first_pair = min(tomorrow_pairs_nums)
            get_up_time = datetime.datetime.combine(datetime.date.today(), PAIRS_TIME[first_pair]['start']) - datetime.datetime.combine(datetime.date.today(), PAIRS_TIME[1]['start'])
            get_up_time += datetime.datetime.combine(datetime.date.today(), base_get_up_time)
            
            time.sleep(SLEEP_TIME)
            bot.message.reply_text('Вставай в {}'.format(get_up_time.strftime("%H:%M")))
            
    USERS[usr_id]['last_usage'] = time.time()
    write_users()    

def weather(city: str): # получает погоду у врагов с Запада
    config_dict = cfg.get_default_config()
    config_dict['language'] = 'ru' 
    owm = OWM('b14672eeb4d058d2334c4b97a4c84aa0', config_dict)
    mgr = owm.weather_manager()
    obs = mgr.weather_at_place(city)
    weather = obs.weather
    temp = weather.temperature("celsius")
    detail = weather.detailed_status
    return temp, detail

def change_weather_city(bot, update): # на случай если челик переобулся и захотел сменить город
    usr_id = str(bot.effective_user['id'])
    #check_registration(bot.message)
    USERS[usr_id]['city'] = ''
    sendweather(bot, update)

def sendweather(bot, update): # отправляет погоду
    global CONTROL_MSGS
    global USERS
    try:
        usr_id = get_id_bymsg(bot.message)
        check_registration_bymsg(bot.message)
    except Exception:
        usr_id = get_id_bymsg(CONTROL_MSGS[get_id(bot)])
        check_registration_bymsg(CONTROL_MSGS[get_id(bot)])
    if bot.message != None:
        USERS[usr_id]['msg_count'] += 1
        CONTROL_MSGS[get_id(bot)] = bot.message
        log(bot.message)
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['waiting_for_random']:
        USERS[usr_id]['waiting_for_random'] = False
    if USERS[usr_id]['waiting_for_get_up_time']:
        USERS[usr_id]['waiting_for_get_up_time'] = False
    if time.time() - USERS[usr_id]['last_usage'] > CRITICAL_LAST_USAGE_TIME:
        try:
            greeting_to_unseen_user(bot.message)
        except Exception:
            greeting_to_unseen_user(CONTROL_MSGS[usr_id])
    if USERS[usr_id]['city'] == '':
        USERS[usr_id]['waiting_for_city'] = True
        CONTROL_MSGS[get_id(bot)].reply_text('Напиши название города')
        return
    
    btn_text = 'Погода в другом городе'
    button_list = [InlineKeyboardButton(btn_text, callback_data = btn_text)]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,n_cols=1))

    try:
        w = weather(USERS[usr_id]['city'])
        rep = 'В городе ' + USERS[usr_id]['city'] + ' сейчас ' + str(round(w[0]["temp"])) + '°C, ' + w[1]
    except Exception as e:
        rep = 'А этот город вообще существует, дурачье?'
        USERS[usr_id]['city'] = ''
    CONTROL_MSGS[get_id(bot)].reply_text(rep, reply_markup=reply_markup)    
    USERS[usr_id]['last_usage'] = time.time()
    write_users()

def sendweather_handler(bot, update): # вызывается при вопросе про погоду, имба функция
    sendweather(bot, update)

def main(): # БАЗА
    read_words()
    read_holidays()
    read_users()
    print('Started')
    bot = Updater("5260290537:AAGWg9J4a5dZDqsrq3MG3fejuBvD-0tasOA", use_context=True)
    bot.dispatcher.add_handler(CommandHandler('start', sms))
    bot.dispatcher.add_handler(CommandHandler('help', help_user))
    bot.dispatcher.add_handler(CommandHandler('stat', stat))
    bot.dispatcher.add_handler(CommandHandler('exec', exec_cmd))
    bot.dispatcher.add_handler(CommandHandler('set_group', set_group_cmd))
    bot.dispatcher.add_handler(CommandHandler('set_wakeup_time', set_wakeup_time_cmd))
    bot.dispatcher.add_handler(CommandHandler('disable_groups', disable_groups_cmd))
    bot.dispatcher.add_handler(CommandHandler('add_skip', add_skip_cmd))
    bot.dispatcher.add_handler(CommandHandler('add_skips', add_skips_cmd))
    bot.dispatcher.add_handler(CommandHandler('skips', skips_cmd))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Кто я сегодня?'), whoami))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Скинь ножки'), sendlegs))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Рандомчик'), dorandom))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какой сегодня день?'), sendday))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Сколько до перекура?'), whensmoketime))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Во сколько мне завтра вставать?'), whentogetup))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какая погода сейчас?'), sendweather_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Погода в другом городе'), change_weather_city))
    bot.dispatcher.add_handler(CallbackQueryHandler(change_weather_city, pattern='^Погода в другом городе$'))
    bot.dispatcher.add_handler(MessageHandler(Filters.text, reply))

    bot.start_polling()
    bot.idle()

main()
