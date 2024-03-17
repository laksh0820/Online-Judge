from flask import Flask,render_template,redirect,request,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField,RadioField
from wtforms.validators import DataRequired,EqualTo,Email,Regexp
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
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired(),EqualTo('confirm_password')])
    confirm_password = PasswordField("Confirm-Password",validators=[DataRequired()])
    type = RadioField("Type",validators=[DataRequired()],choices=[('Contestants','Contestants'),('Judge','Judge')])
    submit = SubmitField("Submit")

class SignInForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired()])
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
    exp_time = db.Column(db.Integer, nullable=False)
    exp_space = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.title} - {self.description}"

@app.route('/')
def home(): 
    return render_template('home.html',user=None)

@app.route('/signin',methods=['GET','POST'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                flash("Login Successfully")
                return redirect(url_for('signin'))
            else:
                flash("Wrong Password!! Try Again...")
        else:
            flash("User not Found!! Try Again...")
    return render_template('signin.html',form=form)
    
# Add User
@app.route('/signup',methods=['GET','POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            newUser = User()
            newUser.name = form.name.data
            newUser.email = form.email.data
            newUser.password = generate_password_hash(form.password.data,"sha256")
            newUser.type = form.type.data
            try:
                db.session.add(newUser)
                db.session.commit()
            except:
                return "Unable to enter User to the Database"
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        form.confirm_password.data = ''
        form.type.data = ''

        flash("User Added Successfully!!")
        return redirect(url_for('signup'))

    return render_template('signup.html',form = form)

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out Successfully")
    return redirect(url_for('signin'))

@app.route('/judge',methods = ['GET','POST'])
@login_required
def post_problems():
    if request.method == 'POST':
        newProblem = Problem()
        newProblem.title = request.form['title']
        newProblem.description = request.form['description']
        newProblem.sample_input = request.form['sample_input']
        newProblem.sample_output = request.form['sample_output']
        newProblem.exp_time = request.form['exp_time']
        newProblem.exp_space = request.form['exp_space']

        try:
            db.session.add(newProblem)
            db.session.commit()
            return render_template('home.html',user=None)
        except:
            return "Unable to enter the problem into the Database"
    else:
        return render_template('judge.html')

@app.route('/contestant', methods= ['GET' , 'POST'])    # Cause You suck
def solve_problems():
    if request.method == 'POST':
        pass
    else:
        problems_list = Problem.query.all()
        return render_template('contestant.html' , ProblemSet = problems_list)
    
# @app.route('/onlineIDE')
# def online_coding():
#     pass

if __name__ == '__main__':
    app.run(debug=True)