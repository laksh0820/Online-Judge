from flask import render_template,redirect,request,flash,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,current_user,logout_user
from Project import app,db
from Project.forms import SignInForm,SignUpForm,ProblemForm
from Project.models import Problem,User

@app.route('/')
def home(): 
    return render_template('home.html')

def judge_required(inner_func):
    def wrapped_function_judge(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Judge'):
            flash("Please log in as Judge to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    return wrapped_function_judge

def contestant_required(inner_func):
    def wrapped_function_contestant(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Contestant'):
            flash("Please log in as Contestant to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    return wrapped_function_contestant


# Sign in to an existing user
@app.route('/signin',methods=['GET','POST'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,str(form.password.data)):
                login_user(user)
                flash("Logged in Successfully")
                return render_template('home.html')
            else:
                flash("Wrong Password!! Try Again",'error')
        else:
            flash("User not Found!! Try Again",'error')
    return render_template('signin.html',form=form)
    
# Create a new User
@app.route('/signup',methods=['GET','POST'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data).first()
        user_name = User.query.filter_by(name=form.name.data).first()

        if (user_email is None) and (user_name is None):
            newUser = User()
            newUser.name = form.name.data
            newUser.email = form.email.data
            newUser.password = generate_password_hash(str(form.password.data))
            newUser.type = form.type.data
            try:
                db.session.add(newUser)
                db.session.commit()
                flash("User Added Successfully!!")
            except:
                return "Unable to enter User to the Database"
            form.name.data = ''
            form.email.data = ''
            form.password.data = ''
            form.confirm_password.data = ''
            form.type.data = ''
        elif user_name is None:
            flash('This email already exits. Please sign in','error')
        else:
            flash('This name already exits. Please enter a different name','error')

        return redirect(url_for('signup'))
    return render_template('signup.html',form = form)

# Logout of a user account
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out Successfully")
    return redirect(url_for('signin'))

# Post a new Problem
@app.route('/judge',methods = ['GET','POST'])
@login_required
@judge_required
def post_problems():
    form = ProblemForm()
    if form.validate_on_submit():
        newProblem = Problem()
        newProblem.title = form.title.data
        newProblem.description = form.description.data
        newProblem.sample_input = form.sample_input.data
        newProblem.sample_output = form.sample_output.data
        newProblem.exe_time = form.exe_time.data
        newProblem.exe_space = form.exe_space.data

        try:
            db.session.add(newProblem)
            db.session.commit()
            flash("Problem added Successfully!!")
        except:
            flash("There is some problem in adding the problem",'error')
        
        form.title.data = ''
        form.description.data = ''
        form.sample_input.data = ''
        form.sample_output.data = ''
        form.exe_time.data = 0
        form.exe_space.data = 0

    return render_template('judge.html',form=form)

@app.route('/contestant', methods= ['GET' , 'POST'])   
@login_required
@contestant_required
def solve_problems():
    if request.method == 'GET':
        problem_ids = Problem.query.with_entities(Problem.id).all()
        pblm_id_list = [x[0] for x in problem_ids]
        problem_titles = Problem.query.with_entities(Problem.title).all()
        pblm_title_list = [x[0] for x in problem_titles]
        return render_template('contestant.html' , ProblemIDs = pblm_id_list , ProblemTitles = pblm_title_list)
    else:
        return render_template('contestant.html')
    
@app.route('/problem/<int:problem_id>', methods= ['GET' , 'POST'])
def display_problem(problem_id):
    if request.method == 'GET':
        problem = Problem.query.filter(Problem.id == problem_id).all()
        pblm_parameters_list = [problem[0].id , problem[0].title , problem[0].description , problem[0].sample_input , problem[0].sample_output , problem[0].exe_time , problem[0].exe_space]
        return render_template('problem.html' , Problem_Parameters = pblm_parameters_list)
    else :
        return render_template('problem.html')

# @app.route('/onlineIDE')
# def online_coding():
#     pass