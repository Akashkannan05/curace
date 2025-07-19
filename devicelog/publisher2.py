import paho.mqtt.client as mqtt
import time,json


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to MQTT Broker!")
        # Publish online status (Retained so others can read it later)
        # client.publish("Gokul_SP900_R", "online", retain=True)
        # # Optionally start sending sensor data or similar
        # client.publish("data/device_1", "Hello, I'm online!")
        
    else:
        print("❌ Failed to connect, return code:", reason_code)



data1={
    "date":"18/06/2025 13:28:55",
    "data":[3.000000,26.700001,1.827476,5.836252,9.126534,4.097600,2.000000],
    "name":"Data_1"
}


data2={
    "date":"18/06/2025 13:28:55",
    "data":[2,4,5,1,0,8],
    "name":"Data_2"
}

data3={
    "date":"18/06/2025 13:28:55",
    "data":[0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0],
    "name":"Data_3"
}

data4={
    "date":"18/06/2025 13:28:55",
    "data":[0, 0, 0, 1, 1],
    "name":"Data_4"
}
def on_publish(client, userdata, mid, reason_code, properties):
    print(f"Message {mid} published.")



MQTT_BROKER = "ozoman.com" 
MQTT_PORT = 1883
client=mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,client_id="akashash145")
client.username_pw_set(username="farazan", password="abc123")
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_start()


for i in range(300):
            time.sleep(1)
            client.publish("Gokul_SP900_R",json.dumps({"input1":[data1,data2,data3,data4]}))
            print(i)
        