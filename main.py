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
# Relay outputs
#####
relay_w1 = Relay(23, invert=True)
relay_w2 = Relay(22, invert=True)
relay_w3 = Relay(21, invert=True)
relay_w4 = Relay(19, invert=True)
relay_pumpe = Relay(5, invert=True)
relay_st1 = Relay(16, invert=True)
relay_st2 = Relay(16, invert=True)

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

sc.register_action('pump_enable', relay_pumpe.set_state)
sc.register_publisher('pump', relay_pumpe.get_state)

sc.register_action('w1_enable', relay_w1.set_state)
sc.register_publisher('w1', relay_w1.get_state)
sc.register_action('w2_enable', relay_w2.set_state)
sc.register_publisher('w2', relay_w2.get_state)
sc.register_action('w3_enable', relay_w3.set_state)
sc.register_publisher('w3', relay_w3.get_state)
sc.register_action('w4_enable', relay_w4.set_state)
sc.register_publisher('w4', relay_w4.get_state)

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
            print("handle_mqtt() - connected")
                for i in range(59):
                    sc.mqtt.check_msg()
                    time.sleep(1)
            sc.publish_all()
        else:
            print("handle_mqtt() - MQTT not connected - try to reconnect")
            sc.connect()
            errcount += 1
            await uasyncio.sleep_ms(19000)

        #for i in range(45):
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




