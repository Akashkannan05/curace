from flask import Blueprint,jsonify,request
from flask_restful import Api,Resource,reqparse
from flask_jwt_extended import  jwt_required, get_jwt_identity
from http import HTTPStatus
from cryptography.fernet import Fernet
from datetime import datetime

import os
from .models import DeviceModel
from Users.models import UserModel
from Organization.models import OrganizationModel
from dotenv import load_dotenv
import json

import paho.mqtt.client as mqtt
import threading


device_bp=Blueprint("device",__name__)
api=Api(device_bp)

load_dotenv()
fernet=Fernet(os.getenv('ENCRYPTION_KEY').encode())
register={
    "Filter Feed pump":27,
    "Ozone Pump":28,
    "Oxygen Generator":29,
    "Ozone Generator":30,
    "PH Dosing Pump":31,
    "Flocculant Dosing Pump":32,
    "Coagulant Dosing Pump":33,
    "Backwash Valve":34,
    "Chlorine Dosing Pump":35
}


def on_off(topic, function_name,onOff=True):
    client = mqtt.Client()
    client.connect('broker.hivemq.com', 1883, 60)
    payload = {
        "cookie": 65432,
        "type": 0,
        "host": "192.168.0.164",
        "port": 502,
        "timeout": 3,
        "server_id": 3,
        "function": 5,
        "register_number": register[function_name],
        "coil_number": 26,
        "value": 1 if onOff else 0
        }
    client.publish(topic, json.dumps(payload))
    print(f"Published {payload} to {topic}")
    client.disconnect()

put_args_addDevice=reqparse.RequestParser()
put_args_addDevice.add_argument("organizationId",type=str,help="Organization ID required",required=False)
put_args_addDevice.add_argument("deviceId",type=str,help="Device ID required",required=True)
put_args_addDevice.add_argument('mqttTopicRead',type=str,help="Mqtt topic is required",required=True)
put_args_addDevice.add_argument('mqttTopicWrite',type=str,help="Mqtt topic is required",required=True)

class AddDevice(Resource):
    @jwt_required()
    def post(self):
        currentUserEmail=get_jwt_identity()
        args=put_args_addDevice.parse_args()
        user=UserModel.objects.filter(email=currentUserEmail).first()
        if args.get('organizationId') is not None:
            organizationId=fernet.decrypt(args.get('organizationId').encode()).decode()
        else:
            organizationId=user.organization

        if user is None:
            return ({"addDevice":"Failed","error":"User not found with this email"},HTTPStatus.NOT_FOUND)
        if user.userRole!="Admin" or user.status!="Active":
            return ({"addDevice":"Failed","error":"Only active admin users are allowed to add a device"},HTTPStatus.BAD_REQUEST)
        
        
        organizationqs=OrganizationModel.objects.filter(pk=organizationId).first()

        if organizationqs is None:
            return ({"addDevice":"Failed","error":"Organization not found"},HTTPStatus.NOT_FOUND)
        
        device=DeviceModel(
            deviceId=args.get("deviceId"),
            customerName=organizationqs.name,
            city=organizationqs.city,
            state=organizationqs.state,
            poolStatus="Excellent",
            organization=organizationqs.pk,
            createdBy=user.pk,
            mqttTopicRead=args.get("mqttTopicRead"),
            mqttTopicWrite=args.get("mqttTopicWrite"),

        )

        device.save()

        return ({"addDevice":"Success","message":"Device added"},HTTPStatus.CREATED)
    
api.add_resource(AddDevice,"/add/")



class ListDevice(Resource):
    @jwt_required()
    def get(self):
        currentEmail=get_jwt_identity()
        user=UserModel.objects.filter(email=currentEmail).first()
        if user is None:
            return ({"listDevice":"Failed","error":"user not found with this email"},HTTPStatus.NOT_FOUND)
        
        organizationId=user.organization
        if organizationId is None:
            return ({"listDevice":"Failed","error":"user does not fill organization"},HTTPStatus.BAD_REQUEST)
        
        devices=DeviceModel.objects.filter(organization=organizationId)
        if devices is None:
            return ({"listDevice":"Failed","error":"No devices"},HTTPStatus.NO_CONTENT)
        
        output=[]
        for i in devices:
            # objectId=fernet.encrypt(str(i.pk).encode()).decode()
            # "objectId":objectId,
            # dt = datetime.strptime(str(i.createdOn), "%a, %d %b %Y %H:%M:%S %Z")
            # formatted_date = dt.strftime("%Y-%m-%d")
            print(str(i.createdOn))
            dictionary={
                "deviceId":i.deviceId,
                "customer":i.customerName,
                "city":i.city,
                "state":i.state,
                "poolStatus":i.poolStatus,
                "createdOn":str(i.createdOn)
            }
            output.append(dictionary)

        return (jsonify(output))

api.add_resource(ListDevice,"/list/")

edit_args_device=reqparse.RequestParser()
edit_args_device.add_argument("deviceId",type=str,help="Device ID is required",required=True)
edit_args_device.add_argument("city",type=str,help="City is not given",required=False)
edit_args_device.add_argument("state",type=str,help="State is not given",required=False)

class EditDevice(Resource):
    @jwt_required()
    def patch(self):
        args=edit_args_device.parse_args()
        currentUserEmail=get_jwt_identity()
        user=UserModel.objects.filter(email=currentUserEmail).first()
        if user is None:
            return ({"EditDevice":"Failed","error":"User not found"},HTTPStatus.NOT_FOUND)
        
        if user.userRole!="Admin":
            return ({"EditDevice":"Failed","error":"Only admin can edit the device"},HTTPStatus.BAD_REQUEST)
        
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"EditDevice":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)

        if args.get("city") is not None:
            device.city=args.get("city")
        if args.get("state") is not None:
            device.state=args.get("state")
        device.save()

        return ({"EditDevice":"Success"},HTTPStatus.OK)


api.add_resource(EditDevice,'/edit/')


del_args_device=reqparse.RequestParser()
del_args_device.add_argument("deviceId",type=str,help="Object ID required",required=True)

class DeleteDevice(Resource):
    @jwt_required()
    def delete(self):
        currentemail=get_jwt_identity()
        args=del_args_device.parse_args()
        user=UserModel.objects.filter(email=currentemail).first()
        if user is None:
            return ({"deleteDevice":"Failed","error":"User not found"},HTTPStatus.NOT_FOUND)
        if user.userRole!="Admin" or user.status!="Active":
            return ({"deleteDevice":"Failed","error":"only active admin can delete the device"},HTTPStatus.BAD_REQUEST)
        print("........")
        # objectId=fernet.decrypt(args.get("objectId").encode()).decode()
        # print(objectId)
        device=DeviceModel.objects.filter(deviceId=args.get('deviceId')).first()
        if device is None:
            return ({"deleteDevice":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        organization=OrganizationModel.objects.filter(pk=device.organization).first()
        userOrganization=OrganizationModel.objects.filter(pk=user.organization).first()

        if device.organization!=user.organization and device.organization!=organization.associateBy and userOrganization.email!="akash2005k26kaniyur12@gmail.com":
            return ({"deleteDevice":"Failed","error":"you are not allowed to delete device"},HTTPStatus.UNAUTHORIZED)
        
        device.delete()
        return ({"deleteDevice":"success"},HTTPStatus.ACCEPTED)
    
api.add_resource(DeleteDevice,"/delete/")

class device_setting(Resource):
    @jwt_required()
    def get(self):
        # device_id=request.args.get("deviceId")
        device=DeviceModel.objects.filter(deviceId=request.args.get("deviceId")).first()
        if device is None:
            return ({"deviceSetting":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        output={
            "minimumPh":device.minimumPh,
            "maximumPh":device.maximumPh,
            "minimumORP":device.minimumORP,
            "maximumORP":device.maximumORP,
            "minimumTemperature":device.minimumTemperature,
            "maximumTemperature":device.maximumTemperature,
            "readingMqttTopic":device.readingMqttTopic,
            "sendingMqttTopic":device.sendingMqttTopic,

            "mqttTopicOriginalRead":device.mqttTopicOriginalRead,
            "mqttTopicOriginalWrite":device.mqttTopicOriginalWrite,

            "deviceFilterFeedPumpOnOff":device.deviceFilterFeedPumpOnOff,
            "deviceOzonePumpOnOff":device.deviceOzonePumpOnOff,
            "deviceOxygenGeneratorOnOff":device.deviceOxygenGeneratorOnOff,
            "deviceOzoneGeneratorOnOff":device.deviceOzoneGeneratorOnOff,
            "devicePhDosingPumpOnOff":device.devicePhDosingPumpOnOff,
            "deviceFlocculantDosingPumpOnOff":device.deviceFlocculantDosingPumpOnOff,
            "deviceCoagulantDosingPumpOnOff":device.deviceCoagulantDosingPumpOnOff,
            "deviceBackwashValveOnOff":device.deviceBackwashValveOnOff,
            "deviceChlorineDosingPumpOnOff":device.deviceChlorineDosingPumpOnOff
        }
        return ({"deviceSetting":"Success","data":output},HTTPStatus.OK)
api.add_resource(device_setting,"/deviceSetting/")


device_value_config=reqparse.RequestParser()
device_value_config.add_argument("deviceId",type=str,help="deviceId is required",required=True)
device_value_config.add_argument("minimumPh",type=float,help="minimum pH value",required=True)
device_value_config.add_argument("maximumPh",type=float,help="maximum pH value",required=True)
device_value_config.add_argument("minimumORP",type=int,help="minimum ORP value",required=True)
device_value_config.add_argument("maximumORP",type=int,help="maximum ORP value",required=True)
device_value_config.add_argument("minimumTemperature",type=int,help="minimum temperature value",required=True)
device_value_config.add_argument("maximumTemperature",type=int,help="maximum temperature value",required=True)

class DeviceValueSetting(Resource):
    def patch(self):
        args=device_value_config.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"editSetting":"Failed","error":"Device is not found"},HTTPStatus.NOT_FOUND)
        
        if args.get("minimumPh") is not None and args.get("maximumPh") is not None and (args.get("minimumPh")<args.get("maximumPh")):
            device.minimumPh=args.get("minimumPh")
            device.maximumPh=args.get("maximumPh")

        else:
            return ({"editSetting":"failed","error":"minimum pH value should be less than maximum pH"},HTTPStatus.BAD_REQUEST)
       

        if args.get("minimumORP") is not None and args.get("maximumORP") is not None and (args.get("minimumORP") < args.get("maximumORP")):
            device.minimumORP=args.get("minimumORP")
            device.maximumORP=args.get("maximumORP")

        else:
            return ({"editSetting":"failed","error":"minimum ORP value should be less than maximum ORP"},HTTPStatus.BAD_REQUEST)
           

        if args.get("minimumTemperature") is not None and args.get("maximumTemperature") is not None and (args.get("minimumTemperature") < args.get("maximumTemperature")):
            device.minimumTemperature=args.get("minimumTemperature")
            device.maximumTemperature=args.get("maximumTemperature")

        else:
            return ({"editSetting":"failed","error":"minimum Temperature value should be less than maximum Temperature"},HTTPStatus.BAD_REQUEST)
           
        
        device.save()
        return ({"editSetting":"Success"},HTTPStatus.OK)
        
api.add_resource(DeviceValueSetting,"/deviceValueConfig/")     


device_mqtt_config=reqparse.RequestParser()
device_mqtt_config.add_argument("deviceId",type=str,help="deviceId is required",required=True)
device_mqtt_config.add_argument("mqttTopicRead",type=str,help="readingMqttTopic is required",required=True)
device_mqtt_config.add_argument("mqttTopicWrite",type=str,help="sendingMqttTopic is required",required=True)
# device_mqtt_config.add_argument("mqttTopic",type=str,help="mqttTopic is required",required=True)

class DeviceMqttSetting(Resource):
    def patch(self):
        args=device_mqtt_config.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"editSetting":"Failed","error":"Device is not found"},HTTPStatus.NOT_FOUND)
        
        if args.get("mqttTopicRead") is not None:
            device.readingMqttTopic=args.get("mqttTopicRead")
        if args.get("mqttTopicWrite") is not None:
            device.sendingMqttTopic=args.get("mqttTopicWrite")
        # if args.get("mqttTopic") is not None:
        #     device.mqttTopic=args.get("mqttTopic")
        
        device.save()
        return ({"editSetting":"Success"},HTTPStatus.OK)

api.add_resource(DeviceMqttSetting,"/devicemqttconfig/")

device_on_off=reqparse.RequestParser()
device_on_off.add_argument("deviceId",type=str,help="Device ID is required",required=True)
device_on_off.add_argument("onOff",type=str,help="On or Off is required",required=True)

class DeviceFilterFeedPumpOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic, "Filter Feed pump",args.get("onOff"))
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)

api.add_resource(DeviceFilterFeedPumpOnOff,"/deviceFilterFeedPumpOnOff/")

class DeviceOzonePumpOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Ozone Pump",args.get("onOff"))
        device.deviceOzonePumpOnOff =  args.get("onOff") 
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)

api.add_resource(DeviceOzonePumpOnOff,"/deviceOzonePumpOnOff/")

class DeviceOxygenGeneratorOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Oxygen Generator",args.get("onOff"))
        device.deviceOxygenGeneratorOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)

api.add_resource(DeviceOxygenGeneratorOnOff,"/deviceOxygenGeneratorOnOff/")

class DeviceOzoneGeneratorOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Ozone Generator",args.get("onOff"))
        device.deviceOzoneGeneratorOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)
api.add_resource(DeviceOzoneGeneratorOnOff,"/deviceOzoneGeneratorOnOff/")

class DevicePhDosingPumpOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"PH Dosing Pump", args.get("onOff"))
        device.devicePhDosingPumpOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)
api.add_resource(DevicePhDosingPumpOnOff,"/devicePhDosingPumpOnOff/")

class DeviceFlocculantDosingPumpOnOff(Resource):

    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Flocculant Dosing Pump", args.get("onOff"))
        device.deviceFlocculantDosingPumpOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)
api.add_resource(DeviceFlocculantDosingPumpOnOff,"/deviceFlocculantDosingPumpOnOff/")

class DeviceCoagulantDosingPumpOnOff(Resource):
    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Coagulant Dosing Pump", args.get("onOff"))
        device.deviceCoagulantDosingPumpOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)
api.add_resource(DeviceCoagulantDosingPumpOnOff,"/deviceCoagulantDosingPumpOnOff/")

class DeviceBackwashValveOnOff(Resource):
    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Backwash Valve", args.get("onOff"))
        device.deviceBackwashValveOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)
api.add_resource(DeviceBackwashValveOnOff,"/deviceBackwashValveOnOff/")

class DeviceChlorineDosingPumpOnOff(Resource):
    def patch(self):
        args=device_on_off.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"deviceOnOff":"Failed","error":"Device not found"},HTTPStatus.NOT_FOUND)
        if device.sendingMqttTopic is None:
            return ({"deviceOnOff":"Failed","error":"Device MQTT topic not configured"},HTTPStatus.BAD_REQUEST)
        topic = device.sendingMqttTopic
        on_off(topic,"Chlorine Dosing Pump", args.get("onOff"))
        device.deviceChlorineDosingPumpOnOff = args.get("onOff")
        device.save()
        return ({"deviceOnOff":"Success"},HTTPStatus.OK)    
api.add_resource(DeviceChlorineDosingPumpOnOff,"/deviceChlorineDosingPumpOnOff/")

# device_detail_args=reqparse.RequestParser()
# device_detail_args.add_argument("deviceId",type="str",help="DEVICEID",required=True)

class GetDeviceData(Resource):
    MQTT_BROKER = "broker.hivemq.com"  # Use your own broker for production
    MQTT_PORT = 1883

    def get_data_from_device(self,topic, timeout=5):
        # topic = f"device/{user_id}/data"
        output = {}  # this will be updated from the MQTT callback
        message_received = threading.Event() 

        def on_connect(client, userdata, flags, rc, properties=None):
            print(f"Connected to MQTT broker with code {rc}")
            client.subscribe(topic)

        def on_message(client, userdata, msg):
            nonlocal output
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
            for i in list:
                if i.get("name")=="Data_1":
                    output['ph'] = i.get("data")[0]
                    output['temperature'] = i.get("data")[1]
                if i.get("name")=="Data_2":
                    output['orp'] = i.get("data")[0]
                    output['ozoneLevel'] = i.get("data")[2]
                if i.get("name")=="Data_3":
                    if i.get("data")[25]==0:
                        output['power']= False
                    else:
                        output['power']= True
            # for i in list:
            # nonlocal received_message
            # received_message = msg.payload.decode()
            # print(f" Received from topic '{msg.topic}': {received_message}")
            message_received.set()  
            client.disconnect()  # Exit loop_forever() and end thread

        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)

        # Start MQTT loop in a separate thread
        mqtt_thread = threading.Thread(target=client.loop_forever)
        mqtt_thread.start()

        # Wait for message or timeout
        # mqtt_thread.join(timeout=timeout)
        # client.disconnect()  # Just in case timeout happens before disconnect in on_message
        message_received.wait(timeout=timeout)
        try:
            client.disconnect()
        except:
            pass
        mqtt_thread.join(timeout=1)

        return output if output else None

    def get(self):
        # args=device_detail_args.parse_args()
        device = DeviceModel.objects.filter(deviceId=request.args.get("deviceId")).first()
        if device is None:
            return {
                "status": "failed",
                "message": "Device not found"
            }, 404
        topic = device.readingMqttTopic
        if not topic:
            return {
                "status": "failed",
                "message": "Device MQTT topic not configured"
            }, 400
        data = self.get_data_from_device(topic, timeout=5)
        if data:
            data['minimumPh'] = device.minimumPh
            data['maximumPh'] = device.maximumPh
            data['minimumORP'] = device.minimumORP
            data['maximumORP'] = device.maximumORP
            data['minimumTemperature'] = device.minimumTemperature
            data['maximumTemperature'] = device.maximumTemperature
            return {
                "status": "success",
                "user_id": topic,
                "data": data
            }, 200
        else:
            return {
                "status": "timeout",
                "user_id": topic,
                "message": f"No data received from device in time for user {topic}"
            }, 504

# Register API endpoint
api.add_resource(GetDeviceData, '/detail/')
