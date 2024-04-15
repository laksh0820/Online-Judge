from flask import Flask,render_template,redirect,request,flash,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,current_user,logout_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from Project import app,db,mail
from Project.forms import SignInForm,SignUpForm,ProblemForm,ResetPasswordForm,RequestResetForm,FeedbackForm,DeleteUserForm
from Project.models import Problem,User,Submissions
import os
import os.path
import time
import datetime

# Home Page
@app.route('/')
def home(): 
    return render_template('home.html')

def judge_required(inner_func):
    def wrapped_function_judge(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Judge' and current_user.type != 'Admin'):
            flash("Please log in as Judge to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapped_function_judge.__name__ = inner_func.__name__
    return wrapped_function_judge

def contestant_required(inner_func):
    def wrapped_function_contestant(*args,**kwargs):
        if (current_user.is_authenticated) and (current_user.type != 'Contestant' and current_user.type != 'Admin'):
            flash("Please log in as Contestant to access this page",'error')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapped_function_contestant.__name__ = inner_func.__name__
    return wrapped_function_contestant

def confirmation_required(inner_func):
    def wrapper(*args,**kwargs):
        if current_user.is_confirmed == False:
            flash("Please confirm your email to access this page",'warning')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapper.__name__ = inner_func.__name__
    return wrapper

def verification_required(inner_func):
    def wrapper(*args,**kwargs):
        if current_user.is_verified == False:
            flash("Please wait for 24 hours until Admin verifies you",'warning')
            return redirect(url_for('home'))
        return inner_func(*args,**kwargs)
    wrapper.__name__ = inner_func.__name__
    return wrapper

# To generate token from User email
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email,salt=app.config['SECURITY_PASSWORD_SALT'])

# To confirm the token and return the email
def confirm_token(token,expiration = 3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt = app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        return email
    except Exception:
        return False

# To confirm the email
@app.route('/confirm_email/<token>', methods=['GET','POST'])
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed",'success')
        return redirect(url_for('home'))
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()
        if current_user.type == 'Contestant':
            flash("You have successfully confirmed your email.")
        else:
            flash("You have successfully confirmed your email. Please wait for 24 hours until Admin verifies you to access Judge page.")
        return redirect(url_for('home'))
    flash("Token expired or invalid.Please register again..")
    return redirect(url_for('signup'))

# To send the email
def send_email(to,subject,template):
    msg = Message(
        subject=subject,
        sender=app.config["MAIL_DEFAULT_SENDER"],
        recipients=[to],
        html=template
    )
    mail.send(msg)

# To resend the confirmation mail
@app.route('/resend',methods=['GET','POST'])
@login_required
def resend_confirmation_mail():
    if current_user.is_confirmed:
        flash("Account already confirmed","success")
        return redirect(url_for('home'))
    token = generate_token(current_user.email)
    confirm_url = url_for('confirm_email',token=token,_external=True)
    html=render_template('confirm_email.html',confirm_url=confirm_url)
    subject = "Email validation Project ZetaX"
    send_email(current_user.email,subject,html)
    flash("A new confirmation email has been sent.","success")
    return redirect(url_for('inactive'))

# To render the inactive page
@app.route('/inactive')
@login_required
def inactive():
    if current_user.is_confirmed == True:
        flash("Already email confirmed")
        return redirect(url_for('home'))
    return render_template('inactive.html')

# Sign in to an existing user
@app.route('/signin',methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        flash("Already signed in")
        return redirect(url_for('home'))
    
    form = SignInForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,str(form.password.data)):
                login_user(user,remember=form.remember_me.data)
                flash("Logged in Successfully")
                if user.type == 'Admin':
                    return redirect(url_for('admin.index'))
                else:
                    return render_template('home.html')
            else:
                flash("Wrong Password!! Try Again",'error')
        else:
            flash("User not Found!! Try Again",'error')
    return render_template('signin.html',form=form)

# Forget password
@app.route('/forget_password',methods=['GET','POST'])
def forget_password():
    form = RequestResetForm()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token=generate_token(email)
            request_URL = url_for('reset_password',token=token,_external=True)
            template = render_template('reset_password_request.html',request_URL=request_URL)
            subject = "Reset Password Request"
            send_email(email,subject,template)
            flash('An email has been sent to you containing the instructions to reset the password','success')
            return redirect(url_for('home'))
        else:
            flash("User not found",'error')
            return redirect(url_for('home'))

    return render_template('forget_password.html',form=form)
        
# Reset passwrod
@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    email=confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    if user:
        form = ResetPasswordForm()

        if form.validate_on_submit():
            user.password = generate_password_hash(str(form.new_password.data))
            db.session.commit()
            flash("Password updated successfully",'success')
            if current_user.is_authenticated:
                return redirect(url_for('home'))
            else:
                return redirect(url_for('signin'))

        return render_template('reset_password.html',form=form,token=token)

    flash("Invalid token or token expired. Please Try Again",'error')
    return redirect(url_for('forget_password'))

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
                token = generate_token(newUser.email)
                confirm_url=url_for('confirm_email',token=token,_external=True)
                html=render_template('confirm_email.html',confirm_url=confirm_url)
                subject = "Email validation Project ZetaX"
                send_email(newUser.email,subject,html)
                login_user(newUser, remember=False)
                flash("User Added Successfully")
            except:
                return "Unable to enter User to the Database"
            form.name.data = ''
            form.email.data = ''
            form.password.data = ''
            form.confirm_password.data = ''
            form.type.data = ''

            return render_template('inactive.html')
        elif user_name is None:
            flash('This email already exits. Please sign in','error')
        else:
            flash('This name already exits. Please enter a different name','error')
            form.name.data = ''
            return render_template('signup.html',form=form)

        return redirect(url_for('signin'))
    return render_template('signup.html',form = form)

# Logout of a user account
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out Successfully")
    return redirect(url_for('signin'))

# View Current user info
@app.route('/view_info/<int:id>',methods=['GET','POST']) 
@login_required
def view_info(id):
    user = User.query.get_or_404(id)
    if user:
        return render_template('view_info.html',user=user)
    else:
        flash("User not found")
        return redirect(url_for('home'))

# Delete an user
@app.route('/delete_user/<int:id>',methods=['GET','POST'])
@login_required
def delete_user(id):
    form = DeleteUserForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(id)
        if user:
            password = form.password.data
            if check_password_hash(user.password,str(password)):

                if user.type == 'Contestant':
                    for submission in user.submissions:
                        try:
                            db.session.delete(submission)
                            db.session.commit()
                        except:
                            flash("There is some issue in deleting the user. Please Try Again.. ")
                            return redirect(url_for('delete_user',id=user.id))
                else: 
                    for problem in user.problems:
                        for submission in problem.submission:
                            try:
                                db.session.delete(submission)
                                db.session.commit()
                            except:
                                flash("There is some issue in deletion. Please Try Again..")
                                return redirect(url_for('delete_user',id=user.id))
                        try:
                            db.session.delete(problem)
                            db.session.commit()
                        except:
                            flash("There is some issue in deleting the user. Please Try Again.. ")
                            return redirect(url_for('delete_user',id=user.id))
                    
                try:
                    logout_user()
                    db.session.delete(user)
                    db.session.commit()
                    flash("Successfully deleted",'success')
                    return redirect(url_for('home'))
                except:
                    flash("Oops! There is some problem in deleting the user. Please Try Again..")
                    return redirect(url_for('delete_user',id=user.id))
            else:
                flash("Wrong Password! Try Again",'error')
                return redirect(url_for('delete_user',id=user.id))
        else:
            flash('User not found')
            return redirect(url_for('home'))
    
    return render_template('confirm_for_deletion.html',form=form,user=current_user)

# Display the Online editor
@app.route('/onlineIDE',methods=['GET','POST'])
def online_coding():
    if request.method == 'GET':
        return render_template('onlineIDE.html')
    else:
        output_json = request.get_json()
        userCode = output_json['userCode']
        stdin = output_json['stdin']
        max_allowed_time = 5+2 # seconds
        output = ""
        compile_output = ""
        time_taken = 0
        memory_taken = 0
        flag = 0

        path = r"./runner_C_files"

        # create a separate folder for each submission
        now = datetime.datetime.now()
        now = now.strftime('%Y-%m-%d_%H-%M-%S')

        os.system(f"cd {path} && mkdir {now}")

        path = f"{path}/{now}"
        file_name = "main.c"
        file_path = os.path.join(path, file_name)

        f = open(file_path, "w")
        f.write(userCode)
        f.close()

        input_file_name = "input.txt"
        input_file_path = os.path.join(path, input_file_name)

        f = open(input_file_path, "w")
        f.write(stdin)
        f.close()

        # userCode is stored in userCode.c
        os.system(f"cd {path} && gcc -Wall main.c 2> compiler_message.txt")
        time.sleep(2) # Required to compile in 2 seconds

        exe_path = f"{path}/a.out"

        # if a.exe is created, run it, else status is compilation error
        if os.path.isfile(exe_path):
            os.system(f"cd {path} && timeout {max_allowed_time}s ./a.out < input.txt; echo $? > timeout_status.txt")
            
            # Check the timeout status. If time limit exceeds then set status to TLE
            timeout_status_path = os.path.join(path,"timeout_status.txt")
            with open(timeout_status_path,'r') as f:
                timeout_status = f.read()
                timeout_status = timeout_status.split()

            if timeout_status[0]=='0':
                # Run the program and get the output.txt and time_taken.txt
                os.system(f"cd {path} && command time -f '%M' -o memory_taken.txt \\time -f '%U' -o time_taken.txt ./a.out < input.txt > output.txt")

                # Read time_taken.txt
                time_taken_path = os.path.join(path,"time_taken.txt")
                with open(time_taken_path,'r') as f:
                    time_taken = f.read()
                    if time_taken != '':
                        time_taken = float(time_taken)
                    else:
                        time_taken = 0
                
                # Read memory_taken.txt
                memory_taken_path = os.path.join(path,"memory_taken.txt")
                with open(memory_taken_path,'r') as f:
                    memory_taken = float(f.read())

                # If time_taken is less than the time_limit, read output.txt else set status to TLE 
                if time_taken <= max_allowed_time:
                    output_path = os.path.join(path, "output.txt")
                    with open(output_path,'r') as f:
                        output = f.read()
                else:
                    output = ""
                    compile_output = "Time Limit Exceeded"
                    time_taken = max_allowed_time

                os.remove(f"{path}/time_taken.txt")
                os.remove(f"{path}/memory_taken.txt")
                os.remove(f"{path}/output.txt")
                flag = 1
            
            elif timeout_status[0]=='124':
                output = ""
                compile_output = "Time Limit Exceeded"
                time_taken = max_allowed_time
                memory_taken = 0
                flag = 1

            elif timeout_status[0]=='139':
                output = ""
                compile_output = "Segmentation fault"
                time_taken = 0
                memory_taken = 0
                flag = 1
            
            else:
                output = ""
                compile_output_path = os.path.join(path, "compiler_message.txt")
                with open(compile_output_path,'r') as f:
                    compile_output = f.read()

            os.remove(f"{path}/timeout_status.txt")
            os.remove(f"{path}/a.out")
        else:
            output = ""
            compile_output_path = os.path.join(path, "compiler_message.txt")
            with open(compile_output_path,'r') as f:
                compile_output = f.read()
        
        if output == "" and flag==0:
            compile_output_path = os.path.join(path, "compiler_message.txt")
            with open(compile_output_path,'r') as f:
                compile_output = f.read()
        
        # Remove the create files
        os.remove(f"{path}/main.c")
        os.remove(f"{path}/compiler_message.txt")
        os.remove(f"{path}/input.txt")
        os.rmdir(path)

        # Execution time
        exe_time = "\nExecution time of the program is : "+str(time_taken * 1000)+" milliseconds"
        exe_memory = "\nExecution memory of the program is : "+str(memory_taken)+" kilobytes"
        if output != "":
            output = output + exe_time
            output = output + exe_memory
        compile_output = compile_output + exe_time
        compile_output = compile_output + exe_memory

        return jsonify({'stdout':output,'compile_output':compile_output})

# Post a new Problem
@app.route('/judge',methods = ['GET','POST'])
@login_required
@judge_required
@confirmation_required
@verification_required
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
@confirmation_required
@verification_required
def show_judge_problems(id):
    judge = User.query.get_or_404(id)
    return render_template('show_judge_problems.html',problems=judge.problems)

# To modify the problems created by the current user(Judge)
@app.route('/modify_problem/<int:id>',methods=['GET','POST'])
@login_required
@judge_required
@confirmation_required
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
        for submission in problem.submission:
            try:
                db.session.delete(submission)
                db.session.commit()
            except:
                flash("There is some issue in deletion. Please Try Again..")
                return render_template('show_judge_problems.html',problems=current_user.problems)
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
@confirmation_required
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
@confirmation_required
def get_submissions(id):
    contestant = User.query.get_or_404(id)
    problems = Problem.query.all()
    return render_template('submissions.html',submissions=contestant.submissions,problems=problems)

# To delete the submissions posted by the current user(Contestant)
@app.route('/delete_submission/<int:id>',methods=['GET','POST'])
@login_required
@contestant_required
@confirmation_required
def delete_submission(id):
    problems = Problem.query.all()
    submission = Submissions.query.get_or_404(id)

    try:
        db.session.delete(submission)
        db.session.commit()

        flash("Successfully deleted","message")

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
        # Output variables
        status = ""
        time_taken = 0
        memory_taken = 0
        compile_output = ""

        output = request.get_json()
        problem = Problem.query.filter(Problem.id == output['problem_id']).all()
        pblm_parameters_list = [problem[0].id , problem[0].title , problem[0].description , problem[0].sample_input , problem[0].sample_output , problem[0].exe_time , problem[0].exe_space]
        
        userCode = output['userCode']
        test_input = problem[0].judging_testcases
        expected_output = problem[0].exp_testcases_output
        time_limit = float(problem[0].exe_time) # in seconds
        memory_limit = problem[0].exe_space # in KB

        expected_output_list = expected_output.split()

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

        path = r"./runner_C_files"

        # create a separate folder for each submission
        now = datetime.datetime.now()
        now = now.strftime('%Y-%m-%d_%H-%M-%S')

        os.system(f"cd {path} && mkdir {now}")

        path = f"{path}/{now}"
        file_name = "main.c"
        file_path = os.path.join(path, file_name)

        f = open(file_path, "w")
        f.write(userCode)
        f.close()

        input_file_name = "input.txt"
        input_file_path = os.path.join(path, input_file_name)
    
        f = open(input_file_path, "w")
        f.write(test_input)
        f.close()

        # userCode is stored in main.c
        os.system(f"cd {path}; gcc -Wall main.c 2> compiler_message.txt")
        time.sleep(1) # Required to compile in 1 second

        exe_path = f"{path}/a.out"

        extra_sys_time = time_limit+1

        # if a.exe is created, run it, else status is compilation error
        if os.path.isfile(exe_path):
            os.system(f"cd {path} && timeout {extra_sys_time}s ./a.out < input.txt > output_t.txt; echo $? > timeout_status.txt")
            
            # Check the timeout status. If time limit exceeds then set status to TLE
            timeout_status_path = os.path.join(path,"timeout_status.txt")
            with open(timeout_status_path,'r') as f:
                timeout_status = f.read()
                timeout_status = timeout_status.split()

            if timeout_status[0]=='0':
                # Run the program and get the output.txt and time_taken.txt
                os.system(f"cd {path} && command time -f '%M' -o memory_taken.txt \\time -f '%U' -o time_taken.txt ./a.out < input.txt > output.txt")

                # Read time_taken.txt
                time_taken_path = os.path.join(path,"time_taken.txt")
                with open(time_taken_path,'r') as f:
                    time_taken = f.read()
                    if time_taken != '':
                        time_taken = float(time_taken)
                    else:
                        time_taken = 0
                
                # Read memory_taken.txt
                memory_taken_path = os.path.join(path,"memory_taken.txt")
                with open(memory_taken_path,'r') as f:
                    memory_taken = float(f.read())

                # If time_taken is less than the time_limit, read output.txt else set status to TLE 
                if time_taken<=time_limit and memory_taken<=memory_limit:
                    output_path = os.path.join(path, "output.txt")
                    with open(output_path,'r') as f:
                        output = f.read()
                        output_list = output.split()
                elif time_taken > time_limit:
                    status = "Time Limit Exceeded"
                    time_taken = time_limit
                else:
                    status = "Memory Limit Exceeded"
                    memory_taken = memory_limit

                os.remove(f"{path}/time_taken.txt")
                os.remove(f"{path}/memory_taken.txt")
                os.remove(f"{path}/output.txt")

            elif timeout_status[0]=='124':
                status = "Time Limit Exceeded"
                time_taken = time_limit
                memory_taken = 0

            elif timeout_status[0]=='139':
                status = "Segmentation fault"
                time_taken = 0
                memory_taken = 0
            
            else:
                status = "Runtime Error"
                time_taken = 0
                memory_taken = 0

            os.remove(f"{path}/timeout_status.txt")
            os.remove(f"{path}/a.out")
            os.remove(f"{path}/output_t.txt")
            compile_output = ""

        else:
            status = "Compilation Error"
            output = ""
            time_taken = 0
            memory_taken = 0
        
        compile_output_path = os.path.join(path, "compiler_message.txt")
        with open(compile_output_path,'r') as f:
            compile_output = f.read()
        
        if compile_output != "" and status == "":
            status = "Compilation Error"

        # If times are alright, check the output if it is correct
        if status == "":
            status = "Accepted"
            if len(output_list) == len(expected_output_list):
                for i in range(0,len(output_list)):
                    if output_list[i] != expected_output_list[i]:
                        status = "Wrong Answer"
                        break
            else:
                status = "Wrong Answer"
        
        # For cleaning up the files
        os.remove(f"{path}/main.c")
        os.remove(f"{path}/compiler_message.txt")
        os.remove(f"{path}/input.txt")
        os.rmdir(path)
                    
        # We have status, compile_output and time_taken

        # Update status
        submit_solution.status = status
        submit_solution.compile_output = compile_output
        submit_solution.time_taken = time_taken * 1000
        submit_solution.memory_taken = memory_taken
        try:
            db.session.commit()
        except:
            flash("There is a problem in submitting the solution. Please Try Again")

        flash(status,status)
        problems = Problem.query.all()
        return jsonify({'redirect':url_for('get_submissions',id=current_user.id)})


# Feedback for a problem
@app.route('/feedback/<int:id>',methods=['GET','POST'])
def feedback(id):
    form = FeedbackForm()
    problem = Problem.query.get_or_404(id)
    if form.validate_on_submit():
        subject="Issue in Problem {}".format(problem.title)
        user = User.query.get_or_404(problem.user_id)
        if user:
            receiver=user.email
            sender=current_user.email
            description=form.description.data
            msg = Message(
                recipients=[receiver],
                sender=sender,
                subject=subject
            )
            msg.body = description
            mail.send(msg)
            flash("Issue is successfully reported")
            return redirect(url_for('solve_problem',problem_id=problem.id))
        else:
            flash('User not found')
            return redirect(url_for('solve_problem',problem_id=problem.id))

    return render_template('feedback.html',problem=problem,form=form)
