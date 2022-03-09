from tkinter import NE
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup
from glob import glob
import time
from random import choice
import random
import datetime

WORDS = dict()
POSITIVE_REPLIES = ['Хорошо, сенпаи^^','Да, согласна)','Ты такой милашка','Ага)','Хорошо)', 'Desu-desu :3']
NEGATIVE_REPLIES = ['Чеел','Иди нахуй','Эмм','Лол', 'Не пиши сюда больше, бака']

def read_words():
    f = open('words.txt', 'r')
    for line in f:
        tmp = line.split()
        WORDS[tmp[0]] = int(tmp[1])
    f.close()


def compute_emo_rate(msg):
    del_list = '.,;!?:`'
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
    keyboard = ReplyKeyboardMarkup([['Скинь ножки', 'Какой сегодня день?'], ['Кто я сегодня?']])
    bot.message.reply_text('Охае, {}!'.format(bot.message.chat.first_name))
    time.sleep(1)
    bot.message.reply_text("Меня зовут Кагуя Синомия. Чем могу помочь?", reply_markup=keyboard)


def reply(bot, update):
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


def main():
    read_words()
    bot = Updater("5260290537:AAFKwTweXBj02R7Y2Fog6nu6nU9obCIEnn8", use_context=True)
    bot.dispatcher.add_handler(CommandHandler('start', sms))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Кто я сегодня?'), whoami))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Скинь ножки'), sendlegs))
    bot.dispatcher.add_handler(MessageHandler(Filters.regex('Какой сегодня день?'), sendday))
    bot.dispatcher.add_handler(MessageHandler(Filters.text, reply))

    bot.start_polling()
    bot.idle()


main()