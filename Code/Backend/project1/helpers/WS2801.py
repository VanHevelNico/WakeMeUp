from RPi import GPIO
import time

class WS2801:
    def __init__(self,sda,clk,aantalLeds):
        self.sda = sda
        self.clk = clk
        self.aantalLeds = aantalLeds
        #Variabelen voor kleurenwiel
        self.kleurTeller = 0
        self.kleurModus = 1
        #Variabelen gewoon
        self.gewoonTeller = 0

    def setup(self):
        GPIO.setmode(GPIO.BCM)    
        GPIO.setup(self.sda,GPIO.OUT)
        GPIO.setup(self.clk,GPIO.OUT) 
        GPIO.output(self.clk,0)
        time.sleep(0.005)
 

    def set_byte(self,byte):
        #print("byte: ",byte)
        mask = 128
        for i in range(0,8):
            if byte & (mask >> i): #Als het een 1 is
                #print(1)
                GPIO.output(self.sda,1)
                GPIO.output(self.clk,1)
                GPIO.output(self.clk,0)
            else:
                #print(0)
                GPIO.output(self.sda,0)
                GPIO.output(self.clk,1)
                GPIO.output(self.clk,0)
        #print("------ Einde byte ------")

    def allesUit(self,hoeveelLeds):
        time.sleep(0.005)
        for i in range(0,hoeveelLeds):
            self.set_byte(0)    
            self.set_byte(0)    
            self.set_byte(0)
        self.gewoonTeller = 0
        self.kleurModus = 1
        self.kleurTeller = 0            

    def flikker(self,hoeveelLeds,delay, helderheid):
        for j in range(0,hoeveelLeds):
            self.set_byte(helderheid)   #Rood  
            self.set_byte(0)    #Blauw
            self.set_byte(0)     #Groen

        time.sleep(delay)

        for j in range(0,hoeveelLeds):
            self.set_byte(0)   #Rood  
            self.set_byte(0)    #Blauw
            self.set_byte(0)     #Groen

        time.sleep(delay)

    def kleur(self,hoeveelLeds,delay,helderheid):
        if(self.kleurModus == 1):
            rood = helderheid
            groen = self.kleurTeller
            blauw = 0
        elif(self.kleurModus == 2):
            rood = helderheid - self.kleurTeller
            groen = helderheid
            blauw = 0    
        elif(self.kleurModus == 3):
            rood = 0
            groen = helderheid
            blauw = self.kleurTeller   
        elif(self.kleurModus == 4):
            rood = 0
            groen = helderheid - self.kleurTeller
            blauw = helderheid                
        elif(self.kleurModus == 5):
            rood = self.kleurTeller
            groen = 0
            blauw = helderheid            
        elif(self.kleurModus == 6):
            rood = helderheid
            groen = 0
            blauw = helderheid - self.kleurTeller                

        if(self.kleurTeller == helderheid):
            if(self.kleurModus <= 5):
                self.kleurModus +=1
            else: 
                self.kleurModus = 1
            self.kleurTeller = 0

        for i in range(0,hoeveelLeds):
            self.set_byte(rood)   #Rood  
            self.set_byte(blauw)    #Blauw
            self.set_byte(groen)     #Groen    
            time.sleep(0.00001)
        self.kleurTeller += 1
        time.sleep(delay)

    def gewoon(self,hoeveelLeds,delay,maxHelderheid):
        if(self.gewoonTeller < maxHelderheid):
            self.gewoonTeller += 1
            for i in range(0,hoeveelLeds):
                self.set_byte(self.gewoonTeller)   #Rood  
                self.set_byte(self.gewoonTeller)    #Blauw
                self.set_byte(self.gewoonTeller)     #Groen
                print(self.gewoonTeller)
        time.sleep(delay)