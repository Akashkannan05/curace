from mongoengine import *
from datetime import date
from dotenv import load_dotenv

load_dotenv()
connect(db='ozopool_iot',
        host="62.72.13.179",
        port=27017,
        username="ozopool_iot",
        password="Faraday@2023",
        authentication_source= "ozopool_iot"
)


class DeviceModel(Document):
    deviceId= StringField(unique=True,required=True)
    customerName=StringField(required=True)
    city=StringField(required=True)
    state=StringField(required=True)
    poolStatus=StringField(choices=['Excellent','Good','Need attention','Not Recommended'],required=True)
    createdOn=DateField(default=date.today)
    organization=ObjectIdField(required=True)
    createdBy=ObjectIdField(required=True)

    minimumPh=FloatField(default=6.8)
    maximumPh=FloatField(default=7.6)
    minimumORP=IntField(default=250)
    maximumORP=IntField(default=950)
    minimumTemperature=IntField(default=26)
    maximumTemperature=IntField(default=32)
    
    readingMqttTopic=StringField()
    sendingMqttTopic=StringField()
    mqttTopic=StringField(required=True)


    def __repr__(self):
        return f"{self.deviceId}-{self.customerName}"