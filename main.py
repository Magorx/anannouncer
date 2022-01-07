#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from threading import Thread
from random import randint, choice, shuffle
from time import time, sleep
import logging
import message as Msg

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


MSGDB = Msg.MessageDB('messages.db', 'messages')


logging.basicConfig(format='[%(levelname)s]<%(name)s>{%(asctime)s} : %(message)s',
                    level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.start)


def help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help)


def help_recieve(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help_recieve)


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def msg_create(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.msg_create_err_one_arg)
        return
    
    code = context.args[0]
    msg = Msg.Message(code, time(), update.effective_user.name)
    MSGDB.add_msg(msg)

    reply = '{}\nCode: {}\nCreator: {}'.format(REPLY.msg_create_done, code, msg.info.user)

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


def msg_text(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.effective_user.send_message(REPLY.msg_text_err_no_args)
        return
    
    code = context.args[0]
    if not code in MSGDB.messages:
        update.effective_user.send_message(REPLY.msg_text_err_no_such_code)
        return
    
    msg = MSGDB.messages[code]

    text = update.message.text.split(' ')[1:]
    if text[0].count('\n') > 0:
        text[0] = '\n'.join(text[0].split('\n')[1:])
    else:
        del text[0]

    text = ' '.join(text)
    msg.text = text

    update.effective_user.send_message(REPLY.success)


def msg_date(update: Update, context: CallbackContext):
    pass


def msg_seal(update: Update, context: CallbackContext):
    pass


def msg_sign(update: Update, context: CallbackContext):
    pass


def recieve(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.msg_create_err_one_arg)
        return
    
    code = context.args[0]
    if not code in MSGDB.messages:
        update.effective_user.send_message(REPLY.msg_text_err_no_such_code)
        return

    msg = MSGDB.messages[code]
    update.effective_user.send_message(msg.text)


handlers = {
    'start' : start,
    'help'  : help,
    'help_recieve' : help_recieve,
    'recieve' : recieve,
    'msg_create' : msg_create,
    'msg_text' : msg_text
}

for handler in handlers:
    hldr = CommandHandler(handler, handlers[handler])
    dispatcher.add_handler(hldr)


updater.start_polling()

updater.idle()
