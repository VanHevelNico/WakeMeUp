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

#Gpio
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# GPIO PINNEN
#LCD
rs = 19
E = 26
#shiftregister
ds = 16 
oe = 25
st_cp = 24
sh_cp = 23
mr = 18
#WS2801
sda = 21
clk = 20
#Klok
vorige_tijd = 0000
#Seriele communicatie
ser = Serial('/dev/ttyS0', 115200, bytesize=8, parity=PARITY_NONE, stopbits=1)

#SPI openen
spi = spidev.SpiDev()

#Objecten van klasses
mcp = MCP3008(spi)
shift = SHIFTREGISTER(ds,sh_cp,st_cp,mr,oe)
lcd= LCD(E,rs,shift)
ledstrip = WS2801(sda,clk,15)


#FLASK
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

#Programmma variabelen
delay = 60

#Acties
def setup():
    shift.setup()
    lcd.setup()
    #Shift register aanzetten
    shift.init_shift_register()
    #LCD Aanzetten
    lcd.init_lcd()
    ledstrip.setup()
    

def initialLCD():
    ips = check_output(['hostname', '--all-ip-addresses'])
    adressen = str(ips)
    adressen = adressen.replace("n", "")
    adressen = adressen.replace("b", "")
    adressen = "IP:" + adressen
    print(adressen)
    lcd.send_instruction_lcd(1)
    lcd.write_message(adressen)
    print("Lcd opgestart")

try:
    setup()
    initialLCD()
    while True:
        ledstrip.kleur(15,0.01,255)
except KeyboardInterrupt as e:
    print(e)
finally:
    ledstrip.allesUit(15)
    GPIO.cleanup()
    print('Stoppen')

