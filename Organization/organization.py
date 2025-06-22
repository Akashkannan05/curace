import os

from flask import Blueprint,jsonify,current_app
from flask_restful import Api,Resource,reqparse
from flask_jwt_extended import  jwt_required, get_jwt_identity
from flask_mail import Mail, Message

from dotenv import load_dotenv
from cryptography.fernet import Fernet

from mongoengine import *
from http import HTTPStatus

from .models import OrganizationModel
from Users.models import UserModel

organization_bp=Blueprint("organization",__name__)
api=Api(organization_bp)
load_dotenv()
fernet=Fernet(os.getenv('ENCRYPTION_KEY').encode())

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
        organization=OrganizationModel(name="Faraday Ozone",contactName="Company",email="akash2005k26kaniyur12@gmail.com",customerType="Owner",status="Active",
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
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            
            if current_user is None:
                return ({"addOrganization":"failed","error":"specify the organization"},HTTPStatus.BAD_REQUEST)
            current_organization=current_organization.customerType
            check_email=OrganizationModel.objects.filter(email=args.get('email')).first()
            if check_email is not None:
                return ({"addOrganization":"failed","error":"Email id already exisit"},HTTPStatus.BAD_REQUEST)
            if args.get('customerType')!='End Customer' and current_organization!="Owner":
                return ({"addOrganization":"failed","error":"Only the owner can add the patner or another owner"},HTTPStatus.BAD_REQUEST)
            
            organization=OrganizationModel(
                name=args.get("organizationName"),
                status="Pending",
                contactName=args.get('contactName'),
                phoneNo=args.get('phoneNo'),
                email=args.get('email'),
                address=args.get('address'),
                city=args.get('city'),
                state=args.get('state'),
                country=args.get('country'),
                customerType=args.get('customerType'),
                assocaiteBy=current_user.organization
            )
            organization.save()
            frontend_url="http://localhost:5173/set-password/"
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
            return ({"addOrganization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)
    
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

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            args=change_status_organization_args.parse_args()
            objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            if current_user.userRole!="Admin" or current_user.status!="Active":
                return ({"activateOrganization":"failed","error":"Only active admin can change the status"},HTTPStatus.BAD_REQUEST)
            change_organization=OrganizationModel.objects.filter(pk=objectId).first()
            if change_organization is None:
                return ({"activateOrganization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            if current_user.organization!=change_organization.assocaiteBy or not(current_organization is not None and current_organization.customerType=="Owner"):
                return ({"activateOrganization":"failed","error":"Only you can change the organization under you or assosiated by you"},HTTPStatus.NOT_FOUND)
            change_organization.status='Active'
            change_organization.save()
            return ({"activateOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"activateOrganization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"activateOrganization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(ActivateOrganizationResource,'/activate/')

class InactivateOrganizationResource(Resource):

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            args=change_status_organization_args.parse_args()
            objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            current_user=UserModel.objects.get(email=current_user_email)
            if not (current_user.userRole=="Admin" and current_user.status=="Active"):
                return ({"inactivateOrganization":"failed","error":"Only active admin can change the status"},HTTPStatus.BAD_REQUEST)
            change_organization=OrganizationModel.objects.filter(pk=objectId).first()
            if change_organization is None:
                return ({"inactivateOrganization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            current_organization=OrganizationModel.objects.filter(pk=current_user.organization).first()
            if current_user.organization!=change_organization.assocaiteBy or not(current_organization is not None and current_organization.customerType=="Owner"):
                return ({"inactivateOrganization":"failed","error":"Only you can change the organization under you  or assosiated by you"},HTTPStatus.NOT_FOUND)
            change_organization.status='Inactive'
            change_organization.save()
            return ({"inactivateOrganization":"success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"inactivateOrganization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"inactivateOrganization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(InactivateOrganizationResource,'/inactivate/')

# detail_organization_args=reqparse.RequestParser()
# detail_organization_args.add_argument("objectId",type=str,help="Enter the objectid",required=True)

class DetailOrganizationResource(Resource):

    @jwt_required()
    def get(self,objectId):
        try:
            if objectId is None:
                return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            objectId=fernet.decrypt(objectId.encode()).decode()
            # args=detail_organization_args.parse_args()
            current_user_email=get_jwt_identity()
            user=UserModel.objects.get(email=current_user_email)
            user_organization=OrganizationModel.objects.filter(pk=user.organization).first()
            if user_organization is None:
                return ({"organization":"failed","error":"User does not belong to this organization"},HTTPStatus.BAD_REQUEST)
            organization=OrganizationModel.objects.filter(pk=objectId).first()
            if organization is None:
                return ({"organization":"failed","error":"There is no organization with this objectId"},HTTPStatus.NOT_FOUND)
            if organization.assocaiteBy!=user_organization.pk:
                return ({"organization":"failed","error":"You can only access the details of your associated organization"},HTTPStatus.BAD_REQUEST)
            #Statistics still to do after the device section
            contactInformation={
                "contactName":organization.contactName,
                "email":organization.email,
                "phoneNo":organization.phoneNo
            }
            location={
                "address":organization.address,
                "city":organization.city,
                "state":organization.state,
                "country":organization.country
            }
            organization_list_qs=OrganizationModel.objects.filter(assocaiteBy=organization.pk)
            if organization_list_qs :
                organization_list=[org.to_mongo().to_dict() for org in organization_list_qs]
            users_list_qs=UserModel.objects.filter(organization=objectId)
            if users_list_qs:
                user_list=[user.to_mongo().to_dict() for user in users_list_qs]
            #Still devices in need to be done
            return ({
                "name":organization.name,
                "customerType":organization.customerType,
                "assocaiteBy":organization.assocaiteBy,
                "status":organization.status,
                "contactInformation":contactInformation,
                "location":location,
                "organizations":organization_list,
                "users":user_list
            })

        except DoesNotExist as e:
            return ({"organization":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"organization":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(DetailOrganizationResource,'/detail/<string:objectId>')