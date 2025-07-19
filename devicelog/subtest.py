import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "ozoman.com"
MQTT_PORT = 1883
MQTT_TOPIC = "Gokul_SP900_W"
USERNAME = "farazan"
PASSWORD = "abc123"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):
    print(f"📥 Message received on topic {msg.topic}")
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print("Message JSON:")
        print(json.dumps(data, indent=4))
    except Exception as e:
        print(f"⚠️ Error decoding JSON: {e}")
        print(f"Raw message: {msg.payload}")

def on_disconnect(client, userdata, rc):
    print("⚠️ Disconnected from MQTT Broker")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT} ...")
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

client.loop_forever()
