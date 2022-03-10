from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup
from glob import glob
import time
from random import choice
import random
from datetime import date
import datetime
from pyowm import OWM
from pyowm.utils import config as cfg

WORDS = dict()
POSITIVE_REPLIES = ['Хорошо, сенпай^^','Да, согласна)','Ты такой милашка','Ага)','Хорошо)', 'Desu-desu :3']
NEGATIVE_REPLIES = ['Чеел','Иди нахуй','Эмм','Лол', 'Не пиши сюда больше, бака']

def read_words():
    f = open('words.txt', 'r')
    for line in f:
        tmp = line.split()
        if tmp[1] != '0':
            WORDS[tmp[0]] = int(tmp[1])
    f.close()

def compute_emo_rate(msg):
    del_list = '.,;!?:`()'
    p_msg = msg.strip().lower()
    trantab = p_msg.maketrans('', '', del_list)
    p_msg = p_msg.translate(trantab)

    msg_words = p_msg.split()
    rate = 0
    for word in msg_words:
        if word in WORDS:
            rate += WORDS[word]
    return rate

def sms(bot, update):
    print(bot.message.text)
    keyboard = ReplyKeyboardMarkup([['Скинь ножки', 'Какой сегодня день?'], ['Кто я сегодня?', 'Когда новый сезон?'], ['Какая погода сейчас?']])
    bot.message.reply_text('Охае, {}!'.format(bot.message.chat.first_name))
    time.sleep(1)
    bot.message.reply_text("Меня зовут Кагуя Синомия. Чем могу помочь?", reply_markup=keyboard)
    #update.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAADAgADOQADfyesDlKEqOOd72VKAg')

def reply(bot, update):
    if random.random() <= 0.05:
        bot.message.reply_text('Когда ты мне пишешь...')
        time.sleep(1)
        bot.message.reply_text('Твоё сообщение')
        time.sleep(1)
        bot.message.reply_text('И я просто выхожу на хаха')
        time.sleep(1)
        bot.message.reply_text('Я просто ссу себе в штаныыы')
        time.sleep(1)
        bot.message.reply_text('Ссу себе в штаны')
        time.sleep(1)
        bot.message.reply_text('Это невероятно')
    else:
        if compute_emo_rate(bot.message.text) < 0:
            rep = NEGATIVE_REPLIES[random.randint(0, len(NEGATIVE_REPLIES) - 1)]
        else:
            rep = POSITIVE_REPLIES[random.randint(0, len(POSITIVE_REPLIES) - 1)]
        print(bot.message.text)
        time.sleep(1)
        bot.message.reply_text(rep)


def whoami(bot, update):
    print(bot.message.text)
    replys = ["долбаеб", "сын шалавы ебаной", 'уебан сраный', 'гандон штопаный', 'ублюдок недоебаный', 'блядский мудак',
              'пидорас', 'уёбак', 'конченный хуесос', 'дифичент ебаный', 'хуепутало']
    rep = replys[random.randint(0, len(replys) - 1)]
    time.sleep(1)
    bot.message.reply_text('{}, ты сегодня такой {}'.format(bot.message.chat.first_name, rep))


def sendlegs(bot, update):
    print(bot.message.text)
    list = glob('LEGS/*')
    pic = choice(list)
    time.sleep(1)
    bot.message.reply_text('Ну.... Хорошо')
    time.sleep(1)
    update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
    time.sleep(1)
    bot.message.reply_text('Надеюсь, тебе понравилось)')

def when3season(bot, update):
    print(bot.message.text)
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
        bot.message.reply_text('Но как только он выйдет, я обязательно тебе сообщу')
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

        bot.message.reply_text('Ура, вышла серия {}'.format(ser))
        time.sleep(1)
        update.bot.send_photo(chat_id=bot.message.chat.id, photo=open('NEWSEASON/out.png', 'rb'))
        time.sleep(1)
        bot.message.reply_text('А ну бегом смотреть')
        time.sleep(1)
        bot.message.reply_text('https://jut.su/kaguya-sama/')

def sendday(bot, update):
    print(bot.message.text)
    bot.message.reply_text('Хммм, дай-ка подумать')
    pic = 0
    if datetime.datetime.today().weekday() == 0:
        pic = 'DAY/monday.jpg'
    elif datetime.datetime.today().weekday() == 1:
        pic = 'DAY/tuesday.jpg'
    elif datetime.datetime.today().weekday() == 2:
        pic = 'DAY/wednesday.jpg'
    elif datetime.datetime.today().weekday() == 3:
        pic = 'DAY/thursday.jpg'
    elif datetime.datetime.today().weekday() == 4:
        pic = 'DAY/friday.jpg'
    elif datetime.datetime.today().weekday() == 5:
        pic = 'DAY/saturday.jpg'
    elif datetime.datetime.today().weekday() == 6:
        pic = 'DAY/sunday.jpg'
    time.sleep(1)
    update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(pic, 'rb'))
    time.sleep(1)
    bot.message.reply_text('Хорошего дня, {})'.format(bot.message.chat.first_name))

def getlocation(lat, lon):
    url = f"https://yandex.ru/pogoda/moscow?lat={lat}&lon={lon}"
    return url

def weather(city: str):
    config_dict = cfg.get_default_config()
    config_dict['language'] = 'ru' 
    owm = OWM('b14672eeb4d058d2334c4b97a4c84aa0', config_dict)
    mgr = owm.weather_manager()
    obs = mgr.weather_at_place(city)
    weather = obs.weather
    loc = getlocation(obs.location.lat, obs.location.lon)
    temp = weather.temperature("celsius")
    return temp, loc

def sendweather(bot, update):
    #bot.message.reply_text('Напиши название города')
    time.sleep(1)
    city = 'Москва'#bot.message.text
    #try:
    w = weather(city)
    bot.message.reply_text('В городе ' + city + ' сейчас  ' + str(round(w[0]["temp"])) + '° C')
    #except Exception:
    #    bot.message.reply_text('А этот город вообще существует, дурачье?')

def main():
    read_words()
    bot = Updater("5260290537:AAGWg9J4a5dZDqsrq3MG3fejuBvD-0tasOA", use_context=True)
    bot.dispatcher.add_handler(CommandHandler('start', sms))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Кто я сегодня?'), whoami))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Скинь ножки'), sendlegs))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какой сегодня день?'), sendday))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Когда новый сезон?'), when3season))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какая погода сейчас?'), sendweather))
    bot.dispatcher.add_handler(MessageHandler(Filters.text, reply))

    bot.start_polling()
    bot.idle()

main()