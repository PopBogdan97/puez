import time
import pycom
import struct
import socket
import ubinascii
from network import LoRa
from network import Bluetooth
from machine import Timer

class BLEThing:

    bt_periph = Bluetooth()
    bt_periph.set_advertisement(name = 'puez_1df7b', service_uuid = b'1234567890123456')

    def conn_cb (bt_o):
        events = bt_o.events()
        if  events & Bluetooth.CLIENT_CONNECTED:
            bt_o.advertise(False)
            print("Client connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            bt_o.advertise(True)
            print("Client disconnected")

    bt_periph.callback(trigger = Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler = conn_cb)
    bt_periph.advertise(True)
    service1 = bt_periph.service(uuid = 0, isprimary = True, nbr_chars=10)
    #service2 = bt_periph.service(uuid = b'1234567890123457', isprimary = True)

    temperature = service1.characteristic(uuid = 1, value = 'TEMPERATURE')
    light = service1.characteristic(uuid = 2, value = 'LIGHT')
    flame = service1.characteristic(uuid = 3, value = 'FLAME')
    humidity = service1.characteristic(uuid = 4, value = 'HUMIDITY')
    windSpeed = service1.characteristic(uuid = 5, value = 'WINDSPEED')
    windDirection = service1.characteristic(uuid = 6, value = 'WINDDIRECTION')
    time = service1.characteristic(uuid = 7, value = 'TIME')
    # user = service1.characteristic(uuid = 1, value = 'ciao')
    # user = service1.characteristic(uuid = 2, value = 'cazzo')
    # #blaster2 = service1.characteristic(uuid = 2, value = 'cazzo')
    # cont = 55
    # user2 = service2.characteristic(uuid = 2, value = cont)
    # while (True):
    #     cont += 1
    #     print(cont)
    #     user2.value(cont)
    #     time.sleep_ms(1000)
    #
    # def blaster_cb(chr):
    #     print("Read request, returning value = {}".format(user.value()))
    #
    # blaster_cb = temperature.callback(trigger = Bluetooth.CHAR_WRITE_EVENT, handler = blaster_cb)
    #
    # chr_try = srv_test.characteristic(uuid = b'ab34567890123456', value = 'culo')
    #
    # def blaster_ch(chr):
    #     print("Read request, returning value = {}".format(chr_try.value()))
    #
    # blaster_ch = chr_try.callback(trigger = Bluetooth.CHAR_READ_EVENT, handler = blaster_ch)

    pycom.heartbeat(True) # Initialise built-in LED


    def setTemperature(self, t):
        self.temperature.value(t)

    def setLight(self, t):
        self.light.value(t)

    def setHumidity(self, t):
        self.humidity.value(t)

    def setFlame(self, t):
        self.flame.value(t)

    def setWindSpeed(self, t):
        self.windSpeed.value(t)

    def setWindDirection(self, t):
        self.windDirection.value(t)

    def getTime(self):
        return self.time.value()
