#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from threading import Thread
from random import randint, choice, shuffle
from time import time, sleep


TOKEN = open('token.tg', 'r').read()
print("TOKEN =", TOKEN)

