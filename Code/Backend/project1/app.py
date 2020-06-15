from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import json
import time
#from datetime import datetime
import datetime 
from datetime import timedelta  
import threading
from subprocess import check_output
from serial import Serial,PARITY_NONE
import pygame

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

#Variabel licht
statusLicht = "uit"
wekkerAan = 0

#Acties
def setup():
    shift.setup()
    lcd.setup()
    #Shift register aanzetten
    shift.init_shift_register()
    #LCD Aanzetten
    lcd.init_lcd()
    ledstrip.setup()

def getTemp():
    while True:
        volts = mcp.read_channel(0)
        temp = ((volts * 460) / float(1023)) - 50
        temp = round(temp, 1)
        vandaag = datetime.datetime.now()
        vandaag = vandaag.strftime('%Y-%m-%d %H:%M:%S')
        #print(vandaag)
        DataRepository.insert_meting(temp,vandaag,1,1)
        temp = DataRepository.read_sensor_by_id(1,1)
        #print(temp)
        socketio.emit('B2F_temperatuur', temp,broadcast=True)
        time.sleep(delay)

def getTempGrafiek():
    while True:
        s = DataRepository.read_temperaturen(1,1)
        socketio.emit('B2F_grafiek', s,broadcast=True)    
        time.sleep(delay)

def statusLight():
    global statusLicht
    while True:
        s = DataRepository.read_status_lamp(1)
        socketio.emit('B2F_statusLamp',s,broadcast=True)
        #print(s)
        #print(s["status"])
        if(statusLicht != s["status"]):
            statusLicht = s["status"]
        time.sleep(1)

def lichtAanpassen():
    global statusLicht
    global wekkerAan
    while wekkerAan == 0:
        lichten(statusLicht)
        time.sleep(0.1)

def checkAlarm():
    while True:
        global wekkerAan
        #Checken welke alarmen aanstaan
        #Checken welke dag we zijn (maandag, dinsda,...)
        #Checken of het alarm vandaag al is geweest
        #Als de dag klopt en het uur is gepasseerd maar het alarm is nog niet geweest -> laten afgaan

        #Dag van vandaag ophalen
        vandaag = datetime.datetime.today()
        dag = vandaag.weekday()
        uur = vandaag.strftime("%H:%M")
        vandaag = vandaag.strftime('%Y-%m-%d 00:00:00')
        #Wekkers ophalen die aanstaan
        s = DataRepository.read_alarmen_aan(1,vandaag)
        #print(s)
        for alarm in s:
            #Elke alarm wordt apart opgehaald.
            #De alarm["herhaling"] is een string met 7 cijfers in 1=afgaan 0=uit De dag is de index waarde
            p = alarm["herhaling"]
            idAlarm = alarm["idAlarm"]
            tijdstip = alarm["tijdstip"]
            #print(tijdstip)
            tijdstip = datetime.datetime.strptime(tijdstip, '%H:%M')
            tijdstip = tijdstip + timedelta(seconds=300)  
            tijdstip = tijdstip.strftime("%H:%M")
            #print(str(tijdstip))
            #Als de dag een 1 heeft moet de wekker vandaag afgaan
            if(int(p[dag]) == 1):
                #Kijken hoelaat het is en kijken of het uur al gepasseerd is
                if(uur > alarm["tijdstip"] and uur < str(tijdstip)):
                    print(wekkerAan)
                    if(wekkerAan == 0):
                        #Het uur is net gepasseerd dus alarm laten afgaan
                        print("Alarm laten afgaan")
                        #Muziek afspelen
                        print(alarm["deuntje"])
                        licht = alarm["lichteffect"]
                        liedje = alarm["deuntje"]
                        liedje = "muziek/" + liedje
                        #Juiste leds laten aangaan
                        pygame.mixer.init()
                        pygame.mixer.music.set_volume(1.0)    
                        pygame.mixer.music.load(liedje)
                        pygame.mixer.music.play(50)                      
                        while mcp.read_channel(2) > 1000:
                            wekkerAan = 1
                            lichten(licht)
                            #print(mcp.read_channel(2))
                        print("Uitzetten")
                        wekkerAan = 0
                        ledstrip.allesUit(15)
                        pygame.mixer.music.stop()
                        DataRepository.update_alarm_uit(vandaag,idAlarm)

        time.sleep(1)

def lichten(licht):
    if(licht == "flikker"):
        ledstrip.flikker(15,0.5,255)
    elif(licht == "kleur"):
        ledstrip.kleur(15,0.5,255)
    elif(licht == "gewoon"):
        ledstrip.gewoon(15,0.5,255)
    else:
        ledstrip.allesUit(15)

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

def read_serialport():
    global ser
    recv_mesg = ser.readline()
    recv_mesg = str(recv_mesg,encoding='utf-8')
    if(recv_mesg != ""):
        print(recv_mesg)

def tijd_sturen():
    while True:
        global vorige_tijd
        nu = datetime.datetime.now()
        tijd = nu.strftime("%H%M")
        if tijd != vorige_tijd:
            ser.write(tijd.encode(encoding="utf-8"))  
            read_serialport()
            vorige_tijd = tijd
        time.sleep(1)

#Threading


#API ENDPOINTS
endpoint = '/api'

@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route(endpoint + '/alarmen', methods=['GET','POST'])
def get_alarmen():
    if request.method == 'GET':
        s = DataRepository.read_alarmen(1)
        return jsonify(s), 200
    elif request.method == 'POST':
        gegevens = DataRepository.json_or_formdata(request)
        tijdstip = gegevens["tijdstip"]
        tijdstip = "2020-01-01 " +tijdstip+":00"
        print(tijdstip)
        data = DataRepository.insert_alarm(gegevens["titel"], tijdstip, gegevens["herhaling"], gegevens["lichteffect"], gegevens["deuntje"], gegevens["wekkerID"], gegevens["status"], gegevens["kleur"], gegevens["kleurLedstrip"])
        if data is not None:
            if data > 0:
                return jsonify(status="success"), 200
            else:
                return jsonify(status=data), 204
        else:
            return jsonify(status="error"), 404        

@app.route(endpoint + '/alarmen/update', methods=['PUT'])
def update_alarmen():
    if request.method == 'PUT':
        gegevens = DataRepository.json_or_formdata(request)
        tijdstip = gegevens["tijdstip"]
        tijdstip = "2020-01-01 " +tijdstip+":00"
        print(tijdstip)
        data = DataRepository.update_alarm_alles(gegevens["titel"], tijdstip, gegevens["herhaling"], gegevens["lichteffect"], gegevens["deuntje"], gegevens["status"], gegevens["kleur"], gegevens["kleurLedstrip"], gegevens["idAlarm"])
        if data is not None:
            if data > 0:
                return jsonify(status="success"), 200
            else:
                return jsonify(status=data), 204
        else:
            return jsonify(status="error"), 404  

@app.route(endpoint + '/alarmen/<wekkerID>/<alarmID>', methods=['GET'])
def get_alarm_id(wekkerID,alarmID):
    if request.method == 'GET':
        s = DataRepository.read_alarm_by_id(alarmID,wekkerID)
        return jsonify(s), 200

@app.route(endpoint + '/muziekjes', methods=['GET'])
def get_muziekjes():
    if request.method == 'GET':
        s = DataRepository.read_muziekjes()
        return jsonify(s), 200

@app.route(endpoint + '/alarmen/changeOnOff/<id>', methods=['PUT','GET'])
def updatetypes(id):
    gegevens = DataRepository.json_or_formdata(request)
    data = DataRepository.update_alarm(gegevens["value"],id)
    if data is not None:
        if data > 0:
            return jsonify(idtype=id, status="success"), 200
        else:
            return jsonify(status=data), 204
    else:
        return jsonify(status="error"), 404

@app.route(endpoint + '/smartlamp/changeOnOff/<wekkerID>', methods=['PUT','GET'])
def updateLamp(wekkerID):
    data = DataRepository.update_lamp_uit(wekkerID)
    if data is not None:
        if data > 0:
            return jsonify(wekkerID=wekkerID, status="success"), 200
        else:
            return jsonify(status=data), 204
    else:
        return jsonify(status="error"), 404

@app.route(endpoint + '/smartlamp/changeStatus/<wekkerID>/<status>', methods=['PUT','GET'])
def updateLampStatus(wekkerID,status):
    data = DataRepository.update_lamp_status(wekkerID,status)
    if data is not None:
        if data > 0:
            return jsonify(wekkerID=wekkerID, status="success"), 200
        else:
            return jsonify(status=data), 204
    else:
        return jsonify(status="error"), 404

@app.route(endpoint + '/alarmen/delete/<alarmID>', methods=['DEL','GET'])
def delete_alarm_id(alarmID):
    data = DataRepository.delete_alarm(alarmID)
    if data is not None:
        if data > 0:
            return jsonify(alarmID=alarmID, status="success"), 200
        else:
            return jsonify(status=data), 204
    else:
        return jsonify(status="error"), 404

#SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('New client connect')
    setup()  
    threading.Thread(target=getTemp).start()
    threading.Thread(target=getTempGrafiek).start()      
    threading.Thread(target=tijd_sturen).start()
    threading.Thread(target=checkAlarm).start()
    threading.Thread(target=statusLight).start()
    threading.Thread(target=lichtAanpassen).start()
    initialLCD()

@socketio.on('F2B_shutdown')
def initial_connection():
    print('Uitzetten')
    os.system('sudo shutdown -r now')

      
#
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
    app.run(host="169.254.10.1", port=5000, debug=True)
