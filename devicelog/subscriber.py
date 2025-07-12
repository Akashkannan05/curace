import signal
import sys
import time
import paho.mqtt.client as mqtt
import json
from modelsmqtt import DeviceRecord

def graceful_exit(signum, frame):
    print(f"\nReceived signal {signum}. Stopping MQTT client...")
    client.loop_stop()
    client.disconnect()
    print("MQTT client disconnected cleanly.")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, graceful_exit)
signal.signal(signal.SIGINT, graceful_exit)

def on_message(client, userdata, msg):
    data=json.loads(msg.payload.decode())
    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print("Invalid JSON received:", e)
        return
    except UnicodeDecodeError as e:
        print("Payload could not be decoded:", e)
        return
    #print(data)
    list=data["input1"]
    device=DeviceRecord(topic=msg.topic)
    for i in list:
        if i.get("name")=="Data_1":

            device.pH = i.get("data")[0]
            device.waterTemperature = i.get("data")[1]
            device.waterLinePressure = i.get("data")[2]
            device.mosfetTemperature = i.get("data")[3]
            device.ozoneModuleCurrent = i.get("data")[4]
            device.o3OperatingFrequency = i.get("data")[5]
            device.oxygenFlow = i.get("data")[6]
            

        if i.get("name")=="Data_2":
            device.ORP = i.get("data")[0]
            device.DCBusVoltage = i.get("data")[1]
            device.ozonePowerinWatts = i.get("data")[2]
            device.ozoneConcentration = i.get("data")[3]
            device.oxygenPurity = i.get("data")[4]
            device.ambientOzone = i.get("data")[5]


        
        if i.get("name")=="Data_3":
            boolList=[]
            for j in i.get("data"):
                boolList.append(bool(j))
            device.filterFeedPump = boolList[0]
            device.ozoneBoosterPump = boolList[1]
            device.oxygenGenerator = boolList[2]
            device.ozoneGenerator = boolList[3]
            device.ozoneDestructor = boolList[4]
            device.dosingPumpPH = boolList[5]
            # device.dummy1 = boolList[6]
            device.ozoneON = boolList[8]
            device.alarmOzoneTrippedByLowPower = boolList[9]
            device.alarmOzoneTrippedByHighPower = boolList[10]
            device.alarmOzoneTrippedByMosfet1Fault = boolList[11]
            device.alarmOzoneTrippedByMosfet2Fault = boolList[12]
            device.alarmOzoneTrippedByMosfet3Fault = boolList[13]
            device.alarmOzoneTrippedByMosfet4Fault = boolList[14]
            device.alarmOzoneTrippedByTemperatureFault = boolList[15]
            device.alarmOzoneTrippedByLoadFault = boolList[16]
            device.alarmOzoneTrippedFault = boolList[17]
            device.alarmOzoneTrippedByInrushVoltageFault = boolList[18]
            # device.dummy2 = boolList[19]
            device.alarmOxygenPurityLow = boolList[21]
            device.alarmAmbientOzoneLevelHigh = boolList[22]
            device.warningPHLevelHigh = boolList[23]
            device.warningPHLevelLow = boolList[24]
            device.systemStart = boolList[25]
            device.forceTurnONFilterFeedPump = boolList[26]
            device.forceTurnONOzonePump = boolList[27]
            device.forceTurnONOxygenGenerator = boolList[28]
            device.forceTurnONOzoneGenerator = boolList[29]
            device.forceTurnONPHDosingPump = boolList[30]
            device.forceTurnONFloccDosingPump = boolList[31]
            device.forceTurnONCoagDosingPump = boolList[32]
            device.forceTurnONBackWashValve = boolList[33]
            device.forceTurnONChlorineDosingPump = boolList[34]
            # device.dummy3 = boolList[35]
            device.dosingPumpFlocculation = boolList[64]
            device.dosingPumpCoggulation = boolList[65]
            device.ozoneEnable = boolList[66]
            device.lampGreen = boolList[67]
            device.lampYellow = boolList[68]
            device.lampRed = boolList[69]
            device.hooter = boolList[70]
            # device.dummy4 = boolList[71]

            

        if i.get("name")=="Data_4":
            boolList=[]
            for j in i.get("data"):
                boolList.append(bool(j))
            device.warningPHDosingTankLevelLow = boolList[0]
            device.warningFloccDosingTankLevelLow = boolList[1]
            device.warningCoaggDosingTankLevelLow = boolList[2]
            device.alarmFeedWaterPumpPressureLow = boolList[3]
            device.alarmOzoneBoosterPumpPressureLow = boolList[4]
            # device.dummy5 = boolList[5]



    device.save()


#client=mqtt.Client()
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.connect("ozoman.com")
client.username_pw_set(username="farazan", password="abc123")

client.on_message=on_message

#client.subscribe("deviceunique/#")

client.subscribe("#")

client.loop_start()
while True:
    time.sleep(1)
