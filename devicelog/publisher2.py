import paho.mqtt.client as mqtt
import time,json

client=mqtt.Client()
client.connect('broker.hivemq.com',1883,60)

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

for i in range(2):
    time.sleep(2)
    client.publish("deviceunique/Topic2/",json.dumps({"input1":[data1,data2,data3,data4]}))




client.disconnect()
