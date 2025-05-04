import bcrypt
from datetime import datetime
from application.models import *
import os

def user_data(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    user_dict = {'user_id':user.id,
                 'first_name':user.first_name,}
    return user_dict



# login controller Functions.
def check_user(user,inp_pass) -> bool:
    '''Takes user object and input_password -> returns:
    1. True if user exists and input_password is correct.
    2. False if user exists and input_password is wrong'''

    if bcrypt.checkpw(inp_pass.encode('utf-8'), user.password):
        return True
    else:
        return False
    


# register controller Functions.
def create_user(form_data,uname_req,pass_req,fname_req):
    '''Takes data of form and returns
    1. new_user if user does not already exist.
    2. False if user already exists.'''

    username = form_data['username']
    if not(username):
        return (False,True,False,False)
    password = form_data['password']
    if not(password):
        return (False,False,True,False)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    first_name = form_data['first_name']
    if not(first_name):
        return(False,False,False,True)
    last_name = form_data['last_name']
    qualification = form_data['qualification']
    dob = form_data['dob']
    if User.query.filter_by(username=username).first():
        return (False,False,False,False)
    else:
        new_user = User(username=username,password=hashed_pw,first_name=first_name,last_name=last_name,qualification=qualification,dob=dob)

        db.session.add(new_user)
        db.session.commit()
        return (new_user,False,False,False)



# user_dashboard controller functions
def subj_chap(quiz):
    # This function will add only those chapter from which atleast one question has been asked.
    # If admin has added a chapter but forget to add any question from that chapter, then this chapter will not be sent to webpage.
    subject_chapters= {}
    for question in quiz.questions:
        chapter = db.session.query(Chapter).filter_by(id=question.chapter.id).first()
        subject = db.session.query(Subject).filter_by(id=chapter.subject_id).first()
        if subject.name in subject_chapters.keys():
            if chapter.name not in subject_chapters[subject.name]:
                subject_chapters[subject.name] += [chapter.name]
        else:
            subject_chapters[subject.name] = [chapter.name]
    return subject_chapters

def subj_chap_upcoming(quiz):
    subject_chapters= {}
    # add all chapter from questions
    for question in quiz.questions:
        chapter = db.session.query(Chapter).filter_by(id=question.chapter.id).first()
        subject = db.session.query(Subject).filter_by(id=chapter.subject_id).first()
        if subject.name in subject_chapters.keys():
            if chapter not in subject_chapters[subject.name]:
                subject_chapters[subject.name] += [chapter] #Sending chapter object (but in subj_chap chapter.name is sent)
        else:
            subject_chapters[subject.name] = [chapter] #Sending chapter object (but in subj_chap chapter.name is sent)
    
    # add those chapters whose questions has not been added yet
    for chapter in quiz.chapters:
        subject = db.session.query(Subject).filter_by(id=chapter.subject_id).first()
        if subject.name in subject_chapters.keys():
            if chapter not in subject_chapters[subject.name]:
                subject_chapters[subject.name] += [chapter] #Sending chapter object (but in subj_chap chapter.name is sent)
        else:
            subject_chapters[subject.name] = [chapter] #Sending chapter object (but in subj_chap chapter.name is sent)
    return subject_chapters



def current_quiz(quiz_list,limit=None):    
    # Fetch and store Quiz data
    today = str(datetime.today())[:10]
    quiz_dict_list = []
    for quiz in quiz_list:
        if quiz.is_published and quiz.deadline >= today:
            quiz_dict = {'quiz_id':quiz.id,
                        'date_created':quiz.date_created,
                        'deadline':quiz.deadline,
                        'dur':quiz.time_duration,
                        'questions':quiz.questions,
                        'remarks':quiz.remarks,
                        'quiz_title':quiz.title,
                        'subj_chap_dict':subj_chap(quiz)}
            quiz_dict_list.append(quiz_dict)
    return (quiz_dict_list)

def quiz_details(quiz):
    full_marks=0
    for question in quiz.questions:
        full_marks += question.marks
    quiz_dict = {'quiz_id':quiz.id,
                'date_created':quiz.date_created,
                'deadline':quiz.deadline,
                'dur':quiz.time_duration,
                'questions':quiz.questions,
                'remarks':quiz.remarks,
                'quiz_title':quiz.title,
                'full_marks':full_marks,
                'subj_chap_dict':subj_chap(quiz)}
    return quiz_dict

def upcoming_quiz(quiz_list):    
    # Fetch and store Quiz data
    if quiz_list == None:
        quiz_list = db.session.query(Quiz).all()
    quiz_dict_list = []
    for quiz in quiz_list:
        if not (quiz.is_published):
            quiz_dict = {'quiz_id':quiz.id,
                        'date_created':quiz.date_created,
                        'deadline':quiz.deadline,
                        'dur':quiz.time_duration,
                        'questions':quiz.questions,
                        'remarks':quiz.remarks,
                        'quiz_title':quiz.title,
                        'subj_chap_dict':subj_chap_upcoming(quiz)}
            quiz_dict_list.append(quiz_dict)
    return (quiz_dict_list)

def past_quiz(quiz_list):    
    # Fetch and store Quiz data
    if quiz_list == None:
        quiz_list = db.session.query(Quiz).all()
    quiz_dict_list = []
    for quiz in quiz_list:
        today = str(datetime.today())[:10]
        if quiz.is_published and quiz.deadline < today :
            quiz_dict = {'quiz_id':quiz.id,
                        'date_created':quiz.date_created,
                        'deadline':quiz.deadline,
                        'dur':quiz.time_duration,
                        'questions':quiz.questions,
                        'remarks':quiz.remarks,
                        'quiz_title':quiz.title,
                        'subj_chap_dict':subj_chap(quiz)}
            quiz_dict_list.append(quiz_dict)
    return (quiz_dict_list)

def all_quiz():    
    # Fetch and store Quiz data
    quiz_list = db.session.query(Quiz).all()
    quiz_dict_list = []
    for quiz in quiz_list:
        quiz_dict = {'quiz_id':quiz.id,
                    'date_created':quiz.date_created,
                    'deadline':quiz.deadline,
                    'dur':quiz.time_duration,
                    'questions':quiz.questions,
                    'remarks':quiz.remarks,
                    'quiz_title':quiz.title,
                    'subj_chap_dict':subj_chap(quiz)}
        quiz_dict_list.append(quiz_dict)
    return (quiz_dict_list)

# scores controller functions.
def remarks(score,total_marks):
    if score/total_marks >= 0.90:
        return 'S'
    elif score/total_marks >= 0.80:
        return 'A'
    elif score/total_marks >= 0.70:
        return 'B'
    elif score/total_marks >= 0.60:
        return 'C'
    elif score/total_marks >= 0.50:
        return 'D'
    elif score/total_marks >= 0.40:
        return 'E'
    else:
        return 'Fail'

def get_scores(user_id):
    scores= db.session.query(Scores).filter_by(user_id=user_id).all()
    scores_list = []
    for score in scores:
        marks_obtained = round(float(score.marks_obtained),2)

        start_time_str = score.started_time
        end_time_str = score.end_time

        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f")
 
        time_taken = str(end_time - start_time).split('.')[0]

        quiz = db.session.query(Quiz).filter_by(id=score.quiz_id).first()
        questions = quiz.questions
        total_marks=0
        for question in questions:
            total_marks += question.marks

        remark = remarks(marks_obtained,total_marks)
        subj_chap_dict = subj_chap(quiz)
        subjects_list = [chapter.name for chapter in quiz.chapters]
        subjects_stri = '; '.join(subjects_list)
        score_data_dict = {'score_id':score.id,
                           'quiz_id':score.quiz_id,
                           'attempted_date':score.date_of_attempt,
                           'quiz_title':quiz.title,
                           'time_taken':time_taken,
                           'marks_obtained':marks_obtained,
                           'total_marks':total_marks,
                           'subj_str':subjects_stri,
                           'subj_chap_dict':subj_chap_dict,
                           'questions':quiz.questions,
                           'remarks':remark,
                           'attempt_count':score.attempt_count}
        scores_list.append(score_data_dict)
    return scores_list
        

def get_correct_ans_dict(quiz_questions):
    correct_ans = {}
    correct_ans_dict = {}

    for question in quiz_questions:
        for option in question.options:
            if option.is_correct:
                if question.id in correct_ans:
                    correct_ans[question.id].append(option.id)
                else:
                    correct_ans[question.id] = [option.id]

        correct_ans_dict[question.id] = [correct_ans.get(question.id, []),(question.marks, question.negative_marks)]
    return correct_ans_dict



def evaluate_marks(user_ans_dict, correct_ans_dict):
    total_score = 0

    for question_id, user_options in user_ans_dict.items():
        if question_id in correct_ans_dict:
            correct_options, (pos_marks, neg_marks) = correct_ans_dict[question_id]

            correct_set = set(correct_options)
            user_set = set(user_options)

            if not correct_set:  # Edge case: No correct answers exist
                continue

            correct_attempts = user_set.intersection(correct_set)
            incorrect_attempts = user_set - correct_set

            if incorrect_attempts:  
                # Deduct only proportionally to incorrect attempts
                total_score += neg_marks * len(incorrect_attempts) / len(user_set)
            else:
                # All correct: Award proportional marks
                total_score += len(correct_attempts) * (pos_marks / len(correct_set))

    return total_score



def get_attempts_scores(quiz_id):
    '''
    score_data_dict = {score.user_id,
                        user_name,
                        score.date_of_attempt,
                        Time_taken,
                        score.marks_obtained,
                        score.remarks
    }'''
    scores = db.session.query(Scores).filter_by(quiz_id=quiz_id).all()
    score_data_dict_list = []
    for score in scores:
        score_data_dict =  {}
        user = db.session.query(User).filter_by(id=score.user_id).first()
        
        start_time_str = score.started_time
        end_time_str = score.end_time

        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f")
 
        time_taken = str(end_time - start_time).split('.')[0]

        score_data_dict['user_id'] = score.user_id
        score_data_dict['date_of_attempt'] = score.date_of_attempt
        score_data_dict['marks_obtained'] = round(score.marks_obtained, 1)
        score_data_dict['remarks'] = score.remarks
        score_data_dict['time_taken'] = time_taken


        score_data_dict['name'] = user.first_name + ' ' + user.last_name
        score_data_dict_list.append(score_data_dict)
    return score_data_dict_list