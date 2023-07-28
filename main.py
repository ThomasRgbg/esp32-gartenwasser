from machine import Pin, I2C, reset, RTC, unique_id, Timer, WDT
import time
import ntptime
# import esp32
import uasyncio
import gc
import micropython

from mqtt_handler import MQTTHandler
from relay import Relay

from tfluna_i2c import Luna 

#####
# Schematic/Notes
######

# Relays
# GPIO23 Ch1 Valve1
# GPIO22 Ch2 Valve2
# GPIO21 Ch3 Valve3
# GPIO19 Ch4 Valve4
# GPIO18 Ch5
# GPIO5  Ch6 Pump
# GPIO16 Ch7 Wallplug 1
# GPIO17 Ch8 Wallplug 2

# Buttons
# GPIO32 Button 1 - Pump on/off
# GPIO33 Button 2 - 

# Sensors
# GPIO15 DHT11
# GPIO34 ADC1
# GPIO35 ADC2

# TF Luna
# GPIO25 CLK
# GPIO26 SDA

#####
# Watchdog - 120 seconds, need to be larger then loop time below
#####

wdt = WDT(timeout=120000)

#####
# Housekeeping
#####

wdt.feed()
count = 1
errcount = 0

def get_count():
    global count
    return count

def get_errcount():
    global errcount
    return errcount

#####
# MQTT setup
#####

# time to connect WLAN, since marginal reception
time.sleep(5)

sc = MQTTHandler(b'pentling/gartenwasser', '192.168.0.13')
#sc.register_publisher('pm25', pm25.get_pm25)
#sc.register_publisher('errcount', get_errcount)
#sc.register_publisher('count', get_count)


#####
# Task definition
#####

async def housekeeping():
    global errcount
    global count
    await uasyncio.sleep_ms(1000)

    while True:
        print("housekeeping() - count {0}, errcount {1}".format(count,errcount))
        wdt.feed()
        gc.collect()
        micropython.mem_info()

        # Too many errors, e.g. could not connect to MQTT
        if errcount > 20:
            reset()

        count += 1
        await uasyncio.sleep_ms(60000)

async def handle_mqtt():
    global errcount
    while True:
        # Generic MQTT
        if sc.isconnected():
#        if True:
            print("handle_mqtt() - connected")
    #            for i in range(29):
    #                sc.mqtt.check_msg()
    #                time.sleep(1)
            sc.publish_all()
        else:
            print("handle_mqtt() - MQTT not connected - try to reconnect")
            sc.connect()
            errcount += 1
            await uasyncio.sleep_ms(19000)

        for i in range(45):
            # print(i)
            await uasyncio.sleep_ms(1000)

####
# Main
####

print("main_loop")
main_loop = uasyncio.get_event_loop()

main_loop.create_task(housekeeping())
main_loop.create_task(handle_mqtt())

main_loop.run_forever()
main_loop.close()




