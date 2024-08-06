import paho.mqtt.client as mqtt
import time

# Configuration
broker = "localhost"
port = 1883
topic = "simul/raspatientpi"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def publish_message(client, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "PythonMQTTPublisher")
client.on_connect = on_connect
client.connect(broker, port, 60)

# Start the loop
client.loop_start()

i = 0
while True:
    time.sleep(1)
    i += 1
    publish_message(client, f"Test {i}")
