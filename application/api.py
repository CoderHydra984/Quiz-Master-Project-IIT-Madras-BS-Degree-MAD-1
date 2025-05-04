from flask import request,jsonify
from flask_restful import Resource
from application.models import *
from application.functions import *
from datetime import datetime
from sqlalchemy import func

class QuestionsAPI(Resource):
    def get(self,chap_id):
        chap_id = int(chap_id)
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()
        if chapter:
            return {"Chapter Name": chapter.name,
                    "Chapter Description": chapter.description,
                    "Subject ID":chapter.subject_id,
                    "No. of Questions": db.session.query(func.count(Questions.id)).filter(Questions.chapter_id == chapter.id).scalar(),
                    "Questions List":[question.question_statement for question in chapter.questions]}
        return {"Error": f"No chapter found with the id {chap_id}"}

class UserAPI(Resource):
    def get(self,username,inp_pass):
        user = db.session.query(User).filter_by(username=username).first()
        if user:
            if check_user(user,inp_pass):
                return {"ID":user.id,
                        "username":user.username,
                        "Full name":user.first_name + ' ' + user.last_name,
                        "Qualifications":user.qualification,
                        "D.O.B":user.dob}
            else:
                return {"Error":"Unauthorized Access"}
        return {"Error":"Username does not exist"}
    
    def post(self,username):
        inp_pass = request.json.get('password')
        user = db.session.query(User).filter_by(username=username).first()
        print("Get userename",username)
        if user:
            if check_user(user,inp_pass):
                first_name = request.json.get('first_name')
                last_name =  request.json.get('last_name')
                qualification = request.json.get('qualification')
                dob = request.json.get('dob')
                if dob:
                    try:
                        valid_dob = datetime.strptime(dob, "%Y-%m-%d")
                    except ValueError:
                        return {"Error": "Invalid Date Entered"}
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if qualification:
                    user.qualification = qualification
                if dob:
                    user.dob = str(valid_dob)[:10]
                db.session.commit()
                return {"ID":user.id,
                    "username":user.username,
                    "Full name":user.first_name + ' ' + user.last_name,
                    "Qualifications":user.qualification,
                    "D.O.B":user.dob}
            else:
                return {"Error":"Unauthorized Access"}
        return {"Error":"Username does not exist"}
