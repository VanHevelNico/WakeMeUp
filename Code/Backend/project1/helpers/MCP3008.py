from RPi import GPIO
import spidev
import time

class MCP3008:

    def __init__(self,spi):
        self.spi = spi
        spi.open(0,0)
        spi.max_speed_hz = 10**5

    def read_channel(self, channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data