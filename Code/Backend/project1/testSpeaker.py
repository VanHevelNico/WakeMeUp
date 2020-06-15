# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os

import time
from datetime import datetime
import threading
from subprocess import check_output
from serial import Serial,PARITY_NONE

# Klasses
from RPi import GPIO
import spidev
from helpers.MCP3008 import MCP3008
from helpers.LCD import LCD
from helpers.SHIFTREGISTER import SHIFTREGISTER
from helpers.WS2801 import WS2801
import pygame
#Gpio
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

try:
    pygame.mixer.init()
    pygame.mixer.music.load("muziek/intro.mp3")
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(1.0)
    while pygame.mixer.music.get_busy() == True:
        continue
except KeyboardInterrupt as e:
    print(e)
finally:
    GPIO.cleanup()
    print('Stoppen')

