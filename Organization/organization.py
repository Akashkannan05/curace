import os

from flask import Blueprint,jsonify,current_app,request,Flask,make_response
from flask_restful import Api,Resource,reqparse
from flask_jwt_extended import  jwt_required, get_jwt_identity
from flask_mail import Mail, Message

from dotenv import load_dotenv
from cryptography.fernet import Fernet

from mongoengine import *
from http import HTTPStatus

from .models import OrganizationModel
from Users.models import UserModel
from devices.models import DeviceModel

organization_bp=Blueprint("organization",__name__)
api=Api(organization_bp)
load_dotenv()
fernet=Fernet(os.getenv('ENCRYPTION_KEY').encode())  #byte stream

class ListOrganizationResource(Resource):

    @jwt_required()
    def get(self):
        try:
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            organization_id=current_user.organization
            organization=OrganizationModel.objects.filter(pk=organization_id).first()
            if organization is None:
               return ({"Organization":"failed","error":"please fill the organozation for user"},HTTPStatus.BAD_REQUEST) 
            if organization.customerType=="Owner":
                organization_list=OrganizationModel.objects.all()
            else:
                organization_list=OrganizationModel.objects.filter(assocaiteBy=organization.pk)
            List=[]
            columns=current_user.organizationColumns
            for i in organization_list:
                organization_data={}
                organization_data['objectId']=fernet.encrypt(str(i.pk).encode()).decode()
                organization_data['organizationName']=i.name
                if 'status' in columns:
                    organization_data['status']=i.status
                if 'contactName' in columns:
                    organization_data['contactName']=i.contactName
                if 'phoneNo' in columns:
                    organization_data['phoneNo']=i.phoneNo
                if 'email' in columns:
                    organization_data['email']=i.email
                if 'address' in columns:
                    organization_data['address']=i.address
                if 'city' in columns:
                    organization_data['city']=i.city	
                if 'state' in columns:
                    organization_data['state']=i.state	
                if 'country' in columns:
                    organization_data['country']=i.country	
                if 'customerType' in columns:
                    organization_data['customerType']=i.customerType
                List.append(organization_data)
            return jsonify(List)
        except DoesNotExist as e:
            return ({"organizations":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"organizations":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(ListOrganizationResource,'/')

add_organization_args=reqparse.RequestParser()
add_organization_args.add_argument("objectId",type=str,help="Enter the ObjectID",required=False)
add_organization_args.add_argument("organizationName",type=str,help="Enter the organization name",required=True)
add_organization_args.add_argument("contactName",type=str,help="Enter the contact name",required=True)
add_organization_args.add_argument("phoneNo",type=str,help="Enter the phone number",required=True)
add_organization_args.add_argument("email",type=str,help="Enter the email",required=True)
add_organization_args.add_argument("customerType",type=str,help="Enter the customer type",required=True)
add_organization_args.add_argument("address",type=str,help="enter the address",required=True)
add_organization_args.add_argument("country",type=str,help="Enter the country",required=True)
add_organization_args.add_argument("state",type=str,help="enter the state",required=True)
add_organization_args.add_argument("city",type=str,help="Enter the city",required=True)

class AddOrganizationResource(Resource):

    def get(slef):
        organization=OrganizationModel(orgId=1,name="Faraday Ozone",contactName="Company",email="akash2005k26kaniyur12@gmail.com",customerType="Owner",status="Active",
        phoneNo="123456789",address="address",city="city",state="state",country="country")                               
        organization.save()
        user=UserModel.objects.get(email="akash2005k26kaniyur12@gmail.com")
        user.organization=organization.pk
        user.save()
        return ({"organization":"Done"})
    
    @jwt_required()
    def post(self):
        try:
            mail = current_app.mail
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            args=add_organization_args.parse_args()
            objectID=args.get('objectId')
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            if current_user is None:
                return ({"addOrganization":"failed","error":"specify the organization"},HTTPStatus.BAD_REQUEST)
            current_organization=current_organization.customerType
            check_email=OrganizationModel.objects.filter(email=args.get('email')).first()
            if check_email is not None:
                return ({"addOrganization":"failed","error":"Email id already exisit"},HTTPStatus.BAD_REQUEST)
            if args.get('customerType')!='End Customer' and current_organization!="Owner":
                return ({"addOrganization":"failed","error":"Only the owner can add the patner or another owner"},HTTPStatus.BAD_REQUEST)
            organization_count=OrganizationModel.objects.all().count()
            if objectID :#if objectID is not None
                organizationqs=OrganizationModel.objects.filter(pk=fernet.decrypt(objectID.encode()).decode()).first()
                if organizationqs:
                    assosatied_organization=organizationqs.pk
                else:
                    return ({"addOrganization":"failed","error":"There is no organization with this ID you requested"},HTTPStatus.BAD_REQUEST)
            else:
                 assosatied_organization=current_user.organization
            organization=OrganizationModel(
                orgId=organization_count+1,
                name=args.get("organizationName"),
                status="Active",
                contactName=args.get('contactName'),
                phoneNo=args.get('phoneNo'),
                email=args.get('email'),
                address=args.get('address'),
                city=args.get('city'),
                state=args.get('state'),
                country=args.get('country'),
                customerType=args.get('customerType'),
                assocaiteBy=assosatied_organization,
                createdBy=current_user.pk
            )
            organization.save()
            print("SAVeEDEDEDED")
            frontend_url="https://iot.ozopool.in/set-password/"
            encrypted_email=fernet.encrypt(args.get('email').encode())
            body=f"This email is to inform the adding organization with this email use this link to  Active the account {frontend_url}{encrypted_email}"
            msg=Message(
                subject="Invitation for user",
                recipients=[args.get('email')],
                body=body
            )            
            msg.html=f"""
                <h1>Use this link {frontend_url}{encrypted_email}</h1>
            """
            mail.send(msg)
            print("_____________>",encrypted_email)
            return ({"addOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"addOrganization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"addOrganization":"failed","error":f"Something went wrong contact admin team {e}"},HTTPStatus.CONFLICT)
    
api.add_resource(AddOrganizationResource,'/add/')

# set_activate_from_pending_args=reqparse.RequestParser()
# set_activate_from_pending_args.add_argument('encryption',type=str,help='Enter the encryption',required=True)

#gAAAAABoTOvEio0ktFf7fVIUIGxx2xfOIGnqxE3D0m0i8w34ELRdlxrmQlQDzto_p29phXrw4AyDtU1h7HThl2dnr0vOsxBvaNUCNjb2gHsKDgPWAnCBluI=

class setActivateFromPendingResource(Resource):
    """To set the pending organization to activate by verifying in the email"""

    def patch(self,objectId):
        try:
            if objectId is None:
                return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            objectId=fernet.decrypt(objectId.encode()).decode()
            # args=set_activate_from_pending_args.parse_args()
            email=fernet.decrypt(objectId).decode()
            organization=OrganizationModel.objects.get(email=email)
            if organization.status!='Pending':
                return ({"setOrganization":"failed","error":"If your account is inactive approach the admin"},HTTPStatus.BAD_REQUEST)
            organization.status='Active'
            organization.save()
            return ({"setOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"setOrganization":"failed","error":"There is no organization with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"setOrganization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)
            
api.add_resource(setActivateFromPendingResource,'/pending/<string:objectId>')

change_status_organization_args=reqparse.RequestParser()
change_status_organization_args.add_argument('objectId',type=str,help="Enter the object ID",required=True)

class ActivateOrganizationResource(Resource):
    # def options(self):
    #     return {}, 200

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            # args=change_status_organization_args.parse_args()
            if 'objectId' not in request.args:
                return ({"activateOrganization":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            print(request.args.get('objectId'))
            objectId=fernet.decrypt(request.args.get('objectId').encode()).decode()
            # objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            print(current_user.userRole)
            if current_user.userRole!="Admin" or current_user.status!="Active":
                return ({"activateOrganization":"failed","error":"Only active admin can change the status"},HTTPStatus.BAD_REQUEST)
            change_organization=OrganizationModel.objects.filter(pk=objectId).first()
            print(change_organization)
            if change_organization is None:
                return ({"activateOrganization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            print("_J_J_J_J)I)")
            if current_organization is None:
                return ({"activateOrganization":"failed","error":"There is no organization for this user organization ID"},HTTPStatus.NOT_FOUND)
            if current_user.organization!=change_organization.assocaiteBy or current_organization.customerType!="Owner":
                return ({"activateOrganization":"failed","error":"Only you can change the organization under you or assosiated by you"},HTTPStatus.NOT_FOUND)
            print("JKJKNBBBBJVHV")
            change_organization.status='Active'
            change_organization.save()
            return ({"activateOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"activateOrganization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            print("HELOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            print(e)
            return ({"activateOrganization":"failed","error":f"Something went wrong contact admin team {e}"},HTTPStatus.CONFLICT)

api.add_resource(ActivateOrganizationResource,'/activate/')

class InactivateOrganizationResource(Resource):

    # def options(self):
    #     return {}, 200
    def options(self):
        headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Methods': 'PATCH, OPTIONS'
        }
        return {}, 200, headers

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            # args=change_status_organization_args.parse_args()
            if 'objectId' not in request.args:
                return ({"activateOrganization":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            objectId=fernet.decrypt(request.args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            if not (current_user.userRole=="Admin" and current_user.status=="Active"):
                return ({"inactivateOrganization":"failed","error":"Only active admin can change the status"},HTTPStatus.BAD_REQUEST)
            change_organization=OrganizationModel.objects.filter(pk=objectId).first()
            if change_organization is None:
                return ({"inactivateOrganization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            if current_organization is None:
                return ({"inactivateOrganization":"failed","error":"There is no organization for this user organization ID"},HTTPStatus.NOT_FOUND)
            if current_user.organization!=change_organization.assocaiteBy or  current_organization.customerType!="Owner":
                return ({"inactivateOrganization":"failed","error":"Only you can change the organization under you  or assosiated by you"},HTTPStatus.NOT_FOUND)
            change_organization.status='Inactive'
            change_organization.save()
            return ({"inactivateOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"inactivateOrganization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"inactivateOrganization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(InactivateOrganizationResource,'/inactivate/', methods=['PATCH', 'OPTIONS'])

# detail_organization_args=reqparse.RequestParser()
# detail_organization_args.add_argument("objectId",type=str,help="Enter the objectid",required=True)

class DetailOrganizationResource(Resource):

    # def options(self, objectId=None):
    #     print("Received OPTIONS preflight request for:", objectId)
    #     return '', 200

    @jwt_required()
    def get(self):
        try:
            print("hello")
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            # args=detail_organization_args.parse_args()
            objectId=fernet.decrypt(request.args.get('objectId').encode()).decode()
            print(objectId)
            current_user_email=get_jwt_identity()
            user=UserModel.objects.get(email=current_user_email)
            user_organization=OrganizationModel.objects.filter(pk=user.organization).first()
            if user_organization is None:
                return ({"organization":"failed","error":"User does not belong to this organization"},HTTPStatus.BAD_REQUEST)
            organization=OrganizationModel.objects.filter(pk=objectId).first()
            if organization is None:
                return ({"organization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            if organization.assocaiteBy is None:
                assocaiteBy=None
            else:
                assocaiteByqs=OrganizationModel.objects.filter(pk=organization.assocaiteBy).first()
                if assocaiteByqs is not None:
                    assocaiteBy=assocaiteByqs.name
                else:
                    assocaiteBy=None
            # if organization.assocaiteBy!=user_organization.pk:
            #     return ({"organization":"failed","error":"You can only access the details of your associated organization"},HTTPStatus.BAD_REQUEST)
            #Statistics still to do after the device section
            print("__________")
            organization_list_qs=OrganizationModel.objects.filter(assocaiteBy=organization.pk)
            organization_list=[]
            print(organization_list)
            if organization_list_qs :
                for i in organization_list_qs:
                    dictionary={
                        "objectId":(fernet.encrypt(str(i.pk).encode())).decode(),
                        "orgId":i.orgId,
                        "customerName":i.contactName,
                        "status":i.status,
                        "state":i.state,
                        "createdOn":str(i.createdOn)
                    }
                    organization_list.append(dictionary)
            users_list_qs=UserModel.objects.filter(organization=objectId)
            user_list=[]
            if users_list_qs:
                for i in users_list_qs:
                    dictionary={
                        "objectId":(fernet.encrypt(str(i.pk).encode())).decode(),
                        "username":i.username,
                        "email":i.email,
                        "role":i.userRole,
                        "status":i.status,
                        "createdOn":str(i.createdOn)
                    }
                    user_list.append(dictionary)
            #Still devices in need to be done
            print(user_list)
            device_list=[]
            device=DeviceModel.objects.filter(organization=organization.pk)
            if device is not None:
                for i in device:
                    dictionary={
                        "id": i.deviceId,
                        "customer": i.customerName,
                        "city": i.city,
                        "state": i.state,
                        "poolStatus": "Excellent",
                        "createdOn": str(i.createdOn)
                    }
                    device_list.append(dictionary)
            return ({"organization":{
                        "id": "ORG001",
                        "organizationName":organization.name,
                        "customerType":organization.customerType,
                        "associatedPartner":assocaiteBy,
                        "status":organization.status,
                        "contactName":organization.contactName,
                        "email":organization.email,
                        "phoneNo":organization.phoneNo,
                        "address":organization.address,
                        "city":organization.city,
                        "state":organization.state,
                        "country":organization.country,
                        "statistics": {
                            "totalDevices": len(device_list),
                            "activeDevices": 10,
                            "needAttention": 1
                            },
                        "devices": device_list,
                        "organizations":organization_list,
                        "users":user_list
            }})

        except DoesNotExist as e:
            return ({"organization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"organization":"failed","error":f"Something went wrong contact admin team{e}"},HTTPStatus.CONFLICT)

api.add_resource(DetailOrganizationResource,'/detail/')#,methods=["GET", "OPTIONS"]

edit_organization_args=reqparse.RequestParser()
edit_organization_args.add_argument("objectId",type=str,help="ID of the organization",required=True)
edit_organization_args.add_argument("organizationName",type=str,help="Name of the organization",required=False)
# edit_organization_args.add_argument("status",type=str,help="Status of the organization",required=False)
edit_organization_args.add_argument("contactName",type=str,help="Contact name of the organization",required=False)
edit_organization_args.add_argument("phoneNo",type=str,help="Phone number of the organization",required=False)
edit_organization_args.add_argument("email",type=str,help="Email of the organization",required=False)
edit_organization_args.add_argument("address",type=str,help="Address of the organization",required=False)
edit_organization_args.add_argument("city",type=str,help="City of the organization",required=False)
edit_organization_args.add_argument("state",type=str,help="State of the organization",required=False)
edit_organization_args.add_argument("country",type=str,help="Country of the organization",required=False)
edit_organization_args.add_argument("customerType",type=str,help="Customer type of the organization",required=False)
class EditOrganizationResource(Resource):

    def options(self):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
            'Access-Control-Allow-Methods': 'PATCH, OPTIONS'
        }
        return {}, 200, headers

    @jwt_required()
    def patch(self):
        args=edit_organization_args.parse_args()
        current_user_email=get_jwt_identity()
        current_user=UserModel.objects.filter(email=current_user_email).first()
        if not current_user:
            return ({"editOrganization":"failed","error": "User not found"}, HTTPStatus.NOT_FOUND)
        organization_id=fernet.decrypt(args.get('objectId').encode()).decode()
        organization=OrganizationModel.objects.filter(pk=organization_id).first()
        if not organization:
            return ({"editOrganization":"failed","error": "Organization not found"}, HTTPStatus.NOT_FOUND)
        current_user_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
        if not current_user_organization:
            return ({"editOrganization":"failed","error": "Current user organization not found"}, HTTPStatus.NOT_FOUND)
        if current_user.organization != organization.assocaiteBy and current_user_organization.customerType != "Owner":
            return ({"editOrganization":"failed","error": "You are not authorized to edit this organization"}, HTTPStatus.UNAUTHORIZED)
        if current_user.userRole != "Admin" or current_user.status != "Active":
            return ({"editOrganization":"failed","error": "Only active admin can edit the organization"}, HTTPStatus.UNAUTHORIZED)
        # Update organization fields if provided
        if args.get('organizationName'):
            organization.name = args.get('organizationName')
        # if args.get('status'):
        #     organization.status = args.get('status')
        if args.get('contactName'):
            organization.contactName = args.get('contactName')
        if args.get('phoneNo'):
            organization.phoneNo = args.get('phoneNo')
        if args.get('email'):
            organization.email = args.get('email')
        if args.get('address'):
            organization.address = args.get('address')
        if args.get('city'):
            organization.city = args.get('city')
        if args.get('state'):
            organization.state = args.get('state')
        if args.get('country'):
            organization.country = args.get('country')
        if args.get('customerType'):
            organization.customerType = args.get('customerType')
        organization.save()
        return ({"editOrganization":"success"}, HTTPStatus.OK)
api.add_resource(EditOrganizationResource, '/edit/')