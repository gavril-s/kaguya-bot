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


WORDS = dict()    # словарь с эмоциональными окрасками
HOLIDAYS = dict() # праздники на каждый день
USERS = dict()    # пользователи

#############################
# Псевдо ИИ
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
GOOD_NIGHT = ['Споки)', 'Спокойной ночи <3', 'Сладких снов)', 'Буду ждать твоего сообщения завтра утром)', 'Споки ноки', 'Я тоже иду спать. До завтра',
              'Выспись хорошо. И не проспи будильник))']
GOOD_DAY = ['Привет!', 'Доброе утро! Я вот только проснулась)', 'Ку :3', 'Как настроение?', 'Охае', 'Шалом))0)', 'Э, салам алейкум, брат', 'Выспался?',
            'Приветик)', 'Надеюсь, ты хорошо поспал', 'Утречко)']

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
SLEEP_TIME = 0.5 # задержка в отправке сообщений, шобы на человека было похоже (в секундах)

MORPH = pymorphy2.MorphAnalyzer()
CONTROL_MSGS = dict() # контрольное сообщение, на которое можно ответить, если юзер нихуя не написал
                      # по-хорошему нужно исправить, так как это лютый костыль

def log(msg):
    print('-------------------------')
    print('MESSAGE: ', msg.text)
    print('USER: ', msg.from_user['first_name'])
    print('MOOD: ', USERS[get_id_bymsg(msg)]['mood'])
    print('-------------------------')

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

def read_users():
    global USERS
    try:
        f = io.open('users.json', mode='r', encoding='utf-8').read()
        USERS = json.loads(f)
        for id in USERS:
            if 'max_rating_pos_msgs' not in USERS[id]:
                USERS[id]['max_rating_pos_msgs'] = []
            if 'max_rating_neg_msgs' not in USERS[id]:
                USERS[id]['max_rating_neg_msgs'] = []
            if 'top_messages' not in USERS[id]:
                USERS[id]['top_messages'] = dict()
    except Exception:
        f = io.open('users.json', mode='w', encoding='utf-8')
        f.write('{}')
        USERS = dict()
    print(USERS)

def write_users():
    f = io.open('users.json', mode='w', encoding='utf-8')
    json_string = json.dumps(USERS)
    f.write(json_string)

def register_user(msg): # пажилая регистрация...
    global USERS
    id = str(msg.from_user['id'])
    first_name = msg.from_user['first_name']
    last_name = msg.from_user['last_name']
    username = msg.from_user['username']
    USERS[id] = {
        'first_name' : first_name,
        'last_name' : last_name,
        'username': username,
        'mood' : 0,
        'city' : '',
        'waiting_for_city' : False,
        'msg_count' : 0,
        'pics_unlocked' : 0,
        'pics': [False] * len(glob('LEGS/*')),
        'max_rating_pos_msgs': [],
        'max_rating_neg_msgs': [],
        'top_messages': dict() # топ сообщений челика
    }

def check_registration(bot):
    usr_id = get_id(bot)
    if usr_id not in USERS:
        register_user(msg) # тут хуйня написана, но трогать лень
        print('NEW USER: ', USERS[usr_id])

def check_registration_bymsg(msg):
    usr_id = get_id_bymsg(msg)
    if usr_id not in USERS:
        register_user(msg)
        print('NEW USER: ', USERS[usr_id])

def get_id(bot):
    return str(bot.effective_user['id'])

def get_id_bymsg(msg):
    return str(msg.from_user['id'])

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
    res += 'Настроение твоей Кагуи: ' + f"{USERS[usr_id]['mood']:.2f}" + '\n'
    return res

def get_admin_stat(usr_id): # выдаёт админам личные данные пользователей
    res = 'username: @' + USERS[usr_id]['username'] + '\n' + 'Имя: ' + USERS[usr_id]['first_name']
    if USERS[usr_id]['last_name'] != None:
        res += ' ' + USERS[usr_id]['last_name']
    res += '\n-----------------------------------------\n'
    res += 'Отправлено сообщений: ' + str(USERS[usr_id]['msg_count']) + '\n'
    res += 'Картинок открыто: ' + str(USERS[usr_id]['pics_unlocked']) + '/' + str(len(glob('LEGS/*'))) + '\n'
    res += 'Настроение: ' + f"{USERS[usr_id]['mood']:.2f}" + '\n'
    return res


#############################
# А ВОТ ТУТ УЖЕ РЕАЛ БОТИК

def sms(bot, update): # отвечает на /start
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    keyboard = ReplyKeyboardMarkup([['Скинь ножки', 'Какой сегодня день?'], ['Кто я сегодня?', 'Когда новый сезон?'], ['Какая погода сейчас?']], resize_keyboard=True)
    bot.message.reply_text('Охае, {}!'.format(bot.message.chat.first_name))
    time.sleep(SLEEP_TIME)
    bot.message.reply_text("Меня зовут Кагуя Синомия. Чем могу помочь?", reply_markup=keyboard)
    #update.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAADAgADOQADfyesDlKEqOOd72VKAg')
    write_users()

def help_user(bot, update): # отвечает на /help
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    bot.message.reply_text('Помоги себе сам, ёпта')
    write_users()    

def stat(bot, update): # отвечает на /stat
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False

    if usr_id in ADMINS_ID:
        for u in USERS:
            bot.message.reply_text(get_admin_stat(u))
    else:
        bot.message.reply_text(get_stat(usr_id))
    write_users()

def reply(bot, update): # ответ на обычное сообщение
    global USERS
    global MOOD_FADING
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['city'] = bot.message.text
        USERS[usr_id]['waiting_for_city'] = False
        sendweather(bot, update)
        return
    emo_rate = compute_emo_rate(bot.message.text)
    USERS[usr_id]['mood'] = MOOD_FADING * USERS[usr_id]['mood'] + emo_rate
    if -0.1 < USERS[usr_id]['mood'] < 0 and emo_rate >= 0: # если Кагуя не сильно злится, а чел не сильно злит
        USERS[usr_id]['mood'] = 0                          # прощаем ему всю хуйню
    log(bot.message)
    if bot.message.text == QUIT_TEXT and usr_id in ADMINS_ID:
        quit()
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
        if is_why:
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
            rep = GOOD_DAY[random.randint(0, len(GOOD_DAY) - 1)]
        elif bot.message.text.lower() in BYE:
            rep = GOOD_NIGHT[random.randint(0, len(GOOD_NIGHT) - 1)]
        elif bot.message.text.lower() in WHATSUP_QUESTIONS:
            if USERS[usr_id]['mood'] < 0:
                rep = NEGATIVE_WAHATSUP_ANSWERS[random.randint(0, len(NEGATIVE_WAHATSUP_ANSWERS) - 1)]
            else:
                rep = POSITIVE_WAHATSUP_ANSWERS[random.randint(0, len(POSITIVE_WAHATSUP_ANSWERS) - 1)]
        elif USERS[usr_id]['mood'] < 0:
            if '?' in bot.message.text:
                rep = NEGATIVE_QUIESTION_ANSWERS[random.randint(0, len(NEGATIVE_QUIESTION_ANSWERS) - 1)]
            else:
                if random.random() <= REPLY_WITH_USR_MSG and len(USERS[usr_id]['top_messages']) > 0:
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
                if random.random() <= REPLY_WITH_USR_MSG and len(USERS[usr_id]['top_messages']) > 0:
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
    if msg not in USERS[usr_id]['top_messages'] and msg != 'Кагуя':
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
            'rating' : 1,
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
    else:
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
    write_users()

def whoami(bot, update): # отвечает на "Кто я сегодня?"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    if USERS[usr_id]['mood'] < 0:
        rep = NEGATIVE_WHOAMI_REPLIES[random.randint(0, len(NEGATIVE_WHOAMI_REPLIES) - 1)]
    else:
        rep = POSITIVE_WHOAMI_REPLIES[random.randint(0, len(POSITIVE_WHOAMI_REPLIES) - 1)]
    time.sleep(SLEEP_TIME)
    bot.message.reply_text('{}, ты сегодня такой {}'.format(bot.message.chat.first_name, rep))
    write_users()

def sendlegs(bot, update): # отвечает на "Скинь ножки"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
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
    write_users()
        

def when3season(bot, update): # отвечает на "Когда третий сезон?"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
    now = date.today()
    ser_1 = date(2022, 4, 9)
    ser_2 = date(2022, 4, 16)
    ser_3 = date(2022, 4, 23)
    ser_4 = date(2022, 4, 30)
    ser_5 = date(2022, 5, 7)
    ser_6 = date(2022, 5, 14)
    ser_7 = date(2022, 5, 21)
    ser = 0
    if ser_1 > now:
        bot.message.reply_text('Блин, нового сезона еще нет(')
        time.sleep(SLEEP_TIME)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('NEWSEASON/notyet.png', 'rb'))
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('Но как только он выйдет, я обязательно тебе сообщу)')
    else:
        if ser_7 <= now:
            ser = 7
        elif ser_6 <= now:
            ser = 6
        elif ser_5 <= now:
            ser = 5
        elif ser_4 <= now:
            ser = 4
        elif ser_3 <= now:
            ser = 3
        elif ser_2 <= now:
            ser = 2
        elif ser_1 <= now:
            ser = 1

        bot.message.reply_text('Ура, вышла серия {}!'.format(ser))
        time.sleep(SLEEP_TIME)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('NEWSEASON/out.png', 'rb'))
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('А ну бегом смотреть')
        time.sleep(SLEEP_TIME)
        bot.message.reply_text('https://jut.su/kaguya-sama/')
    write_users()

def sendday(bot, update): # отвечает на "Какой сегодня день?"
    global USERS
    usr_id = get_id_bymsg(bot.message)
    check_registration_bymsg(bot.message)
    log(bot.message)
    USERS[usr_id]['msg_count'] += 1
    if USERS[usr_id]['waiting_for_city']:
        USERS[usr_id]['waiting_for_city'] = False
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
    except Exception:
        rep = 'А этот город вообще существует, дурачье?'
        USERS[usr_id]['city'] = ''
    CONTROL_MSGS[get_id(bot)].reply_text(rep, reply_markup=reply_markup)    
    write_users()

def sendweather_handler(bot, update): # вызывается при вопросе про погоду, имба функция
    sendweather(bot, update)

def main(): # БАЗА
    read_words()
    read_holidays()
    read_users()
    bot = Updater("5260290537:AAGWg9J4a5dZDqsrq3MG3fejuBvD-0tasOA", use_context=True)
    bot.dispatcher.add_handler(CommandHandler('start', sms))
    bot.dispatcher.add_handler(CommandHandler('help', help_user))
    bot.dispatcher.add_handler(CommandHandler('stat', stat))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Кто я сегодня?'), whoami))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Скинь ножки'), sendlegs))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какой сегодня день?'), sendday))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Когда новый сезон?'), when3season))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какая погода сейчас?'), sendweather_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Погода в другом городе'), change_weather_city))
    bot.dispatcher.add_handler(CallbackQueryHandler(change_weather_city, pattern='^Погода в другом городе$'))
    bot.dispatcher.add_handler(MessageHandler(Filters.text, reply))

    bot.start_polling()
    bot.idle()

main()