import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO
from uuid import getnode as get_mac
import smbus

class Presence_sensor(Objet):

    # class attributes
    subID         = None 
    But_pin       = None  
  
    def __init__(self, But_pin = 12, unitID=get_mac(), subID=100, MQTT_PUB_TOPIC="1r1/014/presence", MQTT_SERVER="192.168.0.206", MQTT_PORT=1883,MQTT_SUB_TOPIC="1r1/014/presence/command", *args, **kwargs):
       
        ''' Initialize object '''

        self.subID = subID
        GPIO.setmode(GPIO.BCM)
        self.But_pin = But_pin
        GPIO.setup(self.But_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
        
        
      
    def presence_detect(self, pin):     
        print("presence detected")
        #publish the detected value
        data = {
                "unitID": self.unitID,
                "subID": self.subID,
                "value": not GPIO.input(pin)
         }
        data_out = json.dumps(data)
        # send current data
        self.connection.publish(self.mqtt_pub_topic, data_out)
        print("data sent",data_out)
       

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connection.connected_flag = True
            print("Connection returned code: "+ str(rc))
            GPIO.add_event_detect(self.But_pin, GPIO.BOTH, bouncetime=100)
            GPIO.add_event_callback(self.But_pin, self.presence_detect)
                         
        else:
             print("Bad connection Returned code= "+str(rc))
    
    def on_message(self, client, userdata, msg):
        
        print("received data")
        payload = json.loads(msg.payload)
        print("data received",payload)

#
# MAIN
#

def main():

    #TODO: implement simple tests of your module
    b = Presence_sensor(12)


# Execution or import
if __name__ == "__main__":
    # Start executing
    main()




