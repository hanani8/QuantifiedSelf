import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "The Most Basic" #Used for session and cookie creation
    SECURITY_PASSWORD_HASH = "bcrypt" #sha512_crypt, or pbkdf2_sha512 can also be used
    SECURITY_PASSWORD_SALT = "The Beauty of War Lies in the Rage of It" #Prefixed to the password before hashing
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    

