from flask import Blueprint,jsonify
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

device_bp=Blueprint("device",__name__)
api=Api(device_bp)

load_dotenv()
fernet=Fernet(os.getenv('ENCRYPTION_KEY').encode())



put_args_addDevice=reqparse.RequestParser()
put_args_addDevice.add_argument("organizationId",type=str,help="Organization ID required",required=False)
put_args_addDevice.add_argument("deviceId",type=str,help="Device ID required",required=True)
put_args_addDevice.add_argument('mqttTopic',type=str,help="Mqtt topic is required",required=True)

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
            mqttTopic=args.get('mqttTopic')

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
            dt = datetime.strptime(str(i.createdOn), "%a, %d %b %Y %H:%M:%S %Z")
            formatted_date = dt.strftime("%Y-%m-%d")
            dictionary={
                "deviceId":i.deviceId,
                "customer":i.customerName,
                "city":i.city,
                "state":i.state,
                "poolStatus":i.poolStatus,
                "createdOn":formatted_date
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
device_mqtt_config.add_argument("readingMqttTopic",type=str,help="readingMqttTopic is required",required=True)
device_mqtt_config.add_argument("sendingMqttTopic",type=str,help="sendingMqttTopic is required",required=True)
# device_mqtt_config.add_argument("mqttTopic",type=str,help="mqttTopic is required",required=True)

class DeviceMqttSetting(Resource):
    def patch(self):
        args=device_mqtt_config.parse_args()
        device=DeviceModel.objects.filter(deviceId=args.get("deviceId")).first()
        if device is None:
            return ({"editSetting":"Failed","error":"Device is not found"},HTTPStatus.NOT_FOUND)
        
        if args.get("readingMqttTopic") is not None:
            device.readingMqttTopic=args.get("readingMqttTopic")
        if args.get("sendingMqttTopic") is not None:
            device.sendingMqttTopic=args.get("sendingMqttTopic")
        # if args.get("mqttTopic") is not None:
        #     device.mqttTopic=args.get("mqttTopic")
        
        device.save()
        return ({"editSetting":"Success"},HTTPStatus.OK)

api.add_resource(DeviceMqttSetting,"/devicemqttconfig/")
