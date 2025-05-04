import os
from flask import Flask
from flask_restful import Resource,Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db

app = None
api = None

def create_app():
    app = Flask(__name__,template_folder="templates")
    if os.getenv('ENV',"development") == 'production':
        raise Exception("No production config is setup yet.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
        db.init_app(app)
        api = Api(app)
        app.app_context().push()
        return app , api
    
app, api = create_app()

# Import all the controllers 
from application.controllers import *

# Import all restful controllers
from application.api import UserAPI,QuestionsAPI
# from application.api import *
api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>", "/api/user/<string:username>/<string:inp_pass>")
api.add_resource(QuestionsAPI,"/api/questions_of_chapter/<int:chap_id>")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)