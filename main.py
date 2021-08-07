from machine import Pin, I2C, reset, RTC, unique_id, Timer
import time
import ntptime

from mqtt_handler import MQTTHandler
from relay import Relay

from tfluna_i2c import Luna 

#####
# Schematic/Notes
######

# Relays
# GPIO21 Ch1 Valve1
# GPIO22 Ch2 Valve2
# GPIO23 Ch3 Valve3
# GPIO5  Ch4 Pump On/off

# TF Luna
# GPIO18 CLK
# GPIO19 SDA

def updatetime(force):
    if (rtc.datetime()[0] < 2020) or (force is True):
        if wlan.isconnected():
            print("try to set RTC")
            try:
                ntptime.settime()
            except:  
                print("Some error around time setting, likely timeout")
    else:
        print("RTC time looks already reasonable: {0}".format(rtc.datetime()))

#####
# Watchdog - 120 seconds, need to be larger then loop time below
#####

wdt = WDT(timeout=120000)


####
# Main
####

# time to connect WLAN, since marginal reception
time.sleep(5)

pumpe = Relay(5)

i2c = I2C(scl=Pin(18), sda=Pin(19), freq=100000)
lidar = Luna(i2c)

sc = MQTTHandler(b'pentling/zistvorne', '192.168.0.13')
sc.register_action('pump_enable', pumpe.set_state)

rtc = RTC()
wdt.feed()

logfile = open('logfile.txt', 'w')

def mainloop():
    count = 1
    errcount = 0

    while True:
        dist, min_dist, max_dist = lidar.read_avg_dist()
        amp = lidar.read_amp()
        errorv = lidar.read_error()
        temp = lidar.read_temp()
        timestamp = rtc.datetime()
        print("Distance: {0}".format(dist))
        print("Min Distance: {0}".format(min_dist))
        print("Max Distance: {0}".format(max_dist))
        print("Amplification Value: {0}".format(amp))
        print("Error Value: {0}".format(errorv))
        print("Temperature: {0}".format(temp))
        print("Timestamp: {0}".format(timestamp))
        print("Pumpe: {0}".format(pumpe.state))
        print("Count: {0}".format(count))

        # On device logging for debugging
        if (logfile and (count % 10 == 0)) or (pumpe.state == 1):
            updatetime(False)
            print("Write logfile")
            logfile.write("{0}, ({1}),({2})\n".format(timestamp, dist,pumpe.state))
            logfile.flush()
        
        # After some hours, reallign things
        if (count % 100 == 0):
            # After some days, the TF Luna gets stuck with just one value
            print("periodic reset of Lidar")
            lidar.reset_sensor()
            # Force time sync to avoid to large drift
            updatetime(True) 

        if sc.isconnected():
            print("send to MQTT server")
            sc.mqtt.check_msg()
            sc.publish_generic('distance', dist)
            sc.publish_generic('min_distance', min_dist)
            sc.publish_generic('max_distance', max_dist)
            sc.publish_generic('pump', pumpe.state)
        else:
            print("MQTT not connected - try to reconnect")
            sc.connect()
            errcount += 1
            continue

        wdt.feed()

        time.sleep(40)

        # Too many errors, e.g. could not connect to MQTT
        if errcount > 20:
            reset()

        count += 1

mainloop()
