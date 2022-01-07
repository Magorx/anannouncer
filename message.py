#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pickle



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


class MessageDB:
    def __init__(self, filename=None, name='messages'):
        if (filename):
            try:
                self.load(filename)
                return
            except:
                pass
        
        self.name = name
        self.messages = {}
    

    def save(self):
        filename = self.name + '.db'
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
    

    def load(self, filename):
        with open(filename, 'rb') as file:
            self = pickle.load(file)
    
    
    def add_msg(self, message : Message):
        self.messages[message.code] = message

    