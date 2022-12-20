#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pickle
import threading
from time import sleep


from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton


class CreationInfo:
    def __init__(self, time, date, user):
        self.time = time
        self.date = date
        self.user = user


class receiveInfo:
    def __init__(self):
        self.timestamp = False
        self.seal = False


class Message:
    def __init__(self, code='', time=None, date=None, creator=None, creator_chat_id=None):
        self.code = code
        self.text = ""
        self.info = CreationInfo(time, date, creator)
        self.receive_info = receiveInfo()

        self.creator_chat_id = creator_chat_id
    

    def is_changeable(self) -> bool:
        return not self.receive_info.seal


    def save(self, filename=None):
        strcode = str(self.code)

        if not filename:
            filename = strcode + '.msg'
        
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
    

    def load(self, filename):
        with open(filename, 'rb') as file:
            self = pickle.load(file)


def timed_save(obj, sec_timer=5):
    while True:
        obj.save()
        sleep(sec_timer)


class MessageDB:
    def __init__(self, filename=None, name='messages'):
        if (filename):
            try:
                self.load(filename)
                self.init_backup_thread()
                return
            except:
                pass
        
        self.name = name
        self.messages = {}
        self.init_backup_thread()


    def init_backup_thread(self):
        thread = threading.Thread(target=timed_save, args=(self,))
        thread.start()
    

    def save(self):
        filename = self.name + '.db'
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
    

    def load(self, filename):
        with open(filename, 'rb') as file:
            me = pickle.load(file)
            self.name = me.name
            self.messages = me.messages
    
    
    def add(self, message : Message):
        self.messages[message.code] = message
    
    def get(self, code):
        if code in self.messages:
            return self.messages[code]
        else:
            return None


class MessageStream:
    def __init__(self, user_from, user_to):
        self.user_from = user_from
        self.user_to = user_to
        self.messages = []

        self.cur_message_index = 0

        self.code = user_from + '@' + user_to
        self.tg_msg_id = None

    def add_msg(self, message):
        self.messages.append(message)
    

    def get_cur_msg(self):
        if self.cur_message_index < len(self.messages):
            return self.messages[self.cur_message_index]
        else:
            return None

    def next(self):
        if self.cur_message_index < len(self.messages) - 1:
            self.cur_message_index += 1
            return True
        else:
            return False
    
    def prev(self):
        if self.cur_message_index > 0:
            self.cur_message_index -= 1
            return True
        else:
            return False

    def set_tg_msg(self, msg):
        self.tg_msg_id = msg.message_id
        self.tg_chat = msg.chat.id


    def get_message_text(self):
        msg = f'Steam of @{self.user_from}\n'
        msg += f'Message: {self.cur_message_index + 1}/{len(self.messages)}\n'
        msg += '-----\n'
        cur_msg = self.get_cur_msg()
        if cur_msg:
            msg += cur_msg
        else:
            msg += 'No more messages'
        
        return msg
    
    def get_message_keyboard(self):
        prefix = f'stream@{self.code}@'
        inline_keyboard = [[
            InlineKeyboardButton("prev", callback_data=prefix+'prev'),
            InlineKeyboardButton("next", callback_data=prefix+'next'),
        ]]
        
        return InlineKeyboardMarkup(inline_keyboard)
