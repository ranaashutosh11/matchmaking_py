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

class Registered(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(15), nullable=False)


class MutualCrush(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    id2 = db.Column(db.String(12), nullable=False)


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


class Contacts(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(30), nullable=False)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    msg=''
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matchmaker"
    )
    # global userid
    mycursor = mydb.cursor()
    if (request.method == 'POST'):
        '''Add entry to the database'''
        userid = request.form.get('userid')
        user = request.form.get('username')
        mail = request.form.get('useremail')
        password = request.form.get('password')
        mycursor.execute("SELECT * FROM registered WHERE id='" + userid + "'")
        account = mycursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', userid):
            msg = 'Userid must contain only characters and numbers !'
        elif not username or not password or not mail:
            msg = 'Please fill out the form !'
        else:
            entry = Registered(id=userid, name=user, email=mail, password=password)
            db.session.add(entry)
            db.session.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html',msg=msg)


@app.route('/')
@app.route("/login", methods = ['GET', 'POST'])
def login():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matchmaker"
    )
    mycursor=mydb.cursor()
    global username, useremail, userid
    if request.method=='POST':

        signin=request.form
        userid=signin['userid']
        password=signin['password']
        mycursor.execute("select * from registered where  id='" + userid + "' and password= '" + password + "'")
        account = mycursor.fetchone()
        if account:
            session['loggedin'] = True
            # session['userid'] = account['id']
            return render_template('home.html')
        else:
            msg = 'Incorrect username / password !'
        return render_template('login.html', msg=msg)

    mydb.commit()
    mycursor.close()
    return render_template('login.html')


@app.route("/crush", methods = ['GET', 'POST'])
def crush():
    msg =''
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="matchmaker"
    )
    global useremail
    mycursor=mydb.cursor()
    if request.method=='POST':

        # signin=request.form
        name=request.form.get('name')
        id2 = request.form.get('id')
        id = request.form.get('userid')
        # name=signio['name']
        # id2=signin['id']
        # id=signin['userid']
        entry = MutualCrush(id=id, name=name,  id2=id2)
        db.session.add(entry)
        db.session.commit()
        # mycursor.execute("insert into mutual_crush (id,name,id2)values(%s,%s,%s)",(id,name,id2))
        mycursor.execute("select id2 from mutual_crush where id='" + id2 + "'")
        fetchedid=mycursor.fetchone()
        # fid=' '.join(map(str, fetchedid))
        # fid = ''.join(str(e) for e in fetchedid)
        feid = ' '.join(map(str, fetchedid))
        if(feid == id):
            msg="Congratulations "
            mycursor.execute("select email from `registered` where id='" + id2 + "'")
            e=mycursor.fetchone()
            email=' '.join(map(str, e))
            return render_template('crush.html',msg=(msg+" "+email))
        elif(feid != id):
            msg="Sorry!"
            return render_template('crush.html',msg=msg)
        else:
            # if (fetchedid is None):
            msg = "Not available"
            return render_template('crush.html', msg=msg)
    mydb.commit()
    mycursor.close()
    return render_template('crush.html')



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
        #     return render_template('match.html',msg=msg)
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
            mycursor.execute("select id,name,email from `registered` where id='" + str(idd2) + "'")
            e = mycursor.fetchall()
            iid=e[0][0]
            nm=e[0][1]
            em=e[0][2]
            name=str(nm)
            email = str(em)
            enroll = str(iid)
            mycursor.execute("select about from `match` where id = '" + str(idd2) + "'")
            a=mycursor.fetchone()
            abt=a[0]
            abtt=str(abt)
            # return render_template("match.html", msg=(msg+"Email: "+email+"About: "+abtt))
            return render_template('match.html',msg=msg,name=("You can contact "+name+ " at "),email=email)
    mydb.commit()
    mycursor.close()
    return render_template('match.html')



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    mg=''
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('mail')
        msg = request.form.get('msg')
        entry = Contacts(name=name, email=email, msg=msg, date= datetime.now())
        mg='message sent'
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',msg=mg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


app.secret_key = 'some secret key'
app.run(debug=True)

