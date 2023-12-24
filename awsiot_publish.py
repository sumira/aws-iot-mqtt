import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep, time
from random import uniform
import json

connflag = False

def on_connect(client, userdata, flags, rc):
    global connflag
    if rc == 0:
        print("Connected to AWS IoT")
        connflag = True
    else:
        print(f"Connection failed with result code {rc}")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

awshost = "a17uo13akgrdvr-ats.iot.ap-southeast-2.amazonaws.com"
awsport = 8883
clientId = "aws-iot-mqtt"
thingName = "aws-iot-mqtt"
caPath = "AmazonRootCA1.pem"
certPath = "59eab497ba83881dd36837ba45357dfd391fb29f44a2b59db0be8cd014fe7b08-certificate.pem.crt"
keyPath = "59eab497ba83881dd36837ba45357dfd391fb29f44a2b59db0be8cd014fe7b08-private.pem.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_start()

while True:
    sleep(0.5)
    if connflag:
        timestamp = int(time())  # Current timestamp in seconds since the epoch
        temperature_reading = uniform(20.0, 25.0)
        humidity_reading = uniform(40.0, 60.0)
        
        temperature_message = {"timestamp": timestamp, "type": "temperature", "value": "%.2f" % temperature_reading}
        humidity_message = {"timestamp": timestamp, "type": "humidity", "value": "%.2f" % humidity_reading}
        
        mqttc.publish("environment", json.dumps(temperature_message), qos=1)
        mqttc.publish("environment", json.dumps(humidity_message), qos=1)
        
        print(f"Messages sent: {temperature_message}, {humidity_message}")
    else:
        print("Waiting for connection...")
