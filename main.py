#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from threading import Thread
from random import randint, choice, shuffle
from time import time, sleep
import logging
import telegram

from telegram.ext.defaults import Defaults
import message as Msg
import datetime

import bot_replies as REPLY


TOKEN = open('token.tg', 'r').read()
print("TOKEN =", TOKEN)


from telegram.ext import Updater
from telegram import Update, user
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


MSGDB = Msg.MessageDB('messages.db', 'messages')


logging.basicConfig(format='[%(levelname)s]<%(name)s>{%(asctime)s} : %(message)s',
                    level=logging.INFO)



def get_date_time():
    now = datetime.datetime.now()
    time = now.time().strftime("%H:%M:%S")
    date = now.date().strftime("%d-%m-%Y")
    return (date, time)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.start)


def help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help)


def help_recieve(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help_recieve)


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def get_msg_to_change(update: Update, context: CallbackContext, opts_cnt) -> Msg.Message:
    if len(context.args) < 1 + opts_cnt:
        update.effective_user.send_message(REPLY.msg_err_no_args)
        return None
    
    code = context.args[0]
    username = update.effective_user.name[1:]
    code = username + '@' + code

    if not code in MSGDB.messages:
        update.effective_user.send_message(REPLY.msg_text_err_no_such_code)
        return None
    
    msg = MSGDB.messages[code]
    if not msg.is_changeable():
        update.effective_user.send_message(REPLY.msg_cant_be_changed)
        return None
    
    return msg


def msg_create(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.msg_create_err_one_arg)
        return

    code = context.args[0]
    if '@' in code:
        context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.msg_create_err_no_sep_symb)
        return
    
    username = update.effective_user.name[1:]
    code = username + '@' + code

    time, date = get_date_time()

    msg = Msg.Message(code, time=time, date=date, creator=username, creator_chat_id=update.effective_chat.id)
    MSGDB.add_msg(msg)

    reply = '{}\nCode: {}\nTime: {}\nDate: {}'.format(REPLY.msg_create_done, code, time, date)

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


def msg_text(update: Update, context: CallbackContext):
    msg = get_msg_to_change(update, context, 0)
    if not msg:
        return


    text = update.message.text.split(' ')[1:]
    if text[0].count('\n') > 0:
        text[0] = '\n'.join(text[0].split('\n')[1:])
    else:
        del text[0]

    text = ' '.join(text)
    msg.text = text

    update.effective_user.send_message(REPLY.success)


def msg_date(update: Update, context: CallbackContext):
    msg = get_msg_to_change(update, context, 0)
    if not msg:
        return
    
    msg.recieve_info.timestamp ^= True

    update.effective_user.send_message(REPLY.success)


def msg_seal(update: Update, context: CallbackContext):
    msg = get_msg_to_change(update, context, 0)
    if not msg:
        return
    
    msg.recieve_info.seal ^= True

    update.effective_user.send_message(REPLY.success)


def get_message_to_recieve(update: Update, context: CallbackContext) -> Msg.Message:
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.msg_create_err_one_arg)
        return None
    
    code = context.args[0]
    if not code in MSGDB.messages:
        update.effective_user.send_message(REPLY.msg_text_err_no_such_code)
        return None
    
    msg = MSGDB.messages[code]
    return msg


def show_message(update: Update, context: CallbackContext, msg: Msg.Message):
    if not msg.text:
        update.effective_user.send_message("The message is empty.")
        update.effective_user.send_message("_This additional message is a proof of real emptiness_", parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        update.effective_user.send_message(msg.text)

    reply = ""

    if (msg.recieve_info.timestamp):
        if (reply):
            reply = reply + '\n-----\n'
        reply = reply + "This message was created on {}, time: {}".format(msg.info.date, msg.info.time)
    
    if (msg.recieve_info.seal):
        if (reply):
            reply = reply + '\n-----\n'
        date, time = get_date_time()
        username = update.effective_user.name
        reply = reply + "Unsealed by {} on {}, time: {}".format(username, date, time)
    
    if len(reply):
        update.effective_user.send_message(reply)


def recieve(update: Update, context: CallbackContext):
    msg = get_message_to_recieve(update, context)
    print(msg.__dict__)
    if msg.recieve_info.seal:
        update.effective_user.send_message(REPLY.msg_is_sealed)
        return

    show_message(update, context, msg)


def unseal(update: Update, context: CallbackContext):
    msg = get_message_to_recieve(update, context)
    if not msg.recieve_info.seal:
        update.effective_user.send_message(REPLY.msg_is_not_sealed)
        return
    
    show_message(update, context, msg)
    MSGDB.messages.pop(msg.code, None)

    reply = "The message with the code {} has just been unsealed by {}!".format(msg.code, update.effective_user.name)

    context.bot.send_message(chat_id=msg.creator_chat_id, text=reply)


handlers = {
    'start' : start,
    'help'  : help,
    'help_recieve' : help_recieve,
    'recieve' : recieve,
    'unseal' : unseal,
    'msg_create' : msg_create,
    'msg_text' : msg_text,
    'msg_date' : msg_date,
    'msg_seal' : msg_seal
}

for handler in handlers:
    hldr = CommandHandler(handler, handlers[handler])
    dispatcher.add_handler(hldr)


updater.start_polling()

updater.idle()
