from .database import db
from flask import current_app as app
import bcrypt


# Model definitions
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,nullable=False)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String)
    qualification = db.Column(db.String)
    dob = db.Column(db.String)



class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,nullable=False)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String)
    dob = db.Column(db.String)



class Subject(db.Model):
    __tablename__='subject'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String,nullable=False)
    description = db.Column(db.String)
    is_deleted = db.Column(db.Boolean,nullable=False,default=False)
    chapters = db.relationship('Chapter',back_populates='subject',lazy='select')
    quizzes = db.relationship('Quiz',secondary='quiz_subject',back_populates='subjects',lazy="select")


# Subject Chapters - Each chapter has one subject and each subject can have many chapters
class Chapter(db.Model):
    __tablename__='chapter'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String,nullable=False)
    description = db.Column(db.String)
    subject_id = db.Column(db.Integer,db.ForeignKey('subject.id'),nullable=False)
    subject = db.relationship('Subject', back_populates='chapters')
    is_deleted = db.Column(db.Boolean,nullable=False,default=False)
    questions = db.relationship('Questions',back_populates='chapter')
    quizzes = db.relationship('Quiz',secondary='quiz_chapter',back_populates='chapters',lazy='select')


# Chapter-Questions
class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String)
    date_created = db.Column(db.String,nullable=False)
    deadline = db.Column(db.String)
    time_duration = db.Column(db.String,nullable=False)
    is_published = db.Column(db.Boolean,nullable=False)
    remarks = db.Column(db.String)
    questions = db.relationship('Questions',secondary="quiz_question",back_populates='quizzes',lazy='select')
    chapters = db.relationship('Chapter',secondary='quiz_chapter',back_populates='quizzes',lazy="select")
    subjects = db.relationship('Subject',secondary="quiz_subject",back_populates='quizzes',lazy='select')


# Many-Many relationship b/w Quiz and Questions.
class Quiz_Question(db.Model):
    __tablename__ = 'quiz_question'
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),primary_key=True)
    question_id = db.Column(db.Integer,db.ForeignKey('questions.id'),primary_key=True)

############################ While publishing quiz, delete all unecessary related chapters/subject of that quiz ############################
 
# Many-Many relationship b/w Quiz and Chapters.
class Quiz_Chapter(db.Model):
    __tablename__='quiz_chapter'
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),primary_key=True)
    chapter_id = db.Column(db.Integer,db.ForeignKey('chapter.id'),primary_key=True)

class Quiz_Subject(db.Model):
    __tablename__ = 'quiz_subject'
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),primary_key=True)
    subject_id = db.Column(db.Integer,db.ForeignKey('subject.id'),primary_key=True)
############################################################################################################################################



class Questions(db.Model):
    __tablename__='questions'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    question_statement=db.Column(db.String,nullable=False)
    marks = db.Column(db.Integer,nullable=False)
    negative_marks = db.Column(db.Integer,nullable=False)
    chapter_id = db.Column(db.Integer,db.ForeignKey('chapter.id'),nullable=False)
    is_deleted = db.Column(db.Boolean,nullable=False,default=False)
    quizzes = db.relationship('Quiz',secondary="quiz_question",back_populates='questions',lazy='select')
    options = db.relationship('Options',back_populates='question',lazy='select')
    chapter = db.relationship('Chapter',back_populates='questions',lazy='select')



# one-many: Question-options - each option has one question and each question can have many option 
class Options(db.Model):
    __tablename__='options'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    question_id = db.Column(db.Integer,db.ForeignKey('questions.id'),nullable=False)
    option = db.Column(db.Text,nullable=False)
    is_correct = db.Column(db.Boolean,nullable=False)
    is_deleted = db.Column(db.Boolean,nullable=False,default=False)
    question = db.relationship('Questions',back_populates='options',lazy='select')



class Scores(db.Model):
    __tablename__='scores'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    started_time = db.Column(db.String,nullable=False)
    end_time = db.Column(db.String)
    date_of_attempt = db.Column(db.String,nullable=False)
    marks_obtained = db.Column(db.Numeric)
    attempt_count = db.Column(db.Integer,nullable=False)
    remarks = db.Column(db.String)
    user_answers = db.relationship("User_Answer_Transcript", backref="score", lazy='select')

class User_Answer_Transcript(db.Model):
    __tablename__ = 'user_answer_transcript'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    question_id = db.Column(db.Integer,db.ForeignKey('questions.id'),nullable=False)
    option_id = db.Column(db.Integer,db.ForeignKey('options.id'),nullable=False)
    score_id = db.Column(db.Integer,db.ForeignKey('scores.id'),nullable=False)

def insert_admin():
    if not(db.session.query(Admin).filter_by(username='adminmail@gmail.com').first()):    
        username = 'adminmail@gmail.com'
        password = bcrypt.hashpw('veryhardpassword'.encode('utf-8'), bcrypt.gensalt())
        first_name = 'Loki'
        last_name = 'Lafeyson'
        dob = '1990-09-007'
        admin = Admin(username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    dob=dob)
        db.session.add(admin)
        db.session.commit()
        print(f'Admin with username {admin.username} added successfully.')
    else:
        print('Admin already exist.')

with app.app_context():
    db.create_all()
    insert_admin()