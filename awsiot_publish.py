import paho.mqtt.client as paho
import ssl
from time import sleep, time
import json
from random import uniform
import boto3
import uuid

connflag = False

aws_access_key_id = 'AKIAU744T2435MBWSD4I'
aws_secret_access_key = '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'
aws_region = 'Global'

awshost = "a17uo13akgrdvr-ats.iot.ap-southeast-2.amazonaws.com"
awsport = 8883
clientId = "aws-iot-mqtt"
thingName = "aws-iot-mqtt"
caPath = "AmazonRootCA1.pem"
certPath = "59eab497ba83881dd36837ba45357dfd391fb29f44a2b59db0be8cd014fe7b08-certificate.pem.crt"
keyPath = "59eab497ba83881dd36837ba45357dfd391fb29f44a2b59db0be8cd014fe7b08-private.pem.key"

boto3.setup_default_session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

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

sqs_queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/343388968759/iot-sqs-queue.fifo'
sqs_region = 'ap-southeast-2'

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_start()


sqs = boto3.client('sqs', region_name=sqs_region)

while True:
    sleep(0.5)
    if connflag:
        timestamp = int(time())  
        temperature_reading = uniform(20.0, 25.0)
        humidity_reading = uniform(40.0, 60.0)

        
        temperature_message_id = str(uuid.uuid4())
        humidity_message_id = str(uuid.uuid4())

        temperature_message = {"timestamp": timestamp, "type": "temperature", "value": "%.2f" % temperature_reading}
        humidity_message = {"timestamp": timestamp, "type": "humidity", "value": "%.2f" % humidity_reading}

        mqttc.publish("environment/temperature", json.dumps(temperature_message), qos=1)
        mqttc.publish("environment/humidity", json.dumps(humidity_message), qos=1)

        
        sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps({"environment": "temperature", "data": temperature_message}),
            MessageDeduplicationId=temperature_message_id,
            MessageGroupId='environment'
        )
        sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps({"environment": "humidity", "data": humidity_message}),
            MessageDeduplicationId=humidity_message_id,
            MessageGroupId='environment'
        )

        print(f"Messages sent: {temperature_message}, {humidity_message} to MQTT and SQS")
    else:
        print("Waiting for connection...")
