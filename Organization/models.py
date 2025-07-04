from mongoengine import *
from datetime import date

class OrganizationModel(Document):
    orgId=IntField()
    name=StringField(required=True)
    status=StringField(required=True,choices=['Pending','Active','Inactive'],default='Pending')
    contactName=StringField(max_length=50,required=True)
    phoneNo=StringField(max_length=20,required=True)
    email=EmailField(unique=True,required=True)
    address=StringField(required=True)
    city=StringField(required=True)
    state=StringField(required=True)
    country=StringField(required=True)
    customerType=StringField(choices=['Owner','Patner','End Customer',"Partner"],required=True)
    createdOn=DateField(default=date.today)
    assocaiteBy=ObjectIdField(required=False,null=True)
    createdBy=ObjectIdField(required=False,null=True)

    def __repr__(self):
        return f"{self.name}-{self.customerType}-{self.status}"