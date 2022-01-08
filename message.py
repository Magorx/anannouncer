#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pickle
import threading
from time import sleep



class CreationInfo:
    def __init__(self, time, date, user):
        self.time = time
        self.date = date
        self.user = user


class RecieveInfo:
    def __init__(self):
        self.timestamp = False
        self.seal = False


class Message:
    def __init__(self, code='', time=None, date=None, creator=None, creator_chat_id=None):
        self.code = code
        self.text = ""
        self.info = CreationInfo(time, date, creator)
        self.recieve_info = RecieveInfo()

        self.creator_chat_id = creator_chat_id
    

    def is_changeable(self) -> bool:
        return not self.recieve_info.seal


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
    
    
    def add_msg(self, message : Message):
        self.messages[message.code] = message

    