from RPi import GPIO
import time

class SHIFTREGISTER:

    def __init__(self,ds_pin,shcp_pin,stcp_pin,mr_pin,oe_pin):
        self.ds_pin = ds_pin
        self.oe_pin = oe_pin
        self.stcp_pin = stcp_pin
        self.shcp_pin = shcp_pin
        self.mr_pin = mr_pin
    
    def setup(self):
        GPIO.setmode(GPIO.BCM)    
        GPIO.setup(self.ds_pin,GPIO.OUT)
        GPIO.setup(self.oe_pin,GPIO.OUT)
        GPIO.setup(self.stcp_pin,GPIO.OUT)
        GPIO.setup(self.shcp_pin,GPIO.OUT)
        GPIO.setup(self.mr_pin,GPIO.OUT)  

    def init_shift_register(self):
        GPIO.output(self.mr_pin, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(self.mr_pin, GPIO.HIGH)
        GPIO.output(self.oe_pin, GPIO.LOW)        

    def write_one_bit(self,bit):
        if(bit == False):
            GPIO.output(self.ds_pin,GPIO.LOW)
            time.sleep(0.001)
        else:
            GPIO.output(self.ds_pin,GPIO.HIGH)
            time.sleep(0.001)

        GPIO.output(self.shcp_pin,GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.shcp_pin,GPIO.LOW)
        GPIO.output(self.ds_pin,GPIO.LOW)

    def copy_to_storage_register(self):
        GPIO.output(self.stcp_pin,GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.stcp_pin,GPIO.LOW)

    def write_byte(self,byte):
        mask = 128 #Hexadecimale notatie voor 128
        for i in range(0,8):
            if byte & (mask >> i): #Als het een 1 is
                print(1)
                self.write_one_bit(True)
            else:
                print(0)
                self.write_one_bit(False)
    
    def reset_shift_register(self):
        pass

    def reset_storage_register(self):
        pass