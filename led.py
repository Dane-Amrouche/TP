 
import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
GPIO.setmode(GPIO.BCM)

class OnOff_led(Objet):

    # class attributes
    Type = None
    Led_pin = None

    def __init__(self, unitID=11, MQTT_PUB_TOPIC="1r1/014/light",MQTT_SUB_TOPIC="1r1/014/light/command",MQTT_SERVER = "192.168.0.206",MQTT_PORT = 1883,Type="light", Led_pin=5, io_backend=None, upOutput=None, downOutput=None, stopOutput=None, shutdown_event=None, *args, **kwargs):
       
        self.Type = Type
        self.Led_pin = Led_pin
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
         
    def on_message(self, client, userdata, msg): 
        
        payload = json.loads(msg.payload)
        # the les with get the commands ON or OFF and change their state according to it
        if payload['dest'] == self.Type:
            #it is the destination
            if payload['order'] == "On":
                # turn on the LED
                GPIO.setup(self.Led_pin,GPIO.OUT)  
                GPIO.output(self.Led_pin,GPIO.HIGH)
                print("led on")
            else:
                # turn off the LED
                GPIO.setup(self.Led_pin,GPIO.OUT)  
                GPIO.output(self.Led_pin,GPIO.LOW)

                

def main():
    #TODO: implement simple tests of your module
	led = OnOff_led()     


# Execution or import
if __name__ == "__main__":
    main()





