from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy

started_app = 0
fun = 0

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {'problems':'sqlite:///problem_set.db'}   

db = SQLAlchemy(app)

class user(db.Model):
    name = db.Column(db.String(100), nullable=False,primary_key=True)
    email = db.Column(db.String(100), nullable=False)
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

@app.route('/templates/signin.html',methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        curr_user = user.query.get_or_404(request.form['name'])
        if curr_user == None:
            return "No Such User Found"
        
        if request.form['password'] != curr_user.password:
            return "Wrong Password"
        
        return render_template('home.html',user=curr_user)
    else:
       return render_template('signin.html')

@app.route('/templates/signup.html',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        newUser = user()
        newUser.name = request.form['name']
        newUser.email = request.form['email']
        newUser.password = request.form['password']
        newUser.type = request.form['selection']
        try:
            db.session.add(newUser)
            db.session.commit()
            return render_template('home.html',user=None)
        except:
            return "Unable to enter user to the Database"
    else:
        return render_template('signup.html') 

@app.route('/templates/judge.html',methods = ['GET','POST'])
def post_problems():
    # curr_user = user.query.get_or_404(request.form['name'])

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

# @app.route('/templates/contestant.html', methods= ['GET'])
# def solve_problems():
#     pass

# @app.route('/onlineIDE')
# def online_coding():
#     pass

if __name__ == '__main__':
    app.run(debug=True)