from mongoengine import *
from datetime import datetime

connect('DataBase')

class DeviceRecord(Document):
    # deviceId=StringField(unique=True,required=True)

    topic = StringField(required=True)
    timestamp = DateTimeField(required=True,default=datetime.now() )

    pH = FloatField(required=True)
    waterTemperature = FloatField(required=True)
    waterLinePressure = FloatField(required=True)
    mosfetTemperature = FloatField(required=True)
    ozoneModuleCurrent = FloatField(required=True)
    o3OperatingFrequency = FloatField(required=True)
    oxygenFlow = FloatField(required=True)
    

    ORP = IntField(required=True)
    DCBusVoltage = IntField(required=True)
    ozonePowerinWatts = IntField(required=True)
    ozoneConcentration = IntField(required=True)
    oxygenPurity = IntField(required=True)
    ambientOzone = IntField(required=True)

    filterFeedPump = BooleanField(required=True)
    ozoneBoosterPump = BooleanField(required=True)
    oxygenGenerator = BooleanField(required=True)
    ozoneGenerator = BooleanField(required=True)
    ozoneDestructor = BooleanField(required=True)
    dosingPumpPH = BooleanField(required=True)
    # dummy1 = BooleanField(required=True)
    ozoneON = BooleanField(required=True)
    alarmOzoneTrippedByLowPower = BooleanField(required=True)
    alarmOzoneTrippedByHighPower = BooleanField(required=True)
    alarmOzoneTrippedByMosfet1Fault = BooleanField(required=True)
    alarmOzoneTrippedByMosfet2Fault = BooleanField(required=True)
    alarmOzoneTrippedByMosfet3Fault = BooleanField(required=True)
    alarmOzoneTrippedByMosfet4Fault = BooleanField(required=True)
    alarmOzoneTrippedByTemperatureFault = BooleanField(required=True)
    alarmOzoneTrippedByLoadFault = BooleanField(required=True)
    alarmOzoneTrippedFault = BooleanField(required=True)
    alarmOzoneTrippedByInrushVoltageFault = BooleanField(required=True)
    # dummy2 = BooleanField(required=True)
    alarmOxygenPurityLow = BooleanField(required=True)
    alarmAmbientOzoneLevelHigh = BooleanField(required=True)
    warningPHLevelHigh = BooleanField(required=True)
    warningPHLevelLow = BooleanField(required=True)
    systemStart = BooleanField(required=True)
    forceTurnONFilterFeedPump = BooleanField(required=True)
    forceTurnONOzonePump = BooleanField(required=True)
    forceTurnONOxygenGenerator = BooleanField(required=True)
    forceTurnONOzoneGenerator = BooleanField(required=True)
    forceTurnONPHDosingPump = BooleanField(required=True)
    forceTurnONFloccDosingPump = BooleanField(required=True)
    forceTurnONCoagDosingPump = BooleanField(required=True)
    forceTurnONBackWashValve = BooleanField(required=True)
    forceTurnONChlorineDosingPump = BooleanField(required=True)
    # dummy3 = BooleanField(required=True)
    dosingPumpFlocculation = BooleanField(required=True)
    dosingPumpCoggulation = BooleanField(required=True)
    ozoneEnable = BooleanField(required=True)
    lampGreen = BooleanField(required=True)
    lampYellow = BooleanField(required=True)
    lampRed = BooleanField(required=True)
    hooter = BooleanField(required=True)
    # dummy4 = BooleanField(required=True)


    warningPHDosingTankLevelLow = BooleanField(required=True)
    warningFloccDosingTankLevelLow = BooleanField(required=True)
    warningCoaggDosingTankLevelLow = BooleanField(required=True)
    alarmFeedWaterPumpPressureLow = BooleanField(required=True)
    alarmOzoneBoosterPumpPressureLow = BooleanField(required=True)
    # dummy5 = BooleanField(required=True)


    def __repr__(self):
        return f"{self.topic}"
