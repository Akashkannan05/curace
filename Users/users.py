import os

from flask import Blueprint,jsonify,current_app,request
from flask_restful import Api,Resource,reqparse
from flask_jwt_extended import  create_access_token,jwt_required, get_jwt_identity
from flask_mail import Mail, Message

from dotenv import load_dotenv
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash,check_password_hash
from mongoengine import *
from http import HTTPStatus

# from app import jwt
from .models import UserModel
from Organization.models import OrganizationModel

user_bp=Blueprint("user",__name__)
api=Api(user_bp)
# mail=Mail(user_bp)
load_dotenv()
fernet=Fernet(os.getenv('ENCRYPTION_KEY').encode())


class UserAlreadyExists(Exception):
    """Raised when user already exists."""
    pass

class UserDoesnotExisits(Exception):
    """Raised when user does not exists."""
    pass

def removeTimeFromDate(date):
    List=str(date.split(" "))
    return List[0]+List[1]+List[2]+List[3]

class HelloWorld(Resource):
    def get(self):
        return ({"msg":"Hello WORLD"})

api.add_resource(HelloWorld,"/hello/")
user_login_args=reqparse.RequestParser()
user_login_args.add_argument("email",type=str,help="email required!Please enter the email",required=True)
user_login_args.add_argument("password",type=str,help="password required! Please enter the password",required=True)

class UserLoginResourse(Resource):
    def post(self):
        args=user_login_args.parse_args()
        try:
            user=UserModel.objects.get(email=args.get('email'))
            print(user.email,user.userRole)
            if user.status=='Inactive':
                return ({"login":"failed","error":"Your account is inactive"},HTTPStatus.UNAUTHORIZED)
            if user.status=='Pending':
                return ({"login":"failed","error":"Your account is pending"},HTTPStatus.UNAUTHORIZED)
            if not check_password_hash(user.password,args.get('password')):
               return ({"login":"failed","error":"Enter the correct password"},HTTPStatus.UNAUTHORIZED)
            organization=OrganizationModel.objects.filter(pk=user.organization).first()
            access_token=create_access_token(identity=args.get('email'))
            if organization is None:
                customerType="Not filled yet"
            else:
                customerType=organization.customerType
            if user.userRole is None:
                userRole="Not filled yet"
            else:
                userRole=user.userRole
                # return ({"login":"success","accessToken":access_token,"customerType":"Not filled yet"},HTTPStatus.OK)
            return ({"login":"success","accessToken":access_token,"customerType":customerType,"userRole":userRole,"userId":fernet.encrypt(str(user.pk).encode()).decode()},HTTPStatus.OK)
        except DoesNotExist as e:
            #raise UserDoesnotExisits("A user with this email does not  exists.")
            return ({"login":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            #raise ValidationError(e) 
            return ({"login":"failed","error":str(e)},HTTPStatus.CONFLICT)
    
    def get(self):
        # user=UserModel(username="Ozone faraday",email="akash2005k26kaniyur12@gmail.com",userRole="Admin",password=generate_password_hash("pass143"),status="Active")
        # user.save()  
        # return {"username":"Ozone faraday"}
        user=UserModel.objects.filter(email="akash2005k26kaniyur12@gmail.com").first()
        user.password=generate_password_hash("pass")
        user.save()
        # organization=OrganizationModel.objects.filter(email="akash2005k26kaniyur12@gmail.com").first()
        # user=UserModel(username="Ashwin K ",email="akash2005kaniyur12@gmail.com",userRole="Engineer",password=generate_password_hash("pass143"),status="Active",organization=organization.pk)
        # user.save()
        # return {"username":"Ozone faraday"}
        
api.add_resource(UserLoginResourse,'/login/')


add_user_args=reqparse.RequestParser()
#add_user_args.add_argument('accessToken',type=str,help="Please provide the access token",required=True)\
# add_user_args.add_argument('objectId',type=str,help="please provide the objectID",required=False)
add_user_args.add_argument('username',type=str,help="please provide the username",required=True)
add_user_args.add_argument('email',type=str,help="Please provide the email",required=True)
add_user_args.add_argument('userRole',type=str,help="Please provide the user role",required=True)

class AddUserResourse(Resource):

    @jwt_required()
    def post(self):
        try:
            mail = current_app.mail
            print("STRAT_____________")
            args=add_user_args.parse_args()
            
            
            current_user_email=get_jwt_identity()
            user=UserModel.objects.filter(email=current_user_email).first()
            if not user:
                return ({"user":"failed","error":f"Can't find the user with provided email {current_user_email}"},HTTPStatus.NOT_FOUND)
            if user.userRole!="Admin":
                return ({"user":"failed","error":"Only Admin user can add another user"},HTTPStatus.NOT_ACCEPTABLE)
            if user.status!="Active":
                return ({"user":"failed","error":"Only acitive admin can add another user"},HTTPStatus.UNAUTHORIZED)
            # objectId=args.get('objectId')
            # if objectId is not None:
            #     objectId=fernet.decrypt(objectId.encode()).decode()
            #     assosiatedBY=UserModel.objects.filter(pk=objectId).first()
            #     if assosiatedBY is None:
            #         return ({"user":"failed","error":"There is no user with this objectId"},HTTPStatus.NOT_FOUND)
            #     if assosiatedBY.status=='Pending':
            #         return ({"user":"failed","error":"Can not add the user until he set the password"},HTTPStatus.BAD_REQUEST)
            # else:
            assosiatedBY=user
            new_user=UserModel(
                username=args.get('username'),
                email=args.get('email'),
                userRole=args.get('userRole'),
                organization=user.organization,
                assocaiteBy=assosiatedBY,
                createdBy=user,
                password=None,  # Password will be set later
                status='Pending'
                )
            new_user.save()
            frontend_url="http://localhost:5173/#/set-password/"
            encrypted_email=fernet.encrypt(args.get('email').encode()).decode()
            body=f"This email is to inform the request of the adding user with this email use this link to set password and Active the account {frontend_url}{encrypted_email}"
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
            return ({"user":"success","msg":"user was added successfully"})
        except Exception as e:
            return ({"user":"failed",f"error":"Something went wrong contact admin team{e}"},HTTPStatus.CONFLICT)

api.add_resource(AddUserResourse,'/add/')

add_user_object_args=reqparse.RequestParser()
#add_user_args.add_argument('accessToken',type=str,help="Please provide the access token",required=True)\
add_user_object_args.add_argument('objectId',type=str,help="please provide the objectID",required=True)
add_user_object_args.add_argument('username',type=str,help="please provide the username",required=True)
add_user_object_args.add_argument('email',type=str,help="Please provide the email",required=True)
add_user_object_args.add_argument('userRole',type=str,help="Please provide the user role",required=True)
class AddUserResourceThroughObjectId(Resource):

    @jwt_required()
    def post(self):
        try:
            mail = current_app.mail
            print("STRAT_____________")
            args=add_user_object_args.parse_args()
    
            current_user_email=get_jwt_identity()
            user=UserModel.objects.filter(email=current_user_email).first()
            if not user:
                return ({"user":"failed","error":f"Can't find the user with provided email {current_user_email}"},HTTPStatus.NOT_FOUND)
            if user.userRole!="Admin":
                return ({"user":"failed","error":"Only Admin user can add another user"},HTTPStatus.NOT_ACCEPTABLE)
            if user.status!="Active":
                return ({"user":"failed","error":"Only acitive admin can add another user"},HTTPStatus.UNAUTHORIZED)
            
            objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            assosiatedBY=user
            # if assosiatedBY is None:
            #     return ({"user":"failed","error":"There is no user with this objectId"},HTTPStatus.NOT_FOUND)
            # if assosiatedBY.status=='Pending':
            #     return ({"user":"failed","error":"Can not add the user until he set the password"},HTTPStatus.BAD_REQUEST)
            
            new_user=UserModel(
                username=args.get('username'),
                email=args.get('email'),
                userRole=args.get('userRole'),
                organization=objectId,
                assocaiteBy=assosiatedBY,
                createdBy=user,
                password=None,  # Password will be set later
                status='Pending'
                )
            new_user.save()
            frontend_url="http://localhost:5173/#/set-password/"
            encrypted_email=fernet.encrypt(args.get('email').encode()).decode()
            body=f"This email is to inform the request of the adding user with this email use this link to set password and Active the account {frontend_url}{encrypted_email}"
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
            return ({"user":"success","msg":"user was added successfully"})
        except Exception as e:
            return ({"user":"failed","error":f"Something went wrong contact admin team {e}"},HTTPStatus.CONFLICT)

api.add_resource(AddUserResourceThroughObjectId,'/add/objectId/')
#b'gAAAAABoSmL2QQ2N_uROUbIS7aDZHnC_H7BdSul08FzifjvAael23TYcOgUpKQFBF73KTLdx-CpZV2TvKnAKH_R5ZgJlm6FmX6uhFkdsHIuTGuj8dbmgABU='

password_args=reqparse.RequestParser()
# password_args.add_argument("encryption",type=str,help="Encrypted value is required",required=True)
password_args.add_argument("password",type=str,help="password is required",required=True)
password_args.add_argument("confirmPassword",type=str,help="conform password is required",required=True)
class setPasswordResource(Resource):

    def patch(self):
        encryption=request.args.get('encryption')
        if encryption is None:
            return ({"password":"failed","error":"The encryption is not provided"},HTTPStatus.BAD_REQUEST)
        args=password_args.parse_args()
        if args.get('password').strip()=="":
            return ({"password":"failed","error":"password can not be an empty space"},HTTPStatus.BAD_REQUEST)
        if args.get('password')!=args.get('confirmPassword'):
            return ({"password":"failed","error":"password should match the conform password"},HTTPStatus.BAD_REQUEST)
        email=fernet.decrypt(encryption.encode()).decode()
        try:
            user=UserModel.objects.get(email=email)
            print(user.username)
            if user.status!="Pending":
                return ({"password":"failed","error":"Password was already set"},HTTPStatus.BAD_REQUEST)
            user.password=generate_password_hash(args.get('password'))
            user.status='Active'
            user.save()
            return({"password":"success"},HTTPStatus.ACCEPTED)
        except DoesNotExist as e:
            #raise UserDoesnotExisits("A user with this email does not  exists.")
            return ({"password":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"password":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(setPasswordResource,'/set-password/')

class  ListUserResource(Resource):

    @jwt_required()
    def get(self):
        try:
            current_user_email=get_jwt_identity()#akash@GMAIL.COM
            user=UserModel.objects.get(email=current_user_email)
            user_organization=user.organization
            if user_organization is None:
                return({"users":"failed","error":"User does not fill the organization"},HTTPStatus.BAD_REQUEST)
            user_list=UserModel.objects.filter(organization=user_organization)
            print("_________",user_list)
            output=[]
            for i in user_list:
                user_data={}
                user_data['objectId'] = (fernet.encrypt(str(i.pk).encode())).decode()
                user_data['username']=i.username
                user_data['email']=i.email
                user_data['userRole']=i.userRole
                user_data['status']=i.status
                user_data['createdOn']=str(i.createdOn)
                output.append(user_data)
            print(output)
            return (jsonify(output))
        except DoesNotExist as e:
            return ({"users":"failed","error":"There is no account with this email"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"users":"failed","error":f"Something went wrong contact admin team {e}"},HTTPStatus.CONFLICT)

api.add_resource(ListUserResource,"/") 

user_status_args=reqparse.RequestParser()
user_status_args.add_argument('objectId',type=str,help="Please enter the object id",required=True)

class UserStatusActivateResource(Resource):

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"bojectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            args=user_status_args.parse_args()
            objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            user=UserModel.objects.get(email=current_user_email)
            if user.userRole!="Admin":
                return ({"status":"failed","error":"Only Admin user can change the status"},HTTPStatus.UNAUTHORIZED)
            if user.status!="Active":
                return ({"status":"failed","error":"Only acitive admin can change the status"},HTTPStatus.UNAUTHORIZED)
            change_user=UserModel.objects.get(pk=objectId)
            if change_user.status=='Pending':
                return ({"status":"failed","error":"Can not change the status of the user until he set the password"},HTTPStatus.BAD_REQUEST)
            if user.organization!=change_user.organization:
                return ({"status":"failed","error":"Only you can change the member of your organization"},HTTPStatus.UNAUTHORIZED)
            change_user.status="Active"
            change_user.save()
            return ({"status":"Success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"status":"failed","error":"There is no account with this objectId"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"status":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(UserStatusActivateResource,"/activate/")

class UserStatusInactivateResource(Resource):

    @jwt_required()
    def patch(self):
        try:
            args=user_status_args.parse_args()
            # if objectId is None:
            #     return ({"status":"failed","error":"bojectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            objectId=fernet.decrypt(args.get('objectId').encode()).decode()
            current_user_email=get_jwt_identity()
            user=UserModel.objects.get(email=current_user_email)
            if user.userRole!="Admin":
                return ({"status":"failed","error":"Only Admin user can change the status"},HTTPStatus.NOT_ACCEPTABLE)
            if user.status!="Active":
                return ({"status":"failed","error":"Only acitive admin can change the status"},HTTPStatus.UNAUTHORIZED)
            change_user=UserModel.objects.get(pk=objectId)
            if change_user.status=='Pending':
                return ({"status":"failed","error":"Can not change the status of the user until he set the password"},HTTPStatus.BAD_REQUEST)
            if user.organization!=change_user.organization:
                return ({"status":"failed","error":"Only you can change the member of your organization"},HTTPStatus.UNAUTHORIZED)
            if change_user.userRole=='Admin':
                count=len(UserModel.objects.filter(userRole="Admin",organization=user.organization,status='Active'))
                if count<=1:
                    return ({"status":"failed","error":"There must be atleast one active admin"},HTTPStatus.BAD_REQUEST)
            change_user.status="Inactive"
            change_user.save()
            return ({"status":"Success"},HTTPStatus.OK)
        except DoesNotExist as e:
            return ({"status":"failed","error":"There is no account with this objectId"},HTTPStatus.NOT_FOUND)
        except Exception as e:
            return ({"status":"failed","error":"Something went wrong contact admin team"},HTTPStatus.CONFLICT)

api.add_resource(UserStatusInactivateResource,"/inactivate/")


user_edit_args=reqparse.RequestParser()
user_edit_args.add_argument('objectId',type=str,help="Enter the id",required=True)
user_edit_args.add_argument('username',type=str,help="enter the username",required=False)
user_edit_args.add_argument('email',type=str,help="enter the email",required=False)
user_edit_args.add_argument('userRole',type=str,help="Enter the user role",required=False)

class EditUserResource(Resource):

    @jwt_required()
    def patch(self):
        try:
            # if objectId is None:
            #     return ({"status":"failed","error":"objectId is not provided"},HTTPStatus.NOT_ACCEPTABLE)
            # objectId=fernet.decrypt(objectId).decode()
            
            args=user_edit_args.parse_args()
            objectId=fernet.decrypt(args.get('objectId')).decode()
            current_user_email=get_jwt_identity()
            user=UserModel.objects.get(email=current_user_email)
            if user.userRole!="Admin":
                return ({"status":"failed","error":"Only Admin user can edit "},HTTPStatus.NOT_ACCEPTABLE)
            if user.status!="Active":
                return ({"status":"failed","error":"Only acitive admin can edit"},HTTPStatus.UNAUTHORIZED)
            change_user=UserModel.objects.get(pk=objectId)
            if change_user.status=='Pending':
                return ({"status":"failed","error":"Can not edit the user until he set the password"},HTTPStatus.BAD_REQUEST)
            if user.organization!=change_user.organization:
                return ({"status":"failed","error":"Only you can change the member of your organization"},HTTPStatus.UNAUTHORIZED)
            if args.get('username') is not None:
                change_user.username=args.get('username')
            if args.get('email') is not None:
                check_email=UserModel.objects.filter(email=args.get('email')).first()
                if check_email is None:
                    change_user.email=args.get('email')
                else:
                    return({"edit":"failed","error":"The email is already present please try someother password"},HTTPStatus.BAD_REQUEST)
            if args.get('userRole') is not None:
                if args.get('userRole')  not in ["Admin","Engineer", "Executive"]:
                    return ({"edit":"failed","error":"Enter the valid user role"})
                if change_user.userRole=="Admin" and args.get('userRole')!="Admin":
                    count=len(UserModel.objects.filter(userRole="Admin",organization=user.organization,status='Active'))
                    if count<=1:
                        return ({"status":"failed","error":"There must be atleast one active admin"},HTTPStatus.BAD_REQUEST)
                change_user.userRole=args.get('userRole')
            change_user.save()
            return ({"edit":"success"},HTTPStatus.ACCEPTED)
        except DoesNotExist as e:
            return ({"edit":"failed","error":"There is no account with this objectId"},HTTPStatus.NOT_FOUND)
        # except Exception as e:
        #     return ({"edit":"failed","error":f"Something went wrong contact admin team {e}"},HTTPStatus.CONFLICT)

        
api.add_resource(EditUserResource,"/edit/")