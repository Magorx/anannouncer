#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pickle
import threading
from time import sleep



class CreationInfo:
    def __init__(self, time, user):
        self.time = time
        self.user = user


class Message:
    def __init__(self, code='', time=None, creator=None):
        self.code = code
        self.text = ""
        self.info = CreationInfo(time, creator)


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

    