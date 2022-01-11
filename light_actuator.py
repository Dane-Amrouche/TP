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
from uuid import getnode as get_mac

class Light_actuator(Objet):

    # class attributes
    MQTT_PUB_LUM = None
    MQTT_SUB_LUM = None
    MQTT_SUB_PRESENCE = None
    MQTT_PUB_ALARM = None
    MQTT_PUB_LIGHT = None
    presence_sensor_subID = None
    luminosity_sensor_subID = None
    shutter_unitID = None
    is_there_someone = False
    are_blinds_open = False
    unauthorised = False
    
    _condition  = None      # threading condition
    _thread     = None      # thread to handle shutter's course

    def __init__(self, unitID, MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT,MQTT_PUB_LUM, MQTT_SUB_LUM, MQTT_SUB_PRESENCE,
                 MQTT_PUB_ALARM,MQTT_PUB_LIGHT, presence_sensor_subID, luminosity_sensor_subID, shutter_unitID, io_backend=None, upOutput=None, downOutput=None, stopOutput=None, shutdown_event=None, *args, **kwargs):
       
        self.MQTT_PUB_LUM = MQTT_PUB_LUM
        self.MQTT_SUB_LUM = MQTT_SUB_LUM
        self.MQTT_SUB_PRESENCE = MQTT_SUB_PRESENCE
        self.MQTT_PUB_ALARM = MQTT_PUB_ALARM
        self.MQTT_PUB_LIGHT = MQTT_PUB_LIGHT
        self.presence_sensor_subID = presence_sensor_subID
        self.luminosity_sensor_subID = luminosity_sensor_subID
        self.shutter_unitID = shutter_unitID
        
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
         

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connection.connected_flag = True
            print("Connection returned code: "+ str(rc))
            self.connection.subscribe(self.mqtt_sub_topic,qos=0)
            self.connection.subscribe(self.MQTT_SUB_PRESENCE,qos=0)
            self.connection.subscribe(self.MQTT_SUB_LUM,qos=0)
        else:
             print("Bad connection Returned code= "+str(rc))
             
     
     
    def send_alarm(self):
        data = { 
            "unitID": self.unitID,   
            "order": "ALARM"
        }
        data_out = json.dumps(data)
        self.connection.publish(self.MQTT_PUB_ALARM, data_out)
        
    def get_date_time(self):
        weekdays= ("Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche")
        # detect time and the day
        time = datetime.now().strftime("%H")
        date = datetime.today().weekday()
        return (weekdays[date],time)

    def on_message(self, client, userdata, msg):
        
        #check that the presence respects the times that authorise access
        (day, hour) = self.get_date_time()
        hour = int(hour)
        if self.is_there_someone:
            # authorised times : mon-frid -> 8h-20h and sat ->8h-15h 
            if (day == "Dimanche"):
                #send alarm
                self.send_alarm()
                return
            elif day == "Samedi" and (hour < 8 or hour > 15):
                #send alarm
                self.send_alarm()
                return
            else:
                if (hour < 8 or hour > 20):
                    # send alarm 
                    self.send_alarm()
                    return
                    
        payload = json.loads(msg.payload)
        print(payload)
        
        if payload['unitID'] == self.shutter_unitID:
             print("shutter")
             if payload['status']== 1:
                self.are_blinds_open = True
             else:
                self.are_blinds_open = False
                
        # get the source of the message the message
        elif payload['subID'] == self.presence_sensor_subID:
            print("presence")
            if payload['value']:
               #if someone is detected get the luminosity value
               self.is_there_someone = True
               data = {
                "dest": self.luminosity_sensor_subID,
                "order": "capture"
               }
               data_out = json.dumps(data)
               # send current data 
               self.connection.publish(self.MQTT_PUB_LUM, data_out) 
            else:
                # if no one in the room turn off the lights
                self.is_there_someone = False
                data = {
                    "dest": "light",
                    "order": "off"
                }
                data_out = json.dumps(data)
                # send current data 
                self.connection.publish(self.MQTT_PUB_LIGHT, data_out)
                
                  
        elif payload['subID'] == self.luminosity_sensor_subID and self.is_there_someone:
            print(self.are_blinds_open)
            if payload['value'] < 400 and self.are_blinds_open:
                # if lum <400 and blinds are open turn on the lights
                data = {
                    "dest": "light",
                    "order": "On"
                }
                data_out = json.dumps(data)
                # send current data 
                self.connection.publish(self.MQTT_PUB_LIGHT, data_out)
            elif payload['value'] < 400:
                # the blinds are close we should open them
                data = {
                    "dest": self.shutter_unitID,
                    "order": "UP"
                }
                data_out = json.dumps(data)
                # send current data 
                self.connection.publish(self.mqtt_pub_topic, data_out)
                # then wait that the blinds open completely to update are_blinds_open variable
        
        # at the end of the day the shutters will be closed automatically
        if ((day == "samedi" and hour > 15) or (hour > 20)) and self.are_blinds_open:
            # send a down command to shutter
            data = {
                "dest": self.shutter_unitID,
                "order": "DOWN"
            }
            data_out = json.dumps(data)
            # send current data 
            self.connection.publish(self.mqtt_pub_topic, data_out)
                
            

#
# MAIN
#

def main():

    MQTT_PUB_SHUTTER = "salle14/shutter/command"
    MQTT_SUB_SHUTTER = "salle14/shutter"
    MQTT_PUB_LUM = "salle14/Luminosity/command"
    MQTT_SUB_LUM = "salle14/Luminosity"
    MQTT_SUB_PRESENCE = "salle14/Presence"
    MQTT_PUB_ALARM = "Security/Alarm"
    MQTT_PUB_LIGHT = "salle14/light/command"
    MQTT_SERVER = "192.168.0.206"
    MQTT_PORT = 1883
    presence_sensor_subID = 120
    luminosity_sensor_subID = 57
    shutter_unitID = "center"

# declare the 3 shutters in our class
    unitID = get_mac()
    subID = 125
    
    l = Light_actuator(unitID, MQTT_PUB_SHUTTER,MQTT_SUB_SHUTTER,MQTT_SERVER,MQTT_PORT,MQTT_PUB_LUM, MQTT_SUB_LUM,
                                        MQTT_SUB_PRESENCE,MQTT_PUB_ALARM,MQTT_PUB_LIGHT,presence_sensor_subID,luminosity_sensor_subID,shutter_unitID)


# Execution or import
if __name__ == "__main__":

    # Logging setup
    '''logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s", stream=sys.stdout)
    log = logging.getLogger()

    print("\n[DBG] DEBUG mode activated ... ")
    log.setLevel(logging.DEBUG)'''
    #log.setLevel(logging.INFO)

    # Start executing
    main()


# The END - Jim Morrison 1943 - 1971
#sys.exit(0)


