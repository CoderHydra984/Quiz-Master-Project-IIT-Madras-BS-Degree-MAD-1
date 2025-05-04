import os
basedir = os.path.abspath(os.path.dirname(__file__))



class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    if not os.path.exists(SQLITE_DB_DIR):
        os.makedirs(SQLITE_DB_DIR)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR,"database_quiz_master.sqlite3")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR,"test_database.sqlite3")
    DEBUG =False

    SECRET_KEY = "mystrongsecretkey123456"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "mystrongsecuritypasswordsalt123456"