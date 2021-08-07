from machine import Pin

 
class Relay:
    def __init__(self, gpio):
        self.pin=Pin(gpio, Pin.OUT)
        self.gpio=gpio
        self.pin.value(0)

    def on(self):
        print("Set GPIO {0} on".format(self.gpio))
        self.pin.value(1)

    def off(self):
        print("Set GPIO {0} off".format(self.gpio))
        self.pin.value(0)

    @property
    def state(self):
        print("State off GPIO {0} is {1}".format(self.gpio, self.pin.value()))
        return self.pin.value()

    @state.setter
    def state(self, value):
        print("Setting Relay at GPIO {0} to {1}".format(self.gpio, value))
        if int(value) == 1:
            self.on()
        else:
            self.off()

    def set_state(self, value):
        self.state = int(value)

    def get_state(self):
        return self.state
