import paho.mqtt.client as paho
import os
import socket
import ssl
from time import time
import json

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#", 1)

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8")
    payload_dict = json.loads(payload_str)

    timestamp = payload_dict.get("timestamp", "N/A")
    message_type = payload_dict.get("type", "N/A")
    value = payload_dict.get("value", "N/A")

    print(f"Timestamp: {timestamp}, Type: {message_type}, Value: {value}")

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

mqttc.loop_forever()
