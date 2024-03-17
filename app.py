from flask import Flask,render_template,redirect,request,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField, PasswordField, SubmitField,TextAreaField,RadioField
from wtforms.validators import DataRequired,EqualTo,Email
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,login_user,login_required,LoginManager,current_user,logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
app.config['SQLALCHEMY_BINDS'] = {'problems':'sqlite:///problem_set.db'}   
app.config['SECRET_KEY'] = 'projectzetaxksdkar37ro8hf83fh3892hmfijw38fh'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class SignUpForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(),Email(message="Invalid email address (should be of the form something@example.com)")])
    password = PasswordField("Password",validators=[DataRequired(),EqualTo('confirm_password',message="Password does not match to Confirm Password. Please retype")])
    confirm_password = PasswordField("Confirm-Password",validators=[DataRequired()])
    type = RadioField("Type",validators=[DataRequired()],choices=[('Contestants','Contestants'),('Judge','Judge')])
    submit = SubmitField("Submit")

class SignInForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email(message="Invalid email address (should be of the form something@example.com)")])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Submit")

class ProblemForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    description = TextAreaField("Description",validators=[DataRequired()])
    sample_input = TextAreaField("Sample Input",validators=[DataRequired()])
    sample_output = TextAreaField("Sample Output",validators=[DataRequired()])
    exe_time = IntegerField("Expected Execution Time",validators=[DataRequired()])
    exe_space = IntegerField("Expected Execution Space",validators=[DataRequired()])
    submit = SubmitField("Submit")  

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False,unique=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"{self.name} - {self.type}"
    
class Problem(db.Model):
    __bind_key = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    sample_input = db.Column(db.String(100), nullable=False)
    sample_output = db.Column(db.String(100), nullable=False)
    exe_time = db.Column(db.Integer, nullable=False)
    exe_space = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.title} - {self.description}"

@app.route('/')
def home(): 
    return render_template('home.html',user=None)

# Sign in to an existing user
@app.route('/signin',methods=['GET','POST'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                flash("Logged in Successfully")
                return redirect(url_for('signin'))
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
            newUser.password = generate_password_hash(form.password.data,"sha256")
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

# @app.route('/contestant', methods= ['GET' , 'POST'])
# @login_required                                         # Cause You suck
# def solve_problems():
#     if request.method == 'POST':
#         pass
#     else:
#         problems_list = Problem.query.all()
#         return render_template('contestant.html' , ProblemSet = problems_list)
    
# @app.route('/onlineIDE')
# def online_coding():
#     pass

if __name__ == '__main__':
    app.run(debug=True)