from flask import render_template,redirect,request,flash,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,current_user,logout_user
from Project import app,db
from Project.forms import SignInForm,SignUpForm,ProblemForm
from Project.models import Problem,User,Submissions
import requests
import base64

# Home Page
@app.route('/')
def home(): 
    return render_template('home.html')

def judge_required(inner_func):
    def wrapped_function_judge(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Judge'):
            flash("Please log in as Judge to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapped_function_judge.__name__ = inner_func.__name__
    return wrapped_function_judge

def contestant_required(inner_func):
    def wrapped_function_contestant(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Contestant'):
            flash("Please log in as Contestant to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapped_function_contestant.__name__ = inner_func.__name__
    return wrapped_function_contestant


# Sign in to an existing user
@app.route('/signin',methods=['GET','POST'])
def signin():
    form = SignInForm()
         
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,str(form.password.data)):
                login_user(user,remember=form.remember_me.data)
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

# Display the Online editor
@app.route('/onlineIDE',methods=['GET'])
def online_coding():
    return render_template('onlineIDE.html')

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
        newProblem.judging_testcases = form.judging_testcases.data
        newProblem.exp_testcases_output = form.exp_testcases_output.data
        newProblem.user_id = current_user.id

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
        form.judging_testcases.data = ''
        form.exp_testcases_output.data = ''

    return render_template('judge.html',form=form)

# To show the problems created by the current user(Judge)
@app.route('/show_judge_problems/<int:id>',methods=['GET','POST'])
@login_required
@judge_required
def show_judge_problems(id):
    judge = User.query.get_or_404(id)
    return render_template('show_judge_problems.html',problems=judge.problems)

# To modify the problems created by the current user(Judge)
@app.route('/modify_problem/<int:id>',methods=['GET','POST'])
@login_required
@judge_required
def modify_problem(id):
    problem = Problem.query.get_or_404(id)
    form = ProblemForm()

    if form.validate_on_submit():
        problem.title = form.title.data
        problem.description = form.description.data
        problem.sample_input = form.sample_input.data
        problem.sample_output = form.sample_output.data
        problem.exe_time = form.exe_time.data
        problem.exe_space = form.exe_space.data
        problem.judging_testcases = form.judging_testcases.data
        problem.exp_testcases_output = form.exp_testcases_output.data
        problem.user_id = current_user.id

        try:
            db.session.commit()
            flash("Problem updated successfully")
        except:
            flash("Unable to update the Problem",'error')
        
        return render_template('show_judge_problems.html',problems=current_user.problems)
    
    form.title.data=problem.title
    form.description.data=problem.description
    form.sample_input.data=problem.sample_input
    form.sample_output.data=problem.sample_output
    form.exe_time.data=problem.exe_time
    form.exe_space.data=problem.exe_space  
    form.judging_testcases.data=problem.judging_testcases
    form.exp_testcases_output.data=problem.exp_testcases_output
    return render_template('modify_problem.html',form=form,current_problem=problem)

# To delete the problems created by the current user(Judge)
@app.route('/delete_problem/<int:id>',methods=['GET','POST'])
@login_required
@judge_required
def delete_problem(id):
    problem = Problem.query.get_or_404(id)

    try:
        db.session.delete(problem)
        db.session.commit()

        flash("Successfully deleted")

        return render_template('show_judge_problems.html',problems=current_user.problems)
    except:
        flash("Oops! There is a problem in deleting this problem. Try Again")
        return render_template('show_judge_problems.html',problems=current_user.problems)


# Show problems to the contestant
@app.route('/contestant', methods= ['GET'])   
@login_required
@contestant_required
def show_problems():
    problem_ids = Problem.query.with_entities(Problem.id).all()
    pblm_id_list = [x[0] for x in problem_ids]
    problem_titles = Problem.query.with_entities(Problem.title).all()
    pblm_title_list = [x[0] for x in problem_titles]
    return render_template('contestant.html' , ProblemIDs = pblm_id_list , ProblemTitles = pblm_title_list)

# To show the problems submitted by the current user(Contestant)
@app.route('/get_submissions/<int:id>',methods=['GET','POST'])
@login_required
@contestant_required
def get_submissions(id):
    contestant = User.query.get_or_404(id)
    problems = Problem.query.all()
    return render_template('submissions.html',submissions=contestant.submissions,problems=problems)

# To delete the submissions posted by the current user(Contestant)
@app.route('/delete_submission/<int:id>',methods=['GET','POST'])
@login_required
@contestant_required
def delete_submission(id):
    problems = Problem.query.all()
    submission = Submissions.query.get_or_404(id)

    try:
        db.session.delete(submission)
        db.session.commit()

        flash("Successfully deleted")

        return render_template('submissions.html',submissions=current_user.submissions,problems=problems)
    except:
        flash("Oops! There is a problem in deleting this submission. Try Again")
        return render_template('submissions.html',submissions=current_user.submissions,problems=problems)

    
# Problem Description and API call on submission
@app.route('/problem/<int:problem_id>', methods= ['GET' , 'POST'])
@login_required
@contestant_required
def solve_problem(problem_id):
    if request.method == 'GET':
        problem = Problem.query.filter(Problem.id == problem_id).all()
        pblm_parameters_list = [problem[0].id , problem[0].title , problem[0].description , problem[0].sample_input , problem[0].sample_output , problem[0].exe_time , problem[0].exe_space]
        return render_template('problem.html' , Problem_Parameters = pblm_parameters_list)
    else :
        # Input information, change these according to your request
        output = request.get_json()
        problem = Problem.query.filter(Problem.id == output['problem_id']).all()
        pblm_parameters_list = [problem[0].id , problem[0].title , problem[0].description , problem[0].sample_input , problem[0].sample_output , problem[0].exe_time , problem[0].exe_space]
        
        userCode = output['userCode']
        test_input = problem[0].judging_testcases
        expected_output = problem[0].exp_testcases_output
        time_limit = problem[0].exe_time # in seconds
        memory_limit = problem[0].exe_space # in KB

        # Output information
        status = "" # Accepted/ Wrong Answer / Compilation Error
        compile_output = "" # Will contain the compiler output if there is a compilation error


        # base64 encoding the text data
        userCode_encoded = (base64.b64encode(userCode.encode("utf-8"))).decode("utf-8")
        test_input_encoded = (base64.b64encode(test_input.encode("utf-8"))).decode("utf-8")
        expected_output_encoded = (base64.b64encode(expected_output.encode("utf-8"))).decode("utf-8")


        url = "https://judge0-ce.p.rapidapi.com/submissions"

        querystring = {"base64_encoded":"true","wait":"true","fields":"*"}

        payload = {
            "language_id": 50,
            "source_code": userCode_encoded,
            "stdin": test_input_encoded,
            "expected_output" : expected_output_encoded,
            "cpu_time_limit" : time_limit,
            "memory_limit" : memory_limit
        }
        headers = {
            "content-type": "application/json",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": 'bf1c68d90fmsh23eab7668080859p1cb108jsn2275494bdbe0',
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }

        # Getting the response
        response = requests.post(url, json=payload, headers=headers, params=querystring)

        API_data = response.json()

        status = API_data["status"]["description"]
        compile_output_encoded = API_data["compile_output"]

        if(compile_output_encoded!=None):
            compile_output = base64.b64decode(compile_output_encoded)
            compile_output = compile_output.decode("utf-8")

        submit_solution = Submissions()
        submit_solution.user_code = userCode
        submit_solution.user_id = current_user.id
        submit_solution.problem_id = output['problem_id']
        submit_solution.status = status

        try:
            db.session.add(submit_solution)
            db.session.commit()
        except:
            flash("There is a problem in submitting the solution. Please Try Again")

        flash(status,status)
        problems = Problem.query.all()
        return jsonify({'redirect':url_for('get_submissions',id=current_user.id)})