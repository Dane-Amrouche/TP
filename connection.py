import paho.mqtt.client as mqtt
import time
import json


class Objet():

    # Connection attributes 

    connection         = None  # mqtt client
    mqtt_pub_topic     = None  # topic to publish into
    mqtt_sub_topic     = None  # topic to subscribe to
    unitID             = None  # id of the object instance 

    # Connection initialization
    def __init__(self,unitID ,mqtt_pub_topic, mqtt_sub_topic,mqtt_server,mqtt_port):
        
        self.mqtt_pub_topic = mqtt_pub_topic
        self.mqtt_sub_topic = mqtt_sub_topic
        self.unitID = unitID

        # setup MQTT connection
        
        self.connection = mqtt.Client()
        self.connection.connect(mqtt_server, mqtt_port, keepalive=60)
        

        self.connection.on_connect = self.on_connect
        self.connection.on_disconnect = self.on_disconnect
        self.connection.on_publish = self.on_publish
        self.connection.on_message = self.on_message
        self.connection.on_subscribe = self.on_subscribe

        self.connection.loop_forever()


    def send_message(self, topic, payload):
        pass

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connection.connected_flag = True
            print("Connection returned code: "+ str(rc))
            self.connection.subscribe(self.mqtt_sub_topic,qos=0)
        else:
             print("Bad connection Returned code= "+str(rc))
       
        

    def on_disconnect(self,client, userdata, rc):
        if rc != 0:
             print("Unexpected disconnection.")
        self.connection.connected_flag=False

    def on_publish(self, client, userdata, mid):
        pass

    def on_message(self, client, userdata, msg):
        print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic)
        
    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass


