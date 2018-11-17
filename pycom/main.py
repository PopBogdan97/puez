import utime
import pycom
import struct
import socket
import ubinascii
import os
import machine
from machine import Pin
from network import LoRa
from machine import ADC
from dth import DTH
import ujson
import crypto
from BLEThing import BLEThing

def Random():
   r = crypto.getrandbits(32)
   return ((r[0]<<24)+(r[1]<<16)+(r[2]<<8)+r[3])/4294967295.0

def RandomRange(rfrom, rto):
   return Random()*(rto-rfrom)+rfrom

# If a user connects, store its ID and timestamp
btId = ""
ti = 0
def CALL_BACK(value):
    print(" ",value)
    a = str(value).split(" ")
    global btId
    btId = a[0]
    global ti
    ti = a[1]

pycom.heartbeat(False) # Initialise built-in LED
uart = machine.UART(1, 9600)

# ------------Set-up sensors----------------#
# Basic analog reading (12 bits by default, 4096)
# adc = machine.ADC()
# apin = adc.channel(pin='P14', attn=ADC.ATTN_11DB)
# apin() prints the ADC value
# More info: https://docs.pycom.io/firmwareapi/pycom/machine/adc

# SENSOR ----- PIN --- ATTENUATION
# DHT11        P3      ADC.ATTN_0DB
# Flame        P17     ADC.ATTN_0DB
# LM35         P14     ADC.ATTN_0DB
# Light        P17     ADC.ATTN_11DB

flame = machine.ADC()
temp = machine.ADC()
light = machine.ADC()

# Might need to set it to 11DB for real flames
flamePin = flame.channel(pin='P17', attn=flame.ATTN_0DB) # G6
tempPin = temp.channel(pin='P14', attn=temp.ATTN_0DB) # G4
# Calibration: 3.1 volts, maximum is 6000 lux, min is 1 lux
lightPin = light.channel(pin='P20', attn=light.ATTN_11DB) # G7
th = DTH(Pin('P3', mode=Pin.OPEN_DRAIN),0)

# Initialise BLE and callback when a user connects
thing = BLEThing()
thing.setCallBack(CALL_BACK)


# Initialise LoRa in LORAWAN mode
lora = LoRa(mode=LoRa.LORAWAN, device_class=LoRa.CLASS_C)

# Create an ABP authentication
dev_addr = struct.unpack(">l", ubinascii.unhexlify('007f6c48'))[0] # your device address here
nwk_swkey = ubinascii.unhexlify('e8b5606374b7688c4585a3c25c0a79de') # your network session key here
app_swkey = ubinascii.unhexlify('4596c2f319690ff914cdca0212f622a4') # your application session key here

# Join the network using ABP (Activation By Personalisation)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# Remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)

# Set the 3 default channels to the same frequency
lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

# Uplink sending and downlink receiving
while(True):
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW) # create a LoRa socket
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5) # set the LoRaWAN data rate
    s.setblocking(False) # make the socket non-blocking

    # Print and save all the values to be sent
    flameVal = flamePin()
    # print("Flame = %d" % flameVal)
    tempVal1 = tempPin()/32
    # print("Temperature (LM35) = %.2f" % tempVal1)
    lightVal = 6000 * lightPin()/4096 # Translate into lux
    # print("Light = %.2f lx" % lightVal)
    dhtVal = th.read()
    tempVal2 = dhtVal.temperature
    # print("Temperatura (DHT11) = %.2f C" % tempVal2)
    avgTemp = (tempVal1 + tempVal2) / 2.0
    # print("AvgTemp = %.2f" % avgTemp)
    humVal = dhtVal.humidity
    # print("Humidity = %d %%" % humVal)

    windSpeed = RandomRange(0, 40)
    windDir = RandomRange(0,360) # Polar coordinates 90 degrees shifted

    # Sending start, prepare JSON object
    pkt = {
        "F": flameVal,
        "L": lightVal,
        "T": avgTemp,
        "H": humVal,
        "W": windSpeed,
        "D": windDir,
        "BTid": btId,
        "Time": ti
    }
    pktReady = ujson.dumps(pkt)

    # Uplink sending
    s.send(pktReady)

    print(pktReady + " sent")

    # Once it is sent, clear data from the callback
    btId = ""
    ti = 0

    # Now, send the data to the client via BLE
    thing.setTemperature(str(avgTemp))
    thing.setLight(str(lightVal))
    thing.setHumidity(str(humVal))
    thing.setFlame(str(flameVal))
    thing.setWindSpeed(str(windSpeed))
    thing.setWindDirection(str(windDir))

    utime.sleep(6) # this dead-time is needed by the network to gather to your LoRa packets
    # Sending finished

    # Downlink receiving
    rx, port = s.recvfrom(4096)
    if rx:
        print('Received: {}, on port: {}'.format(rx, port))

    s.close() # close the LoRa socket
    ##end of LoRa
