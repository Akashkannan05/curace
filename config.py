import os
from dotenv import load_dotenv
load_dotenv()

def strToBool(value):
    value=str(value).strip().lower()
    if value=="True":
        return True
    elif value=="False":
        return False
    else:
        raise ValueError("Enter the correct value")

class Config:
    MAIL_SERVER =os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USE_SSL = False
    MAIL_USERNAME=os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')


class DevlopmentConfig(Config):
    DEBUG=True
    TESTING=True
    CORS_SUPPORTS_CREDENTIALS = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING=False
    CORS_SUPPORTS_CREDENTIALS = True        #JWT or cookies used->Use supports_credentials=True