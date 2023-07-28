# V1 (baseline, do not remember)

from machine import Pin

 
class Relay:
    def __init__(self, gpio, invert=False):
        self.pin=Pin(gpio, Pin.OUT)
        self.gpio=gpio
        self.inverted = invert
        self.off()

    def on(self):
        print("replay.py/on() Set GPIO {0} on".format(self.gpio))
        if self.inverted:
            self.pin.value(0)
        else:
            self.pin.value(1)

    def off(self):
        print("replay.py/off() Set GPIO {0} off".format(self.gpio))
        if self.inverted:
            self.pin.value(1)
        else:
            self.pin.value(0)

    @property
    def state(self):
        value = self.pin.value()
        if self.inverted:
            if value == 1:
                value = 0
            else:
                value = 1
                    
        print("replay.py/state() State of Relay at  GPIO {0} is {1}".format(self.gpio, value))
        return value

    @state.setter
    def state(self, value):
        print("replay.py/state() Setting Relay at GPIO {0} to {1}".format(self.gpio, value))
        if int(value) == 1:
            self.on()
        else:
            self.off()

    def set_state(self, value):
        self.state = int(value)

    def get_state(self):
        return self.state
