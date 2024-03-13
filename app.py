from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return '<Id %r>' % self.id

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/judge',methods = ['GET'])
def post_problems():
    return render_template('judge.html')

@app.route('/contestant')
def solve_problems():
    pass

@app.route('/onlineIDE')
def online_coding():
    pass

if __name__ == '__main__':
    app.run(debug=True)