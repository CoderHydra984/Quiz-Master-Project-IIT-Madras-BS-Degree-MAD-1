
from flask import Flask, request,redirect,render_template,url_for,session
from flask import current_app as app
from application.models import *
from application.functions import *
import bcrypt
from functools import wraps
from datetime import datetime,timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func,desc



#################################################### Login Reqired Wrapper #################################################################
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
############################################################################################################################################


#################################################### Database consistency ##################################################################

# Below route is to update quiz_chapter and quiz_subject relationship tables based on quiz_question relationship table.
@app.route("/update_quiz_relations",methods=["GET"])
@admin_required
def update_quiz_relations():
    quizzes = db.session.query(Quiz).all()
    for quiz in quizzes:
        # quiz.chapters.clear()
        # db.session.commit()
        # quiz.subjects.clear()
        # db.session.commit()
        questions = quiz.questions
        for question in questions:
            chapter = question.chapter
            exists_chap = db.session.query(Quiz_Chapter).filter(
                (Quiz_Chapter.quiz_id==quiz.id) & (Quiz_Chapter.chapter_id==chapter.id)).first()
            if not(exists_chap):
                quiz.chapters.append(chapter)
            subject = chapter.subject
            exists_sub = db.session.query(Quiz_Subject).filter(
                (Quiz_Subject.quiz_id==quiz.id) & (Quiz_Subject.subject_id==subject.id)).first()
            if not(exists_sub):
                quiz.subjects.append(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))



###################################################### Login and Logouts ##################################################################
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for('login'))


@app.route("/redirecting_dashboard",methods=["GET"])
def home():

    if request.method == 'GET':
        if 'user_id' in session and 'first_name' in session:
            return redirect(url_for('user_dashboard',first_name = session['first_name']))
        if 'admin_id' in session and 'first_name' in session:
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Login required'
        


@app.route("/login", methods=["GET", "POST"])
def login():
    # IF it is a get request, response with login template.
    if request.method=='GET':
        wrong_pass = request.args.get('wrong_pass',False)
        user_not_exists = request.args.get('user_not_exists',False)
        unauthorized_access = request.args.get('unauthorized_access',False)
        uname_req = request.args.get('username_required',False)
        pass_req = request.args.get('password_required',False)
        return render_template("index.html",
                               wrong_pass=wrong_pass,
                               user_not_exists=user_not_exists,
                               unauthorized_access=unauthorized_access,
                               username_required=uname_req,
                               password_required = pass_req) 
    # Else check the input data and response respectivley.
    elif request.method=='POST':
        # Read and store form data.
        inp_username=request.form.get("username")
        if not(inp_username):
            return redirect(url_for('login',username_required=True))
        
        inp_pass=request.form.get("password")
        if not(inp_pass):
            return redirect(url_for('login',password_required=True))
        # Check if admin-login
        is_admin = request.form.get("admin-login")
        if is_admin:
            # Check if admin exists.
            admin = db.session.query(Admin).filter_by(username=inp_username).first()
            if admin:
                if check_user(admin,inp_pass):
                    session['admin_id'] = admin.id
                    session['first_name'] = admin.first_name
                    session['last_name'] = admin.last_name
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('login',wrong_pass=True))
            else:
                return redirect(url_for('login',unauthorized_access=True))
        # If not admin query for user
        else:
            # Query user in database.
            user=User.query.filter_by(username=inp_username).first()
            #Check user exists.
            if user:
                #checks if inp_passowrd is correct.
                if check_user(user,inp_pass):
                    # If correct, store user information in session and redirect to user dashboard.
                    session['user_id'] = user.id
                    session['username'] = inp_username
                    session['first_name'] = user.first_name
                    session['last_name'] = user.last_name
                    return redirect(url_for('user_dashboard',first_name=session['first_name']))
                else:
                    # Else give message wrong password.
                    return redirect(url_for('login',wrong_pass=True))
            # if user does not exist, give message user does not exist, register first.
            else:
                return redirect(url_for('login',user_not_exists=True))



@app.route("/logout",methods=["GET"])
def logout():
    if request.method == 'GET':
        # Clear user data from session.
        session.clear()
        # Redirect to login page.
        return redirect(url_for('login'))



@app.route("/register", methods=["GET", "POST"])
def register():
    # IF get request, response with register template.
    if request.method=='GET':
        user_exists = request.args.get('user_exists',False) 
        uname_req = request.args.get('username_required',False)
        pass_req = request.args.get('password_required',False)
        fname_req = request.args.get('first_name_required',False)
        return render_template("register.html",
                               username_required = uname_req,
                               password_required = pass_req,
                               first_name_required = fname_req,
                               user_exists=user_exists)
    # else post request, process the input(form) data and response respectively. 
    elif request.method=='POST':
        # Creating dict of form data to pass in create_user functions
        form_data = request.form.to_dict()

        # This function checks if user already exists or not, if yes returns False, else creates a new user and returns the new_user object.
        (new_user,uname_req,pass_req,fname_req) = create_user(form_data,False,False,False)
        if uname_req:
            return redirect(url_for('register',username_required=True))
        if pass_req:
            return redirect(url_for('register',password_required=True))
        if fname_req:
            return redirect(url_for('register',first_name_required=True))
        # If new_user is returned, store user information in session redirect to user_dashboard
        if new_user:
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['first_name'] = new_user.first_name
            session['last_name'] = new_user.last_name
            return redirect(url_for('user_dashboard',first_name=session['first_name']))
        # If user already exist, give message: User Already Exist.
        else:
            return redirect(url_for('register',user_exists=True))
###########################################################################################################################################


##################################################### User Read Controllers ###############################################################
@app.route("/user/<string:first_name>/quizzes",methods=["GET"])
@user_required
def user_dashboard(first_name):
    state = request.args.get('state', 'current')
    quiz_list = db.session.query(Quiz).all()
    user_id = session['user_id']
    if request.method == 'GET':
        user_dict = user_data(user_id)
        if state == 'current':
            quiz_dict_list = current_quiz(quiz_list)
            return render_template('usr_curr_quizzes.html',quiz_dict_list=quiz_dict_list,
                                   first_name=user_dict['first_name'],
                                   state=state)
        elif state == 'past':
            quiz_dict_list = past_quiz(quiz_list)
            return render_template('usr_past_quizzes.html',quiz_dict_list=quiz_dict_list,
                                   first_name=user_dict['first_name'],
                                   state=state)
        elif state == 'upcoming':
            quiz_dict_list = upcoming_quiz(quiz_list)
            return render_template('usr_upcoming_quizzes.html',quiz_dict_list=quiz_dict_list,
                                   first_name=user_dict['first_name'],
                                   state=state)
        else:
            quiz_dict_list = current_quiz(quiz_list)
            return render_template('usr_dashboard.html',quiz_dict_list=quiz_dict_list,
                                   first_name=user_dict['first_name'],
                                   state=state)
    

@app.route("/user/<string:first_name>/past_quizzes/<int:quiz_id>/questions",methods=["GET"])
def user_questions_in_past_quiz(first_name,quiz_id):
    if request.method == 'GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('usr_questions_in_past_quiz.html',quiz=quiz)

@app.route("/user/<string:first_name>/scores",methods=["GET"])
@user_required
def user_scores(first_name):
    user_id = session['user_id']
    if request.method == 'GET':
        user_dict = user_data(user_id)
        scores_list = get_scores(user_id)
        return render_template('usr_scores.html',scores_list=scores_list,first_name=user_dict['first_name'],user_id=user_id)

@app.route("/user/<string:first_name>/scores/<int:score_id>/answer_transcript",methods=["GET"])
def user_answer_transcript(first_name,score_id):
    score = db.session.query(Scores).filter_by(id=score_id).first()
    uats = db.session.query(User_Answer_Transcript).filter_by(score_id=score_id).all()
    quiz = db.session.query(Quiz).filter_by(id=score.quiz_id).first()
    user_answer_dict = {}
    user_answers = []
    for uat in uats:
        user_answers.append(uat.option_id)
        if uat.question_id in user_answer_dict.keys():
            user_answer_dict[uat.question_id] += [uat.option_id]
        else:
            user_answer_dict[uat.question_id] = [uat.option_id]
    
    correct_ans_dict = get_correct_ans_dict(quiz.questions)

    score_dict = {}
    for question_id, user_options in user_answer_dict.items():
        if question_id in correct_ans_dict:
            correct_options, (pos_marks, neg_marks) = correct_ans_dict[question_id]

            correct_set = set(correct_options)
            user_set = set(user_options)

            correct_attempts = user_set.intersection(correct_set)
            incorrect_attempts = user_set - correct_set
            if incorrect_attempts==set():
                score_dict[question_id] = len(correct_attempts) * (pos_marks/len(correct_set))
            else:
                score_dict[question_id] = neg_marks
    return render_template('usr_quiz_answer_transcript.html',quiz=quiz,
                           score_id=score_id,
                           score_dict=score_dict,
                           user_answers=user_answers)

@app.route("/user/<string:first_name>/quizzes/<int:quiz_id>/quiz-details",methods=["GET"])
def user_quiz_details(first_name,quiz_id):
    if request.method=='GET':
        state = request.args.get('state', 'current')    
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        quiz_dict = quiz_details(quiz)
        if state == 'current':
            return render_template('usr_quiz_view.html',quiz_dict=quiz_dict)
        elif state == 'past':
            return render_template('usr_past_quiz_view.html',quiz_dict=quiz_dict)
        elif state == 'upcoming':
            return render_template('usr_upcom_quiz_view.html',quiz_dict=quiz_dict)

@app.route("/user/<string:first_name>/summary",methods=["GET"])
def user_summary(first_name):
    if request.method == 'GET':
        user_id = session['user_id']
        scores = db.session.query(Scores).filter_by(user_id=user_id).all()
        labels = []
        data = []
        correct_ans_count = 0
        pc_ans_count = 0
        incorr_ans_count = 0
        ua_ans_count = 0
        for score in scores:
            quiz = db.session.query(Quiz).filter_by(id=score.quiz_id).first()
            total_marks = 0
            for question in quiz.questions:
                correct_option_ids = []
                user_selected_option_ids = []
                uats = db.session.query(User_Answer_Transcript).filter(User_Answer_Transcript.user_id==user_id,
                                                                    User_Answer_Transcript.question_id==question.id,
                                                                    User_Answer_Transcript.score_id==score.id,).all()
                for uat in uats:
                    user_selected_option_ids += [uat.option_id]
                for option in question.options:
                    if option.is_correct:
                        correct_option_ids.append(option.id)
                
                correct_set = set(correct_option_ids)
                user_set = set(user_selected_option_ids)

                incorrect_answers = user_set - correct_set

                if user_set == set():
                    ua_ans_count += 1
                elif incorrect_answers == set() and len(user_set) == len(correct_set):
                    correct_ans_count += 1
                elif incorrect_answers == set():
                    pc_ans_count += 1
                else:
                    incorr_ans_count += 1
                total_marks += question.marks
            labels.append(quiz.title)
            data.append(round((score.marks_obtained/total_marks)*100))
        cor_pc_incor_ua = [correct_ans_count,pc_ans_count,incorr_ans_count,ua_ans_count]
        return render_template('usr_summary.html',labels=labels,data=data,cor_pc_incor_ua=cor_pc_incor_ua)

@app.route("/user/<int:user_id>/<string:first_name>/quizzes/<int:quiz_id>/start",methods=["GET"])
def user_start_quiz(user_id,first_name,quiz_id):

    quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
    time_date = datetime.now()
    date_of_attempt = time_date.strftime("%Y-%m-%d")
    attempt_val = db.session.query(func.max(Scores.attempt_count)).filter_by(quiz_id=quiz_id, user_id=user_id).scalar() or 0
    attempt_count = attempt_val + 1
    started_time = datetime.now()
    time_duration = quiz.time_duration 

    # Convert "HH:MM:SS" string to timedelta
    hours, minutes, seconds = map(int, time_duration.split(":"))
    time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Calculate end_time if user closes the browser
    end_time = started_time + time_delta

    score = 0

    user_score = Scores(quiz_id=quiz_id,
                        user_id=user_id,
                        started_time=started_time,
                        end_time=end_time,
                        date_of_attempt=date_of_attempt,
                        marks_obtained=score,
                        attempt_count=attempt_count,
                        remarks=None)
    db.session.add(user_score)
    db.session.commit()
    return render_template('usr_quiz_start.html',quiz=quiz,score_id=user_score.id)
###########################################################################################################################################





########################################################## User Post Controllers ##########################################################
@app.route("/user/<string:first_name>/quizzes/<int:quiz_id>/submit",methods=["GET","POST"])
def user_submit_quiz(first_name, quiz_id):
    current_time = datetime.now()
    end_time = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
    quiz_questions = quiz.questions
    correct_ans_dict = get_correct_ans_dict(quiz_questions)
    user_id = int(request.form.get("user_id"))
    score_id = int(request.form.get("score_id"))
    answers = []
    user_ans_dict = {}
    count = 1
    while True:
        quest_id = request.form.get(f"{count}-question_statement")
        if not quest_id:
            break  # No more questions, exit loop
        quest_id = int(quest_id)
        for i in range(1, 5):
            option_id = request.form.get(f"{count}-option-{i}")
            if option_id:  # Only process checked options
                answers.append(User_Answer_Transcript(
                    user_id=user_id,
                    quiz_id=quiz_id,
                    question_id=int(quest_id),
                    option_id=int(option_id),
                    score_id = score_id
                ))
                if quest_id in user_ans_dict.keys():
                    user_ans_dict[quest_id] += [int(option_id)]
                else:
                    user_ans_dict[quest_id] = [int(option_id)]
        count += 1

    if answers:
        db.session.add_all(answers)
        db.session.commit()
    total_score = evaluate_marks(user_ans_dict,correct_ans_dict)
    score_data = db.session.query(Scores).filter_by(id=score_id).first()
    score_data.marks_obtained = total_score
    score_data.end_time = end_time
    db.session.commit()
    return redirect(url_for('user_scores', first_name=session['first_name']))



###########################################################################################################################################





###################################################### Admin Read Controllers #############################################################
@app.route("/quiz-master/admin-dashboard",methods=["GET"])
@admin_required
def admin_dashboard():
    if request.method == 'GET':
        today = str(datetime.today())[:10]
        subjects = db.session.query(Subject).limit(4).all()
        quiz_list = db.session.query(Quiz).filter(Quiz.is_published==1,Quiz.deadline>=today).limit(4).all()
        quiz_dict_list = current_quiz(quiz_list)
        users_lim = db.session.query(User).limit(4).all()

        quiz_count = db.session.query(Quiz).filter_by(is_published=True).count()
        users = db.session.query(User).limit(4).all()
        user_names = []
        quiz_attempt_counts = []
        for user in users:
            full_name = user.first_name + ' ' + user.last_name
            user_names.append(full_name)
            unique_quiz_attempts = (db.session.query(func.count(func.distinct(Scores.quiz_id))).filter(Scores.user_id == user.id).scalar())
            quiz_attempt_counts.append(unique_quiz_attempts)
        return render_template('adm_dashboard.html',subjects=subjects,
                               quiz_dict_list= quiz_dict_list,
                                users=users_lim,
                                user_names=user_names,
                                quiz_attempt_counts=quiz_attempt_counts,
                                quiz_count=quiz_count,
                                first_name=session['first_name'])

@app.route("/quiz-master/quizzes",methods=["GET"])
@admin_required
def admin_quizzes():
    state = request.args.get('state','current')
    if request.method == 'GET':
        quiz_list = db.session.query(Quiz).all()
        if state == 'current':
            quiz_dict_list = current_quiz(quiz_list)
            return render_template('adm_curr_quizzes.html',quiz_dict_list=quiz_dict_list,
                                    first_name=session['first_name'])
        elif state == 'upcoming':
            quiz_dict_list = upcoming_quiz(quiz_list)
            return render_template('adm_upcoming_quizzes.html',quiz_dict_list=quiz_dict_list,
                                first_name=session['first_name'],)
        elif state == 'past':
            quiz_dict_list = past_quiz(quiz_list)
            return render_template('adm_past_quizzes.html',quiz_dict_list=quiz_dict_list,
                                first_name=session['first_name'],)



@app.route("/quiz-master/subjects",methods=["GET"])
@admin_required
def admin_subjects():
    subjects = db.session.query(Subject).filter_by(is_deleted=False)
    subjects_list = [] #[(subjects,no. of chapters)]
    for subject in subjects:
        chap_count = db.session.query(Chapter).filter(Chapter.subject_id==subject.id,
                                                      Chapter.is_deleted==False).count()
        subjects_list += [(subject,chap_count)]
    return render_template('adm_all_subjects.html', subjects_list=subjects_list)


@app.route("/quiz-master/subject/<int:subj_id>/chapters",methods=["GET"])
@admin_required
def admin_chapters_of_subject(subj_id):
    if request.method == 'GET':
        subject = db.session.query(Subject).filter_by(id=subj_id).first()
        chapters = db.session.query(Chapter).filter(Chapter.subject_id==subj_id,
                                                         Chapter.is_deleted==False).all()
        chapters_list = [] # [(chapter,no. of questions)]
        for chapter in chapters:
            quest_count = db.session.query(Questions).filter(Questions.chapter_id==chapter.id,
                                                             Questions.is_deleted == False).count()
            chapters_list += [(chapter,quest_count)]
        return render_template('adm_chapters_of_subject.html',subject=subject,chapters_list=chapters_list)
    

@app.route("/quiz-master/subject/<int:subj_id>/chapter/<int:chap_id>/questions",methods=["GET"])
@admin_required
def admin_questions_of_chapter(subj_id,chap_id):
    if request.method=='GET':
        chapter= db.session.query(Chapter).filter_by(id=chap_id).first()
        questions_list = db.session.query(Questions).filter(Questions.chapter_id == chap_id,
                                                          Questions.is_deleted == False).all()
        return render_template('adm_questions_of_chapter.html', questions_list=questions_list,subj_id=subj_id,chapter=chapter)


@app.route("/quiz-master/subject/<int:subj_id>/chapter/<int:chap_id>/question/<int:quest_id>/quizzes",methods=["GET"])
def admin_quizzes_on_question(subj_id,chap_id,quest_id):
    if request.method == 'GET':    
        question = db.session.query(Questions).filter_by(id=quest_id).first()
        quiz_list = question.quizzes
        upcom_quiz_dict_list = upcoming_quiz(quiz_list)
        past_quiz_dict_list = past_quiz(quiz_list)
        curr_quiz_dict_list = current_quiz(quiz_list)
        return render_template('adm_quizzes_on_question.html',subj_id=subj_id,chap_id=chap_id,
                               upcom_quiz_dict_list=upcom_quiz_dict_list,
                               past_quiz_dict_list=past_quiz_dict_list,
                               curr_quiz_dict_list=curr_quiz_dict_list)
    
@app.route("/quiz-master/subject/<int:subj_id>/chapter/<int:chap_id>/quizzes",methods=["GET"])
def admin_quizzes_on_chapter(subj_id,chap_id):
    if request.method == 'GET':
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()
        quiz_list = chapter.quizzes
        upcom_quiz_dict_list = upcoming_quiz(quiz_list)
        past_quiz_dict_list = past_quiz(quiz_list)
        curr_quiz_dict_list = current_quiz(quiz_list)
        return render_template('adm_quizzes_on_chapter.html',subj_id=subj_id,chap_id=chap_id,
                               upcom_quiz_dict_list=upcom_quiz_dict_list,
                               past_quiz_dict_list=past_quiz_dict_list,
                               curr_quiz_dict_list=curr_quiz_dict_list,chapter=chapter)

    
@app.route("/quiz-master/subject/<int:subj_id>/quizzes",methods=["GET"])
def admin_quizzes_on_subject(subj_id):
    if request.method == 'GET':
        subject = db.session.query(Subject).filter_by(id=subj_id).first()
        quiz_list = subject.quizzes
        upcom_quiz_dict_list = upcoming_quiz(quiz_list)
        past_quiz_dict_list = past_quiz(quiz_list)
        curr_quiz_dict_list = current_quiz(quiz_list)
        return render_template('adm_quizzes_on_subject.html',subj_id=subj_id,
                               upcom_quiz_dict_list=upcom_quiz_dict_list,
                               past_quiz_dict_list=past_quiz_dict_list,
                               curr_quiz_dict_list=curr_quiz_dict_list,subject=subject)


@app.route("/quiz-master/quizzes/<int:quiz_id>/questions",methods=["GET"])
def admin_questions_in_quiz(quiz_id):
    if request.method == 'GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('adm_questions_in_quiz.html',quiz=quiz)


@app.route("/quiz-master/past-quizzes/<int:quiz_id>/questions",methods=["GET"])
def admin_questions_in_past_quiz(quiz_id):
    if request.method=='GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('adm_questions_in_past_quiz.html',quiz=quiz)

@app.route("/quiz-master/upcoming-quizzes/<int:quiz_id>/questions",methods=["GET"])
def admin_questions_in_upcoming_quiz(quiz_id):
    if request.method=='GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('adm_questions_in_upcoming_quiz.html',quiz=quiz)


@app.route("/quiz-master/quizzes/<int:quiz_id>/attempts",methods=["GET"])
def attempts(quiz_id):
    if request.method == 'GET':
        state = request.args.get('state','current')
        score_data_dict_list = get_attempts_scores(quiz_id)
        return render_template('adm_quiz_attempts.html',score_data_dict_list=score_data_dict_list,state=state)

@app.route("/quiz-master/users",methods=["GET"])
def admin_users_view():
    if request.method == 'GET':
        users = db.session.query(User).all()
        return render_template('adm_users.html',users=users)

@app.route("/quiz-master/users/<int:user_id>/summary",methods=["GET"])
def admin_user_summary(user_id):
    if request.method == 'GET':
        scores = db.session.query(Scores).filter_by(user_id=user_id).all()
        labels = []
        data = []
        correct_ans_count = 0
        pc_ans_count = 0
        incorr_ans_count = 0
        ua_ans_count = 0
        for score in scores:
            quiz = db.session.query(Quiz).filter_by(id=score.quiz_id).first()
            total_marks = 0
            for question in quiz.questions:
                correct_option_ids = []
                user_selected_option_ids = []
                uats = db.session.query(User_Answer_Transcript).filter(User_Answer_Transcript.user_id==user_id,
                                                                    User_Answer_Transcript.question_id==question.id,
                                                                    User_Answer_Transcript.score_id==score.id,).all()
                for uat in uats:
                    user_selected_option_ids += [uat.option_id]
                for option in question.options:
                    if option.is_correct:
                        correct_option_ids.append(option.id)
                
                correct_set = set(correct_option_ids)
                user_set = set(user_selected_option_ids)

                incorrect_answers = user_set - correct_set

                if user_set == set():
                    ua_ans_count += 1
                elif incorrect_answers == set() and len(user_set) == len(correct_set):
                    correct_ans_count += 1
                elif incorrect_answers == set():
                    pc_ans_count += 1
                else:
                    incorr_ans_count += 1
                

                total_marks += question.marks
            labels.append(quiz.title)
            data.append(round((score.marks_obtained/total_marks)*100))
        cor_pc_incor_ua = [correct_ans_count,pc_ans_count,incorr_ans_count,ua_ans_count]
        return render_template('adm_user_summary.html',labels=labels,data=data,cor_pc_incor_ua=cor_pc_incor_ua)

@app.route("/quiz-master/summary",methods=["GET","POST"])
def admin_full_summary():
    if request.method == 'GET':
        quiz = db.session.query(Quiz).first()
        if not(quiz):
             return "Create Quiz First to see user attempts", 404
    elif request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        if not(quiz):
            return "Quiz not found, Enter Correct Quiz ID", 404
    quiz_count = db.session.query(Quiz).filter_by(is_published=True).count()
    users = db.session.query(User).all()
    user_names = []
    quiz_attempt_counts = []
    for user in users:
        full_name = user.first_name + ' ' + user.last_name
        user_names.append(full_name)
        unique_quiz_attempts = (db.session.query(func.count(func.distinct(Scores.quiz_id))).filter(Scores.user_id == user.id).scalar())
        quiz_attempt_counts.append(unique_quiz_attempts)

    # For Graph 2
    # Since above graph 1 already had below line, so i commented this.
    # users = db.session.query(User).all()
    user_names_quiz = []
    highest_scores = []
    total_marks = 0
    for question in quiz.questions:
        total_marks += question.marks
    for user in users:
        full_name = user.first_name + ' ' + user.last_name
        user_names_quiz.append(full_name)
        
        user_scores = db.session.query(Scores).filter(Scores.quiz_id==quiz.id,
                                                        Scores.user_id==user.id).all()
        high_score = 0
        for score in user_scores:
            if score.marks_obtained > high_score:
                high_score = score.marks_obtained
        percent = (high_score*100)/(total_marks)
        highest_scores.append(percent)
    return render_template('adm_full_summary.html',user_names=user_names,
                        quiz_attempt_counts=quiz_attempt_counts,quiz_count=quiz_count,
                        quiz=quiz,
                        user_names_quiz=user_names_quiz,
                        highest_scores=highest_scores)

###########################################################################################################################################



##################################################### Admin Create Controllers ############################################################

@app.route("/quiz-master/quizzes/create_quiz",methods=["GET","POST"])
def admin_create_quiz():
    if request.method == 'GET':
        qtitle_req = request.args.get('qtitle_required',False)
        chapter_id_req = request.args.get('chapter_id_required',False)
        dur_req = request.args.get('duration_required',False)
        deadline_req = request.args.get('deadline_required',False)
        return render_template('adm_create_quiz.html',
                               qtitle_required=qtitle_req,
                               chapter_id_required=chapter_id_req,
                               duration_required=dur_req,
                               deadline_required=deadline_req)
    elif request.method == 'POST':
        quiz_title = request.form.get('quiz_title')
        if not(quiz_title):
            return redirect(url_for('admin_create_quiz',qtitle_required=True))
        chapter_id_list = request.form.get('chapter_id').split(',')
        if (chapter_id_list == [""]):
            return redirect(url_for('admin_create_quiz',chapter_id_required=True))
        duration = request.form.get('duration')
        if not(duration):
            return redirect(url_for('admin_create_quiz',duration_required=True))
        deadline = request.form.get('deadline')
        if not(deadline):
            return redirect(url_for('admin_create_quiz',deadline_required=True))
        remarks = request.form.get('remarks','None')
        date_created = str(datetime.today())[:10]
        is_published = False
        new_quiz = Quiz(title=quiz_title,date_created=date_created,time_duration=duration,deadline=deadline,remarks=remarks,is_published=is_published)
        db.session.add(new_quiz)

        for id in chapter_id_list:
            chapter = db.session.query(Chapter).filter_by(id=int(id)).first()
            new_quiz.chapters.append(chapter)
            if chapter.subject not in new_quiz.subjects:
                new_quiz.subjects.append(chapter.subject)
        db.session.commit()
        return redirect(url_for('admin_quizzes',state='upcoming'))
    
@app.route("/quiz-master/subjects/create_subject",methods=["GET","POST"])
def admin_create_subject():
    if request.method == 'GET':
        return render_template('adm_create_subject.html')
    elif request.method == 'POST':
        subj_name = request.form.get('subject_name')
        subj_desc = request.form.get('description')
        new_subject = Subject(name=subj_name,description=subj_desc)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_subjects'))
    
@app.route("/quiz-master/subject/<string:subj_id>/create-chapter/",methods=["GET","POST"])
def admin_create_chapter(subj_id):
    subject = db.session.query(Subject).filter_by(id=subj_id).first()
    if request.method == 'GET':
        return render_template('adm_create_chapter.html',subject=subject)
    elif request.method == 'POST':
        subject_id = subj_id
        chapter_name = request.form.get('chapter_name')
        chapter_desc = request.form.get('description')
        new_chapter = Chapter(name=chapter_name,description=chapter_desc,subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin_chapters_of_subject', subj_id=subject_id))
    
@app.route("/quiz-master/subject/<string:subj_id>/chapter/<string:chap_id>/create-question",methods=["GET","POST"])
def admin_create_question(subj_id,chap_id):
    if request.method == 'GET':
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()
        return render_template('adm_create_question.html',subj_id=subj_id,chapter=chapter)
    elif request.method == 'POST':
        quest_statement = request.form.get('question_statement')
        marks = request.form.get('marks')
        negative_marks = request.form.get('negative_marks')
        new_question = Questions(question_statement=quest_statement,chapter_id=chap_id,marks=marks,negative_marks=negative_marks)
        db.session.add(new_question)
        db.session.commit()
        for i in range(1,5):
            option = request.form.get(f'option-{i}')
            is_correct = bool(request.form.get(f'is_correct_option{i}'))
            new_option = Options(question_id=new_question.id,option=option,is_correct=is_correct)
            db.session.add(new_option)
        db.session.commit()
        return redirect(url_for('admin_questions_of_chapter', subj_id=subj_id,chap_id=chap_id))

@app.route("/to-be-updated-later/<int:quiz_id>",methods=["GET","POST"])
def admin_create_question_from_quiz(quiz_id):
    if request.method == 'GET':
        return render_template('adm_create_question_from_quiz.html',quiz_id=quiz_id)
    elif request.method == 'POST':
        chap_id = request.form.get('chapter_id')
        quest_statement = request.form.get('question_statement')
        marks = request.form.get('marks')
        negative_marks = request.form.get('negative_marks')
        new_question = Questions(question_statement=quest_statement,marks=marks,negative_marks=negative_marks,chapter_id=chap_id)
        db.session.add(new_question)
        db.session.commit()
        for i in range(1,5):
            option = request.form.get(f'option-{i}')
            is_correct = bool(request.form.get(f'is_correct_option{i}'))
            new_option = Options(question_id=new_question.id,option=option,is_correct=is_correct)
            db.session.add(new_option)
        db.session.commit()
        return redirect(url_for('admin_add_question_in_quiz',quiz_id=quiz_id))
###########################################################################################################################################




##################################################### Admin Update Controllers ############################################################
@app.route("/quiz-master/subject/<string:subj_id>/chapter/<string:chap_id>/questions/<string:quest_id>/update-question",
           methods=["GET","POST"])
def admin_update_question(subj_id,chap_id,quest_id):
    if request.method == 'GET':
        question = db.session.query(Questions).filter_by(id=quest_id).first()

        return render_template('adm_update_question.html',question=question,subj_id=subj_id,chap_id=chap_id,quest_id=quest_id)
    elif request.method == 'POST':
        question = db.session.query(Questions).filter_by(id=quest_id).first()
        quest_statement = request.form.get('question_statement')
        p_marks = request.form.get('marks')
        negative_marks = request.form.get('negative_marks')
        question.question_statement = quest_statement
        question.marks =p_marks
        question.negative_marks = negative_marks
        for i in range(1,5):
            option_i = request.form.get(f'option-{i}')
            is_correct_i = request.form.get(f'is_correct_option{i}')
            question.options[i-1].option = option_i
            question.options[i-1].is_correct = bool(is_correct_i)
        db.session.commit()
        return redirect(url_for('admin_questions_of_chapter',subj_id=subj_id,chap_id=chap_id,quest_id=quest_id))

@app.route("/quiz-master/subject/<string:subj_id>/chapter/<string:chap_id>/update-chapter",methods=["GET","POST"])
def admin_update_chapter(subj_id,chap_id):
    if request.method == 'GET':
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()

        return render_template('adm_update_chapter.html',subj_id=subj_id,chapter=chapter)
    elif request.method == 'POST':
        chap_name = request.form.get('chapter_name')
        chap_desc = request.form.get('description')
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()
        chapter.name = chap_name
        chapter.description = chap_desc
        db.session.commit()
        return redirect(url_for('admin_chapters_of_subject',subj_id=subj_id))

@app.route("/quiz-master/subject/<string:subj_id>/update-subject",methods=["GET","POST"])
def admin_update_subject(subj_id):
    if request.method == 'GET':
        subject = db.session.query(Subject).filter_by(id=subj_id).first()
        return render_template('adm_update_subject.html',subject=subject,subj_id=subj_id)
    elif request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_desc = request.form.get('description')
        subject = db.session.query(Subject).filter_by(id=subj_id).first()
        subject.name = subject_name
        subject.description = subject_desc
        db.session.commit()
        return redirect(url_for('admin_subjects'))

@app.route("/quiz-master/quizzes/<int:quiz_id>/update_quiz",methods=["GET","POST"])
def admin_update_quiz(quiz_id):
    if request.method == 'GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('adm_update_quiz.html',quiz=quiz)
    elif request.method == 'POST':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        title = request.form.get('quiz_title')
        dur = request.form.get('duration')
        deadline = request.form.get('deadline')
        remarks = request.form.get('remarks')
        quiz.title = title
        quiz.time_duration = dur
        quiz.deadline = deadline
        quiz.remarks = remarks
        db.session.commit()
        return redirect(url_for('admin_quizzes',state='upcoming')) 

@app.route("/quiz-master/quizzes/<int:quiz_id>/publish_quiz",methods=["GET"])
def admin_publish_quiz(quiz_id):
    if request.method == 'GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        questions = quiz.questions
        chapters_of_question = []
        subjects_of_question = []
        for question in questions:
            if question.chapter not in chapters_of_question:
                chapters_of_question.append(question.chapter)
            if question.chapter.subject not in subjects_of_question:
                subjects_of_question.append(question.chapter.subject)
        for chapter in quiz.chapters:
            if chapter not in chapters_of_question:
                quiz.chapters.remove(chapter)
                # print(f'removed chapter {chapter}')
        for subject in quiz.subjects:
            if subject not in subjects_of_question:
                quiz.subjects.remove(subject)
                # print(f'removed subject {subject}')
        quiz.is_published = True
        db.session.commit()
        return redirect(url_for('admin_quizzes'))


@app.route("//quiz-master/upcoming-quizzes/<int:quiz_id>/add-questions",methods=["GET","POST"])
def admin_add_question_in_quiz(quiz_id):
    if request.method == 'GET':
        subjects = db.session.query(Subject).all()
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        return render_template('adm_add_question_in_quiz.html',subjects=subjects,quiz=quiz)
    elif request.method == 'POST':
        quest_id = request.form.get('question_id')
        question = db.session.query(Questions).filter_by(id=quest_id).first()
        quiz_id = request.form.get('quiz_id') 
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        quiz.questions.append(question)
        if question.chapter not in quiz.chapters:
            quiz.chapters.append(question.chapter)
            db.session.flush()
        if question.chapter.subject not in quiz.subjects:
            quiz.subjects.append(question.chapter.subject)
            db.session.flush()
        db.session.commit()
        return redirect(url_for('admin_add_question_in_quiz',quiz_id=quiz_id))
###########################################################################################################################################



##################################################### Admin Delete Controllers ############################################################
@app.route("/quiz-master/subject/<string:subj_id>/chapter/<string:chap_id>/questions/<string:quest_id>/delete-question",methods=["GET"])
def admin_delete_question(subj_id,chap_id,quest_id):
    if request.method == 'GET':
        question = db.session.query(Questions).filter_by(id=quest_id).first()
        options = db.session.query(Options).filter_by(question_id=quest_id).all()
        question.is_deleted = True
        for option in options:
            option.is_deleted = True
        db.session.commit()
        return redirect(url_for('admin_questions_of_chapter', subj_id=subj_id,chap_id=chap_id))


@app.route("/quiz-master/subject/<string:subj_id>/chapters/<string:chap_id>/delete-chapter",methods=["GET"])
def admin_delete_chapter(subj_id,chap_id):
    if request.method == 'GET':
        chapter = db.session.query(Chapter).filter_by(id=chap_id).first()
        questions = chapter.questions
        chapter.is_deleted = True
        for question in questions:
            question.is_deleted = True
            options = question.options
            for option in options:
                option.is_deleted = True
        db.session.commit()
        return redirect(url_for('admin_chapters_of_subject', subj_id=subj_id))

@app.route("/quiz-master/subject/<string:subj_id>/delete-subject",methods=["GET"])
def admin_delete_subject(subj_id):
    if request.method == 'GET':
        subject = db.session.query(Subject).filter_by(id=subj_id).first()
        subject.is_deleted = True
        for chapter in subject.chapters:
            chapter.is_deleted = True
            for question in chapter.questions:
                question.is_deleted = True
                options = question.options
                for option in options:
                    option.is_deleted = True
        db.session.commit()
    return redirect(url_for('admin_subjects'))

@app.route("/quiz-master/upcoming-quizzes/<int:quiz_id>/questions/delete-question/<int:quest_id>",methods=["GET"])
def admin_delete_question_in_quiz(quiz_id,quest_id):
    if request.method == 'GET':
        question = db.session.query(Questions).filter_by(id=quest_id).first()
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        flag_chap = False
        flag_sub = False
        quiz.questions.remove(question)

        for quest in quiz.questions:
            if quest.chapter == question.chapter:
                flag_chap=True
                break
        for quest in quiz.questions:
            if quest.chapter.subject == question.chapter.subject:
                flag_sub = True
        if flag_chap:
            pass
        else:
            quiz.chapters.remove(question.chapter)

        if flag_sub:
            pass
        else:
            quiz.subjects.remove(question.chapter.subject)
        db.session.commit()
        return redirect(url_for('admin_questions_in_upcoming_quiz',quiz_id=quiz_id))
    

@app.route("/quiz-master/quizzes/<int:quiz_id>/delete-quiz",methods=["GET"])
def admin_delete_quiz(quiz_id):
    if request.method == 'GET':
        quiz = db.session.query(Quiz).filter_by(id=quiz_id).first()
        quiz.questions.clear()
        quiz.chapters.clear()
        quiz.subjects.clear()
        db.session.commit()
        db.session.delete(quiz)
        db.session.commit()
        return redirect(url_for('admin_quizzes',state='upcoming'))