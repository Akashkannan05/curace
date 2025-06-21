import os
import smtplib
from dotenv import load_dotenv

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from config import DevlopmentConfig, ProductionConfig,Config
from Users.users import user_bp
from Organization.organization import organization_bp

load_dotenv()  

app = Flask(__name__)
app.config.from_object(Config)

app.config.setdefault('JWT_SECRET_KEY', "a763b1ba79ead83dc155359b60f86d9a38212c3958fe7f7530681aa49d035d4e")

api = Api(app)

CORS(
    app,
    resources=app.config.get("CORS_RESOURCES", {}),
    supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", False)
)

jwt = JWTManager(app)
mail = Mail(app)  
app.mail=mail



app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(organization_bp,url_prefix="/organization")

if __name__ == "__main__":
    app.run(debug=True)
