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

from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

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


def help_receive(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help_receive)


def help_msg(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=REPLY.help_msg)


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
    MSGDB.add(msg)

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
    
    msg.receive_info.timestamp ^= True

    update.effective_user.send_message(REPLY.success)


def msg_seal(update: Update, context: CallbackContext):
    msg = get_msg_to_change(update, context, 0)
    if not msg:
        return
    
    msg.receive_info.seal ^= True

    update.effective_user.send_message(REPLY.success)


def get_message_to_receive(update: Update, context: CallbackContext) -> Msg.Message:
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

    if (msg.receive_info.timestamp):
        if (reply):
            reply = reply + '\n-----\n'
        reply = reply + "This message was created on {}, time: {}".format(msg.info.date, msg.info.time)
    
    if (msg.receive_info.seal):
        if (reply):
            reply = reply + '\n-----\n'
        date, time = get_date_time()
        username = update.effective_user.name
        reply = reply + "_Unsealed by {} on {}, time: {}_".format(username, date, time)
    
    if len(reply):
        update.effective_user.send_message(reply, parse_mode=telegram.ParseMode.MARKDOWN)


def receive(update: Update, context: CallbackContext):
    msg = get_message_to_receive(update, context)
    if not msg:
        return

    if msg.receive_info.seal:
        update.effective_user.send_message(REPLY.msg_is_sealed)
        return

    show_message(update, context, msg)


def unseal(update: Update, context: CallbackContext):
    msg = get_message_to_receive(update, context)
    if not msg.receive_info.seal:
        update.effective_user.send_message(REPLY.msg_is_not_sealed)
        return
    
    show_message(update, context, msg)
    MSGDB.messages.pop(msg.code, None)

    reply = "The message with the code {} has just been unsealed by {}!".format(msg.code, update.effective_user.name)

    context.bot.send_message(chat_id=msg.creator_chat_id, text=reply)


def create_stream(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="This command requires one argument - the username of the listener.")
        return
    
    user_to = context.args[0]
    if user_to.startswith('@'):
        user_to = user_to[1:]

    if '@' in user_to:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The username of the listener cannot contain '@'.")
        return
    
    user_from = update.effective_user.name
    if user_from.startswith('@'):
        user_from = user_from[1:]
    
    # if user_from == user_to:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="You cannot listen to yourself.")
    #     return
    
    stream = Msg.MessageStream(user_from, user_to)
    MSGDB.add(stream)

    msg = ''
    msg += f'The stream has been created\n'
    msg += f'Code: {stream.code}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def stream_send(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="This command requires at least two arguments - the code of the stream and the message.")
        return
    
    code = context.args[0]
    if code.startswith('@'):
        code = code[1:]
    code = f'{update.effective_user.name[1:]}@{code}'

    stream = MSGDB.get(code)

    if not stream:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, no such stream.")
        return
    
    if not update.message.text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, no message text.")
        return
    
    text = update.message.text.split(' ')[1:]
    if text[0].count('\n') > 0:
        text[0] = '\n'.join(text[0].split('\n')[1:])
    else:
        del text[0]

    text = ' '.join(text)
    
    stream.add_msg(text)

    msg = ''
    msg += f'Sent!'

    # update stream msg
    stream_msg = stream.get_message_text()
    stream_keyboard = stream.get_message_keyboard()
    try:
        context.bot.edit_message_text(chat_id=stream.tg_chat, message_id=stream.tg_msg_id, text=stream_msg, reply_markup=stream_keyboard)
    except:
        pass

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def listen_stream(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="This command requires one argument - the code of the stream.")
        return
    
    code = context.args[0]
    if code.startswith('@'):
        code = code[1:]
    code = f'{code}{update.effective_user.name}'
    stream = MSGDB.get(code)

    if not stream:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, no such stream.")
        return

    msg = stream.get_message_text()
    keyboard = stream.get_message_keyboard()
    
    tg_msg = context.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=keyboard)

    stream.set_tg_msg(tg_msg)


def inline_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split('@')

    if data[0] == 'stream':
        stream = MSGDB.get(data[1] + '@' + data[2])
        if not stream:
            query.answer(text="Oops, no such stream.")
            return
        
        command = data[3]
        changed = False
        if command == 'next':
            stream.next()
        elif command == 'prev':
            stream.prev()
        else:
            query.answer(text="Oops, unknown command.")
            return
        
        msg = stream.get_message_text()
        keyboard = stream.get_message_keyboard()

        query.answer(text="")
        try:
            query.edit_message_text(text=msg, reply_markup=keyboard)
        except:
            pass
    else:
        query.answer(text="Oops, unknown command.")
    


handlers = {
    'start' : start,
    'help'  : help,
    'help_receive' : help_receive,
    'help_msg' : help_msg,
    'receive' : receive,
    'unseal' : unseal,
    'msg_create' : msg_create,
    'msg_text' : msg_text,
    'msg_date' : msg_date,
    'msg_seal' : msg_seal,

    'stream_create' : create_stream,
    'stream_send' : stream_send,
    'stream_listen' : listen_stream,
}

dispatcher.add_handler(CallbackQueryHandler(inline_callback))
for handler in handlers:
    hldr = CommandHandler(handler, handlers[handler])
    dispatcher.add_handler(hldr)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! Unknown command, try /help")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)


updater.start_polling()

updater.idle()
