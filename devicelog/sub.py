import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC = "uniqueeDevice/topic1"  # Change this to your actual topic

# Called when client connects to broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(TOPIC)
    print(f"Subscribed to topic: {TOPIC}")

# Called when message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"\n📥 Received on topic '{msg.topic}': {payload}")
        data = json.loads(payload)
        # Optional: Parse if format is like your API
        if "input1" in data:
            for i in data["input1"]:
                print(f"🔹 Name: {i.get('name')}, Data: {i.get('data')}")
    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)

# Set up client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect and loop forever
client.connect(MQTT_BROKER, MQTT_PORT, 60)
print("📡 Waiting for messages...")
client.loop_forever()

