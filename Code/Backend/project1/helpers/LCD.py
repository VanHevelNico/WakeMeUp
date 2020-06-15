from RPi import GPIO
import time
from helpers.SHIFTREGISTER import SHIFTREGISTER

class LCD:

    def __init__(self,E,RS,shift):
        self.E = E
        self.RS = RS
        self.shift = shift
  
    def setup(self):
        GPIO.setmode(GPIO.BCM)    
        GPIO.setup(self.RS,GPIO.OUT)
        GPIO.setup(self.E,GPIO.OUT)  

    def send_instruction_lcd(self,value):
        GPIO.output(self.RS,GPIO.LOW)
        GPIO.output(self.E,GPIO.HIGH)
        self.set_data_bits_lcd(value)
        GPIO.output(self.E,GPIO.LOW)
        time.sleep(0.001)
    
    def set_data_bits_lcd(self,byte):
        #print("byte: ",byte)
        mask = 1
        for i in range(0,8):
            if byte & (mask << i): #Als het een 1 is
                #print(1)
                self.shift.write_one_bit(1)
            else:
                #print(0)
                self.shift.write_one_bit(0)
        #print("------ Einde byte ------")
        self.shift.copy_to_storage_register()

    def init_lcd(self):
        self.send_instruction_lcd(56) #Normaal 56
        self.send_instruction_lcd(15)
        #Clear scherm
        self.send_instruction_lcd(1)

    def send_character_lcd(self,value):
        GPIO.output(self.RS,GPIO.HIGH)
        GPIO.output(self.E,GPIO.HIGH)
        self.set_data_bits_lcd(value)
        GPIO.output(self.E,GPIO.LOW)
        time.sleep(0.001)

    def write_message(self,message):
        teller = 0
        for char in message:
            char = ord(char)
            #print(char)
            self.send_character_lcd(char)
            teller = teller +1
            if teller == 15:
                self.send_instruction_lcd(168)