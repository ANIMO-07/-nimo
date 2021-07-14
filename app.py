from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import desc

app=Flask(__name__)
app.secret_key="animo"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime=datetime.timedelta(minutes=10)

db = SQLAlchemy(app)

answers = pd.read_csv("static\\answers.csv")

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    roll = db.Column(db.String(100))
    name = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)

    def __init__(self,name,pwd,roll):
        self.roll=roll
        self.pwd=pwd
        self.name=name

@app.route('/', methods=["POST", "GET"])
def index():
    if "roll" in session:
        roll=session["roll"]
        found_user = users.query.filter_by(roll = roll).first()
        level=found_user.level

        if request.method=="POST":
            ans=request.form["ans"]
            if ans:
                if ans == answers["Answer"][level-1]:
                    level=level+1
                    found_user = users.query.filter_by(roll=roll).first()
                    session["level"]=level
                    time=int(datetime.datetime.utcnow().timestamp())
                    score=(1596223800-time)*level**2
                    found_user.score = score
                    found_user.level = level
                    db.session.commit()
                    return redirect(url_for("cont"))
                    
                else:
                    flash("Incorrect Answer, Try Again")
                    return redirect(url_for("index"))
            else:
                flash("Please input an answer")
                return redirect(url_for("index"))
        else:
            n = answers["Answer"].isna().idxmax()
            if level==n+1:
                #n=total questions
                flash("You have reached the end of the competition")
                return redirect(url_for("leaderboard"))
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
            found_user = users.query.filter_by(roll = roll).first()
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
            found_user = users.query.filter_by(roll = roll).first()
            if found_user:
                flash("This Roll Number has already been registered")
                return redirect(url_for("register"))
            else:
                session["level"]=0
                session["roll"]=roll
                usr =  users(name, pwd, roll)
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
    return render_template('leaderboard.html', values = users.query.order_by(users.score.desc()))

@app.route('/continue', methods=["POST", "GET"])
def cont():
    if request.method=="POST":
        return redirect(url_for("index"))
    else:
        return render_template("continue.html")

@app.route('/animo7121avia3156', methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        pin = request.form["pwd"]
        roll = request.form["rn"]
        name = request.form["nm"]
        pwd = request.form["ps"]
        score = request.form["sc"]
        level = request.form["lvl"]
        f = request.form["boioboi"]
        if (pin == "anmolthegreat" and roll):
            found_user = users.query.filter_by(roll = roll).first()
            if found_user:
                if f == "100":
                    found_user.name = name
                    found_user.pwd = pwd
                    found_user.score = score
                    found_user.level = level
                    db.session.commit()
                
                name = found_user.name
                pwd = found_user.pwd
                score = found_user.score
                level = found_user.level

                return render_template("admin.html", rn = roll, nm = name, ps = pwd, sc = score, lvl = level)
            
            else:
                flash("No such user")
                return redirect(url_for("admin"))
        else:
            flash("Incorrect Pass")
            return redirect(url_for("admin"))
    
    else:
        return render_template("admin.html")



if __name__=='__main__':
    db.create_all()
    app.run(debug=True)