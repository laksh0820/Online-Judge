from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///problem_set.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

problem_set_db = SQLAlchemy(app)
user_db = SQLAlchemy(app)

class Problem(problem_set_db.Model):
    id = problem_set_db.Column(problem_set_db.Integer, primary_key=True)
    title = problem_set_db.Column(problem_set_db.String(100), nullable=False)
    description = problem_set_db.Column(problem_set_db.String(2000), nullable=False)
    sample_input = problem_set_db.Column(problem_set_db.String(100), nullable=False)
    sample_output = problem_set_db.Column(problem_set_db.String(100), nullable=False)
    exp_time = problem_set_db.Column(problem_set_db.Integer, nullable=False)
    exp_space = problem_set_db.Column(problem_set_db.Integer, nullable=False)

    def __repr__(self):
        return '<Id %r>' % self.id

class user(user_db.Model):
    id = user_db.Column(user_db.Integer, primary_key=True)
    name = user_db.Column(user_db.String(100), nullable=False)
    type = user_db.Column(user_db.String(100), nullable=False)
    
    def __repr__(self):
        return '<Id %r>' % self.id

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.form == 'POST':
        newUser = user()
        newUser.name = request.form['name']
        newUser.type = request.form['type']

        try:
            user_db.session.add(newUser)
            user_db.session.commit(newUser)
            return render_template('/')
        except:
            return "Unable to enter user to the Database"
    else:
        return render_template('login.html')

@app.route('/judge/<int:id>',methods = ['POST'])
def post_problems(id):
    curr_user = user.query.get_or_404(id)
    
    newProblem = Problem()
    newProblem.title = request.form['title']
    newProblem.description = request.form['description']
    newProblem.sample_input = request.form['sample_input']
    newProblem.sample_output = request.form['sample_output']
    newProblem.exp_time = request.form['exp_time']
    newProblem.exp_space = request.form['exp_space']

    try:
        problem_set_db.session.add(newProblem)
        problem_set_db.session.commit(newProblem)
        return render_template('home.html')
    except:
        return "There is no such user found. Please Sign Up."

@app.route('/contestant')
def solve_problems():
    pass

@app.route('/onlineIDE')
def online_coding():
    pass

if __name__ == '__main__':
    app.run(debug=True)