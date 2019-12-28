#!/usr/bin/env python

import Global

if not Global.__EMULATE_HW__:
    import RPi.GPIO as GPIO


PI3b = [3,5,7,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]


class Relay(object):
    def __init__(self, pin):
        self.pin = pin
        if not Global.__EMULATE_HW__:
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        if not Global.__EMULATE_HW__:
            GPIO.output(self.pin, GPIO.HIGH)
        return

    def off(self):
        if not Global.__EMULATE_HW__:
            GPIO.output(self.pin, GPIO.LOW)
        return

class Led(object):
    def __init__(self, pin):
        self.pin = pin
        if not Global.__EMULATE_HW__:
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        if not Global.__EMULATE_HW__:
            GPIO.output(self.pin, GPIO.HIGH)
        return

    def off(self):
        if not Global.__EMULATE_HW__:
            GPIO.output(self.pin, GPIO.LOW)
        return

class Button(object):
    def __init__(self, pin):
        self.pin = pin
        # Button pin set as input w/ pull-up to avoid false detection
        if not Global.__EMULATE_HW__:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def addEventDetect(self, myCallback, bouncetime=300):
        if not Global.__EMULATE_HW__:
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=myCallback, bouncetime=bouncetime)
        return

    def removeEventDetect(self):
        if not Global.__EMULATE_HW__:
            GPIO.remove_event_detect(self.pin)
        return

    
class HWSet(object):
    
    def __init__(self, id, relayPin, ledPin, buttonPin):
        self.id = id
        self.relayPin = relayPin
        self.ledPin = ledPin
        self.buttonPin = buttonPin
        
        self.relay = Relay(self.relayPin)
        if self.ledPin:
            self.led = Led(self.ledPin)
        if self.buttonPin:
            self.button = Button(self.buttonPin)

        self._pwr = False
        self.relay.off()
        
        if self.ledPin:
            self.led.off()

        if self.buttonPin:
            self.button.addEventDetect(self.buttonPin, self.buttonPressCallback)

    def __del__(self):
        self.relay = None
        self.led = None
        self.button = None

        if not Global.__EMULATE_HW__:
            GPIO.cleanup()

    def on(self):
        self._pwr = True
        self.relay.on()
        if self.ledPin:
            self.led.on()

    def off(self):
        self._pwr = False
        self.relay.off()
        if self.ledPin:
            self.led.off()

    def toggle(self):
        self._pwr = not self._pwr
        if self._pwr:
            self.on()
        else:
            self.off()

    def buttonPressCallback(self):
        # button pressed
        self.toggle()

    def  getState(self):
        return self._pwr
    
    
