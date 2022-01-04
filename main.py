#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from threading import Thread
from random import randint, choice, shuffle
from time import time, sleep
import logging

import bot_replies as REPLY


TOKEN = open('token.tg', 'r').read()
print("TOKEN =", TOKEN)


from telegram.ext import Updater
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


logging.basicConfig(format='[%(levelname)s]<%(name)s>{%(asctime)s} : %(message)s',
                    level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.start)


def help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help)


def help_recieve(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help_recieve)


def msg_create(update: Update, context: CallbackContext):
    pass


def msg_text(update: Update, context: CallbackContext):
    pass


def msg_date(update: Update, context: CallbackContext):
    pass


def msg_seal(update: Update, context: CallbackContext):
    pass


def msg_sign(update: Update, context: CallbackContext):
    pass


handlers = {
    'start' : start,
    'help'  : help,
    'help_recieve' : help_recieve
}

for handler in handlers:
    hldr = CommandHandler(handler[0], handler[1])
    dispatcher.add_handler(hldr)


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)



updater.start_polling()

updater.idle()
