from flask import Flask, render_template, request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,render_template,url_for,request,session,logging,redirect,flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from datetime import datetime
engine=create_engine("mysql+pymysql://root:@localhost/matchmaker")					#mysql+pymysql://username:password@localhost/databasename
DDB=scoped_session(sessionmaker(bind=engine))

# sess=session()
app = Flask(__name__,template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/matchmaker"
db = SQLAlchemy(app)

useremail=" "
username=" "
usernamedata=" "
res="error"
sex=" "
personality=" "
prefer=" "
matchid=" "
matchres=" "

class Registered(db.Model):
    '''
    serial,enroll,sex,age,personality,eating,hobby,quality,wyr1,wyr2,wyr3,prefer,about,enroll2
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(15), nullable=False)

class MutualCrush(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(30), nullable=False)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30), nullable=True)
    id2 = db.Column(db.String(12), nullable=False)


class Match(db.Model):
    '''
        serial,enroll,sex,age,personality,eating,hobby,quality,wyr1,wyr2,wyr3,prefer,about,enroll2
        '''
    id=db.Column(db.String, primary_key=True)
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
    id2=db.Column(db.String(12), nullable=False)


class Contacts(db.Model):
    serial = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(5), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    msg = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(30), nullable=False)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        userid = request.form.get('userid')
        user = request.form.get('username')
        mail = request.form.get('useremail')
        password = request.form.get('password')
        entry = Registered(id=userid, name=user, email=mail, password=password)
        db.session.add(entry)
        db.session.commit()
    return render_template('register.html')

@app.route("/", methods = ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        id = request.form.get('userid')
        password = request.form.get('password')
        global username,usernamedata,useremail
        usernamedata = DDB.execute("SELECT id FROM registered WHERE id=:id", {"id": id}).fetchone()
        passworddata = DDB.execute("SELECT password FROM registered WHERE id=:id", {"id": id}).fetchone()
        username=DDB.execute("SELECT name FROM registered WHERE id=:id", {"id": id}).fetchone()
        ueremail=DDB.execute("SELECT email FROM registered WHERE id=:id", {"id": id}).fetchone()
        if usernamedata is None:
            flash("No user", "danger")
            return render_template('register.html')
        else:
            if passworddata is password :
                return render_template('home.html')
            else:
                flash( "wrong password")
            # return render_template('dashboard.html')
    return render_template('login.html')




@app.route("/crush", methods = ['GET', 'POST'])
def crush():
    if(request.method=='POST'):
        '''Add entry to the database'''
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        id = request.form.get('id')
        entry = MutualCrush( id=usernamedata, fname=fname, lname=lname, id2=id)
        db.session.add(entry)
        db.session.commit()
        result=DDB.execute("SELECT id FROM mutual_crush WHERE id=:id2", {"id": id}).fetchone()
        if result is None:
            global res
            res="Oops! looks like your match is not registered"
        else:
            if result is id:
                res="congratulations!"
            else:
                res="sorry!!"

    return render_template('crush.html',res=res)

@app.route("/match", methods = ['GET', 'POST'])
def match():
    global sex,personality,prefer
    if (request.method == 'POST'):
        '''Add entry to the database'''
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
        global usernamedata
        entry = Match(id=usernamedata,age=age,sex=sex,personality=personality,eating=eat,hobby=hobbies,quality=qual,wyr1=wyr1,wyr2=wyr2,wyr3=wyr3,prefer=prefer,about=about)
        db.session.add(entry)
        db.session.commit()
    return render_template('match.html')

@app.route("/match", methods = ['GET', 'POST'])
def found():
    global usernamedata,sex,personality,prefer,matchid,matchres
    if (sex is "Male" and personality is "Extrovert" and prefer is "Female"):
        matchid=DDB.execute("SELECT id FROM match WHERE sex = 'Female' and prefer = 'Male' and personality in ('Ambivert','Introvert')").fetchone()
    elif (sex is "Male" and personality is "Introvert" and prefer is "Female"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Female' and prefer = 'Male' and personality in ('Ambivert','Extrovert')").fetchone()
    elif (sex is "Male" and personality is "Ambivert" and prefer is "Female"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Female' and prefer = 'Male'").fetchone()
    elif (sex is "Male" and personality is "Extrovert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Male' and personality in ('Ambivert','Introvert')").fetchone()
    elif (sex is "Male" and personality is "Introvert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Male' and personality in ('Ambivert','Extrovert')").fetchone()
    elif (sex is "Male" and personality is "Ambivert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Male'").fetchone()
    elif (sex is "Female" and personality is "Extrovert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Female' and personality in ('Ambivert','Introvert')").fetchone()
    elif (sex is "Female" and personality is "Introvert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Female' and personality in ('Ambivert','Extrovert')").fetchone()
    elif (sex is "Female" and personality is "Ambivert" and prefer is "Male"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Male' and prefer = 'Female'").fetchone()
    elif (sex is "Female" and personality is "Extrovert" and prefer is "Female"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Female' and prefer = 'Female' and personality in ('Ambivert','Introvert')").fetchone()
    elif (sex is "Female" and personality is "Introvert" and prefer is "Female"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Female' and prefer = 'Female' and personality in ('Ambivert','Extrovert')").fetchone()
    elif (sex is "Female" and personality is "Ambivert" and prefer is "Female"):
        matchid = DDB.execute(
            "SELECT id FROM match WHERE sex = 'Female' and prefer = 'Female'").fetchone()
    if matchid is None:
        matchres="We will get back to you"
    else:
        matchres="match found"
        entry = Found(id=usernamedata, id2=matchid)
        db.session.add(entry)
        db.session.commit()


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('mail')
        msg = request.form.get('msg')
        entry = Contacts(name=name, email=email, msg=msg, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')

if __name__ == "__main__":
    app.secret_key = 'some secret key'
app.run(debug=True)


