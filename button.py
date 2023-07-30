# V1 Baseline

from machine import Pin 
import time 

####
# Button handler
####
class Button:
    def __init__(self, gpionum, mode="toggleswitch", actor=None):
        self.gpio = Pin(gpionum, Pin.IN, Pin.PULL_UP)
        self.gpionum = gpionum
        self.lastirq = 0       # Timestamp of last IRQ
        self.debounce = 50    # Minimal time between to IRQs (debouncer)
        self.mode = mode       # Could be "pushbutton" or "toggleswitch"
        self.saved_irq = False
        self.oldvalue = self.gpio.value()
        self.actor = actor

    def gpio_irq_callback(self,pin):
        self.gpio.value()

        delta = time.ticks_diff(time.ticks_ms(), self.lastirq)

        if (delta > self.debounce):
            self.lastirq = time.ticks_ms()
            print('b', end='')
            self.saved_irq = True
        else:
            print('d', end='')
            
        if self.mode == "pushbutton":
            self.swap_irq()

    def had_irq(self):
        if self.saved_irq:
            self.saved_irq = False
            return True
        else:
            return False

    def enable_irq(self):
        self.gpio.irq(handler=self.gpio_irq_callback, trigger=Pin.IRQ_FALLING)
        self.irqedge = Pin.IRQ_FALLING
        
    def swap_irq(self):
        if self.irqedge == Pin.IRQ_FALLING:
            self.gpio.irq(handler=self.gpio_irq_callback, trigger=Pin.IRQ_RISING)
            self.irqedge = Pin.IRQ_RISING
        else:
            self.gpio.irq(handler=self.gpio_irq_callback, trigger=Pin.IRQ_FALLING)
            self.irqedge = Pin.IRQ_FALLING
            
    def act(self):
        if self.actor is not None:
            value = self.gpio.value()
            if self.mode == "toggleswitch":
                if value == 1 and value != self.oldvalue:
                    self.oldvalue = value
                    self.actor.on()
                elif value == 0 and value != self.oldvalue:
                    self.oldvalue = value
                    self.actor.off()
            elif self.mode == "pushbutton":
                # zero = do something, since pull-up configured 
                if value == 0 and value != self.oldvalue:
                    self.actor.toggle()
                self.oldvalue = value
                    

                    
