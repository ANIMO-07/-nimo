from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.secret_key="animo"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime=timedelta(minutes=10)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    roll = db.Column(db.String(100))
    name = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    level = db.Column(db.Integer, default=0)

    def __init__(self,name,pwd,roll):
        self.roll=roll
        self.pwd=pwd
        self.name=name

@app.route('/', methods=["POST", "GET"])
def index():
    if "roll" in session:
        roll=session["roll"]
        level=session["level"]

        if request.method=="POST":
            answers=['q1', 'q2', 'q3', 'q4']
            ans=request.form["ans"]
            if ans:
                if ans == answers[level]:
                    level=level+1
                    found_user = users.query.filter_by(name=roll).first()
                    found_user.level = level
                    db.session.commit()
                    return render_template('continue.html')
                    
                else:
                    flash("Incorrect Answer, Try Again")
                    return redirect(url_for("index"))
            else:
                flash("Please input an answer")
                return redirect(url_for("index"))
        else:
            x='img'+str(level)+'.jpg'
            return render_template('game.html', n=level, qfile=x)
    else:
        return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method=="POST":
        session.permanent=False
        roll=request.form["rn"]
        pwd=request.form["pwd"]

        if (roll and pwd):
            found_user = users.query.filter_by(name = roll).first()
            if found_user:
                if pwd == found_user.pwd:
                    session["roll"]=roll
                    session["level"] = found_user.level
                    return redirect(url_for("index"))
                else:
                    flash("Incorrect Username/Password")
                    return render_template("login.html")
            else:
                flash("Incorrect Username/Password")
                return render_template("login.html")
        else:
            flash("One or more fields left empty")
            return render_template("login.html")
    else:
        if "roll" in session:
            flash("Already logged in")
            return redirect(url_for("index"))
        else:
            return render_template('login.html')
        

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method=="POST":
        session.permanent=False
        name=request.form["nm"]
        pwd=request.form["pwd"]
        roll=request.form["rn"]

        if (name and pwd and roll):
            found_user = users.query.filter_by(name = roll).first()
            if found_user:
                flash("This Roll Number has already been registered")
                return redirect(url_for("register"))
            else:
                session["level"]=0
                session["roll"]=roll
                usr =  users(roll, name, pwd)
                db.session.add(usr)
                db.session.commit()
                flash("Registered Successfully")
                return redirect(url_for("login"))
        else:
            flash("Multiple fields left empty")
            return render_template('register.html')
    else:
        if "roll" in session:
            flash("Already logged in")
            return redirect(url_for("index"))
        else:
            return render_template('register.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', values = users.query.order_by(users.level.desc()))

if __name__=='__main__':
    db.create_all()
    app.run(debug=True)