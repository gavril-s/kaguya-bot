from re import S
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup
from pyowm import OWM
from pyowm.utils import config as cfg
import pymorphy2
from random import choice
import random
from datetime import date
import datetime
import time
from glob import glob
import io

WORDS = dict()
HOLIDAYS = dict()
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
GOOD_NIGHT = ['Споки)', 'Спокойной ночи <3', 'Сладких снов)', 'Буду ждать твоего сообщения завтра утром)', 'Споки ноки', 'Я тоже иду спать. До завтра',
              'Выспись хорошо. И не проспи будильник))']
GOOD_DAY = ['Привет!', 'Доброе утро! Я вот только проснулась)', 'Ку :3', 'Как настроение?', 'Охае', 'Шалом))0)', 'Э, салам алейкум, брат', 'Выспался?',
                'Приветик)', 'Надеюсь, ты хорошо поспал', 'Утречко)']
BYE = ['споки', 'спокойной ночи', 'а ну спать', 'до завтра', 'пока', 'сладких снов']
HI = ['привет', 'ку', 'здарова', 'доброе утро']
MONTH = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

MOODS = {}
MOOD_FADING = 0.681690113816

MORPH = pymorphy2.MorphAnalyzer()

WAITING_FOR_CITY = False
CITY = ''

def log(msg):
    print('-------------------------')
    print('MESSAGE: ', msg.text)
    print('USER: ', msg.from_user['first_name'])
    if msg.from_user['id'] in MOODS:
        print('MOOD: ', MOODS[msg.from_user['id']])
    else:
        print('MOOD: ', 0)
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

def norm_word(x):
    global MORPH
    p = MORPH.parse(x)[0]
    return p.normal_form

def compute_emo_rate(msg):
    del_list = '.,;!?:`()'
    p_msg = msg.strip().lower()
    trantab = p_msg.maketrans('', '', del_list)
    p_msg = p_msg.translate(trantab)

    if p_msg == 'прости':
        return 1

    msg_words = p_msg.split()
    rate = 0
    for word in msg_words:
        norm = norm_word(word)
        if norm in WORDS:
            rate += WORDS[norm]
    if len(msg_words) == 0:
        if ')' in msg and '(' not in msg:
            return 1
        else:
            return 0
    return rate / len(msg_words)

def sms(bot, update):
    log(bot.message)
    keyboard = ReplyKeyboardMarkup([['Скинь ножки', 'Какой сегодня день?'], ['Кто я сегодня?', 'Когда новый сезон?'], ['Какая погода сейчас?']], resize_keyboard=True)
    bot.message.reply_text('Охае, {}!'.format(bot.message.chat.first_name))
    time.sleep(1)
    bot.message.reply_text("Меня зовут Кагуя Синомия. Чем могу помочь?", reply_markup=keyboard)
    #update.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAADAgADOQADfyesDlKEqOOd72VKAg')

def reply(bot, update):
    log(bot.message)
    global CITY
    global WAITING_FOR_CITY
    if WAITING_FOR_CITY:
        CITY = bot.message.text
        WAITING_FOR_CITY = False
        sendweather(bot)
        return
    global MOODS
    global MOOD_FADING
    usr_id = bot.message.from_user['id']
    if usr_id not in MOODS:
        MOODS[usr_id] = 0
    MOODS[usr_id] = MOOD_FADING * MOODS[usr_id] + compute_emo_rate(bot.message.text)
    if random.random() <= 0.01:
        bot.message.reply_text('Когда ты мне пишешь...')
        time.sleep(1)
        bot.message.reply_text('Твоё сообщение')
        time.sleep(1)
        bot.message.reply_text('И я просто выхожу на хаха')
        time.sleep(1)
        bot.message.reply_text('Это так забавно мне')
        time.sleep(1)
        bot.message.reply_text('Я просто ссу себе в штаныыы')
        time.sleep(1)
        bot.message.reply_text('Ссу себе в штаны')
        time.sleep(1)
        bot.message.reply_text('Это невероятно')
    else:
        if bot.message.text.lower() in HI:
            rep = GOOD_DAY[random.randint(0, len(GOOD_DAY) - 1)]
        elif bot.message.text.lower() in BYE:
            rep = GOOD_NIGHT[random.randint(0, len(GOOD_NIGHT) - 1)]
        elif MOODS[usr_id] < 0:
            if '?' in bot.message.text:
                rep = NEGATIVE_QUIESTION_ANSWERS[random.randint(0, len(NEGATIVE_QUIESTION_ANSWERS) - 1)]
            else:
                rep = NEGATIVE_REPLIES[random.randint(0, len(NEGATIVE_REPLIES) - 1)]
        else:
            if '?' in bot.message.text:
                rep = POSITIVE_QUESTION_ANSWERS[random.randint(0, len(POSITIVE_QUESTION_ANSWERS) - 1)]
            else:
                rep = POSITIVE_REPLIES[random.randint(0, len(POSITIVE_REPLIES) - 1)]
        time.sleep(1)
        bot.message.reply_text(rep)

def whoami(bot, update):
    log(bot.message)
    global MOODS
    global MOOD_FADING
    usr_id = bot.message.from_user['id']
    if usr_id not in MOODS:
        MOODS[usr_id] = 0
    if MOODS[usr_id] < 0:
        rep = NEGATIVE_WHOAMI_REPLIES[random.randint(0, len(NEGATIVE_WHOAMI_REPLIES) - 1)]
    else:
        rep = POSITIVE_WHOAMI_REPLIES[random.randint(0, len(POSITIVE_WHOAMI_REPLIES) - 1)]
    time.sleep(1)
    bot.message.reply_text('{}, ты сегодня такой {}'.format(bot.message.chat.first_name, rep))

def sendlegs(bot, update):
    log(bot.message)
    global MOODS
    global MOOD_FADING
    usr_id = bot.message.from_user['id']
    if usr_id not in MOODS:
        MOODS[usr_id] = 0
    if MOODS[usr_id] < 0:
        rep = NEGATIVE_QUIESTION_ANSWERS[random.randint(0, len(NEGATIVE_QUIESTION_ANSWERS) - 1)]
        bot.message.reply_text(rep)
    else:
        list = glob('LEGS/*')
        pic = choice(list)
        time.sleep(1)
        bot.message.reply_text('Ну.... Хорошо')
        time.sleep(1)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
        time.sleep(1)
        bot.message.reply_text('Надеюсь, тебе понравилось)')

def when3season(bot, update):
    log(bot.message)
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
        time.sleep(1)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('NEWSEASON/notyet.png', 'rb'))
        time.sleep(1)
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
        time.sleep(1)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('NEWSEASON/out.png', 'rb'))
        time.sleep(1)
        bot.message.reply_text('А ну бегом смотреть')
        time.sleep(1)
        bot.message.reply_text('https://jut.su/kaguya-sama/')

def sendday(bot, update):
    log(bot.message)
    global MOODS
    global MOOD_FADING
    usr_id = bot.message.from_user['id']
    if usr_id not in MOODS:
        MOODS[usr_id] = 0
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

    time.sleep(1)
    update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
    time.sleep(1)
    bot.message.reply_text('Сегодня:\n' + HOLIDAYS[str(date.today().day) + ' ' + MONTH[date.today().month-1]])
    time.sleep(1)
    if MOODS[usr_id] < 0:
        rep = 'Хуёвого дня'
    else:
        rep = 'Хорошего дня'
    bot.message.reply_text('Это, кстати, {} {}. {}, {})'.format(date.today().day, MONTH[date.today().month-1], rep, bot.message.chat.first_name))

def weather(city: str):
    config_dict = cfg.get_default_config()
    config_dict['language'] = 'ru' 
    owm = OWM('b14672eeb4d058d2334c4b97a4c84aa0', config_dict)
    mgr = owm.weather_manager()
    obs = mgr.weather_at_place(city)
    weather = obs.weather
    temp = weather.temperature("celsius")
    detail = weather.detailed_status
    return temp, detail

def sendweather(bot):
    global WAITING_FOR_CITY
    global CITY
    if CITY == '':
        WAITING_FOR_CITY = True
        bot.message.reply_text('Напиши название города')
        return
    time.sleep(1)
    try:
        w = weather(CITY)
        bot.message.reply_text('В городе ' + CITY + ' сейчас ' + str(round(w[0]["temp"])) + '°C, ' + w[1])
    except Exception:
        bot.message.reply_text('А этот город вообще существует, дурачье?')
    CITY = ''

def sendweather_handler(bot, update):
    log(bot.message)
    sendweather(bot)

def main():
    read_words()
    read_holidays()
    bot = Updater("5260290537:AAGWg9J4a5dZDqsrq3MG3fejuBvD-0tasOA", use_context=True)
    bot.dispatcher.add_handler(CommandHandler('start', sms))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Кто я сегодня?'), whoami))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Скинь ножки'), sendlegs))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какой сегодня день?'), sendday))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Когда новый сезон?'), when3season))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какая погода сейчас?'), sendweather_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.text, reply))

    bot.start_polling()
    bot.idle()

main()