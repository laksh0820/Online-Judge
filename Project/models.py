from Project import db,app
from flask_login import UserMixin,LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False,unique=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    submissions = db.relationship('Submissions',backref='user')
    problems = db.relationship('Problem',backref='user')
    
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
    judging_testcases = db.Column(db.String(1000000),nullable=False)
    exp_testcases_output = db.Column(db.String(1000000),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submission = db.relationship('Submissions',backref='problem')

    def __repr__(self):
        return f"{self.title} - {self.description}"

class Submissions(db.Model):
    __bind_key = 'submissions'
    id = db.Column(db.Integer,primary_key=True)
    user_code = db.Column(db.String(100000))
    status = db.Column(db.String(100),nullable=False)
    compile_output = db.Column(db.String(100000))
    time_taken = db.Column(db.Float)
    memory_taken = db.Column(db.Float)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    problem_id = db.Column(db.Integer,db.ForeignKey('problem.id'))

    def __repr__(self):
        return f"{self.id} - {self.user_code}"