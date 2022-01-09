from flask import Flask,render_template,request
import mysql.connector
from flask import Flask, render_template, request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,render_template,url_for, request, session,logging,redirect,flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from datetime import datetime
import re

engine=create_engine("mysql+pymysql://root:@localhost/matchmaker")					#mysql+pymysql://username:password@localhost/databasename
DDB=scoped_session(sessionmaker(bind=engine))

app=Flask(__name__,template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/matchmaker"
db = SQLAlchemy(app)

useremail=" "
username=" "
id=" "
res="error"
sex=" "
personality=" "
prefer=" "
matchid=" "
matchres=" "

class Match(db.Model):

    serial = db.Column(db.Integer, primary_key=True)
    id=db.Column(db.String(30), nullable=False)
    age=db.Column(db.String(5), nullable=False)
    sex= db.Column(db.String(30), nullable=False)
    personality = db.Column(db.String(30), nullable=False)
    eating = db.Column(db.String(30), nullable=False)
    hobby = db.Column(db.String(100), nullable=False)
    quality = db.Column(db.String(100), nullable=False)
    wyr1 = db.Column(db.String(30), nullable=False)
    wyr2 = db.Column(db.String(30), nullable=False)
    wyr3 = db.Column(db.String(30), nullable=False)
    prefer = db.Column(db.String(12), nullable=False)
    about = db.Column(db.String(120), nullable=False)

class Found(db.Model):
    id=db.Column(db.String, primary_key=True)
    id2=db.Column(db.String(30), nullable=False)

@app.route("/")
@app.route("/match", methods = ['GET', 'POST'])
def match():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matchmaker"
    )
    msg=""
    mycursor = mydb.cursor()
    if (request.method == 'POST'):
        '''Add entry to the database'''
        id=request.form.get('id')
        age = request.form.get('age')
        sex = request.form.get('gender')
        personality = request.form.get('peronality')
        eat = request.form.get('eating')
        h = request.form.getlist("hob")
        hobbies = ' '.join(map(str, h))
        q = request.form.getlist("quality")
        qual = ' '.join(map(str, q))
        wyr1 = request.form.get('WoulduRather1')
        wyr2 = request.form.get('WoulduRather2')
        wyr3 = request.form.get('WoulduRather3')
        prefer = request.form.get('prefer')
        about = request.form.get('abt')
        # mycursor.execute("SELECT * FROM match WHERE id='" + id + "'")
        # account = mycursor.fetchone()
        # if account:
        #     msg = 'Details already exists !'
        #     return render_template("match.html" , msg=msg)
        entry = Match(id=id,age=age,sex=sex,personality=personality,eating=eat,hobby=hobbies,quality=qual,wyr1=wyr1,wyr2=wyr2,wyr3=wyr3,prefer=prefer,about=about)
        db.session.add(entry)
        db.session.commit()
        if prefer is 'Same':
            mycursor.execute(
                "select a.id from `match` as a inner join `match` as b on a.serial = b.serial+1 where a.sex = b.sex and a.prefer = b.prefer and a.personality != b.personality and ( a.wyr1 = b.wyr1 or a.wyr2 = b.wyr2 or a.wyr3 = b.wyr3 )")
            matchid=mycursor.fetchone()
        else:
            mycursor.execute(
                "select a.id from `match` as a inner join `match` as b on a.serial = b.serial+1 where a.sex != b.sex and a.prefer = b.prefer and a.personality != b.personality and ( a.wyr1 = b.wyr1 or a.wyr2 = b.wyr2 or a.wyr3 = b.wyr3 )")
            matchid = mycursor.fetchone()
        if(matchid is None):
            msg = "We will get back at you!"
            return render_template("match.html", msg=msg)
        else:
            msg = "We found the perfect match for you  "
            idd2 = matchid[0]
            id2 =str(idd2)
            entry = Found(id=id, id2=id2)
            db.session.add(entry)
            db.session.commit()
            mycursor.execute("select id,email from registered where id='" + str(matchid[0]) + "'")
            e = mycursor.fetchone()
            iid=e[0]
            em=e[1]
            email = str(em)
            enroll = str(iid)
            mycursor.execute("select about from `match` where id = '" + str(matchid[0]) + "'")
            a=mycursor.fetchone()
            abt=a[0]
            abtt=str(abt)
            return render_template("match.html", msg=(msg+email+abtt))
    mydb.commit()
    mycursor.close()
    return render_template('match.html')


app.secret_key = 'some secret key'
app.run(debug=True)

