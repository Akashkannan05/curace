from mongoengine import *
from datetime import date
from dotenv import load_dotenv

# connect('DataBase')

load_dotenv()
connect(db='ozopool_iot',
        host="62.72.13.179",
        port=27017,
        username="ozopool_iot",
        password="Faraday@2023",
        authentication_source= "ozopool_iot"
)



class UserModel(Document):
    username=StringField(max_length=50,required=True)
    password=StringField(required=False)
    email=EmailField(required=True,unique=True)
    userRole=StringField(choices=["Admin","Engineer", "Executive"])
    organization=ObjectIdField(required=False,null=True)
    assocaiteBy=ReferenceField('self',required=False,null=True)
    createdBy=ReferenceField('self',required=False,null=True)
    status=StringField(choices=['Pending','Active','Inactive'],default='Pending')
    createdOn=DateField(default=date.today)
    organizationColumns=ListField(default=['status','contactName','phoneNo','email','address','city','state','country','customerType'])

    def clean(self):
        if not self.password and self.status!='Pending':
            raise ValidationError("password cant be null while the user is activate")
        if len(self.username)==0:
            raise ValidationError("Username cant be Zero")
    
    def __repr__(self):
        return f"{self.username}-{self.userRole}-{self.status}"
        