from flask import Flask, render_template, redirect, session, request, url_for, send_file
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import requests

# insantiating Flask class object in variable "app" 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/notes_possible_db'
db = SQLAlchemy(app)

class Userinfo(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    Id = db.Column(db.String(50), unique=True)
    #UserName = db.Column(db.String(30), unique=True)
    Name = db.Column(db.String(50), unique=False)
    #Email = db.Column(db.String(50), unique=True)
    ProfilePicture = db.Column(db.Text, unique=False)

class Documentrecord(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    Id = db.Column(db.String, unique=False)
    #UploaderUN = db.Column(db.String(), unique=False)
    DocumentName = db.Column(db.String(), unique=False)
    UploadDate = db.Column(db.String(), unique=False)
    Source = db.Column(db.String(), unique=False)
    StreamCourse = db.Column(db.String(), unique=False)
    Subject = db.Column(db.String(), unique=False)
    Year = db.Column(db.String(), unique=False)
    Semester = db.Column(db.String(), unique=False)
    Path = db.Column(db.String(), unique=False)
    Extension = db.Column(db.String(), unique=False)

class Relation(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    UNMentor = db.Column(db.String(), unique=True)
    UNMentee = db.Column(db.String(), unique=True)

class totalrelation(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(), unique=True)
    TotalMentor = db.Column(db.Integer)
    TotalMentee = db.Column(db.Integer)

app.secret_key = 'random secret'

#oauth config
oauth = OAuth(app)

folder = ""
filename = ""

@app.route('/')
def index():
    #email = dict(session).get('email', None)
    if session.get("id") is None:
        return render_template('index.html')
    else:
        fetch = Documentrecord.query.filter_by(Id=session['id']).all()
        return render_template('Home.html', data=fetch)
@app.route('/LoginSignUp')
def LoginSignUp():
    # return "Hello"

    if request.args.get("next"):
        session["next"] = request.args.get("next")
    return redirect(

        f"https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.googleapis.com/auth/userinfo.profile&access_type=offline&include_granted_scopes=true&response_type=code&redirect_uri=http://127.0.0.1:5000/authorize&client_id=891944377515-bg8r7phbmiolc8bb29jiqkf9rjnp4e4s.apps.googleusercontent.com")


@app.route('/authorize')
def authorize():

    r = requests.post("https://oauth2.googleapis.com/token", data = {
    "client_id" : '891944377515-bg8r7phbmiolc8bb29jiqkf9rjnp4e4s.apps.googleusercontent.com',
    "client_secret" : 'P9cqAQy9HuzoarRKuwQv3kiG',
    "code" : request.args.get("code"),
    "grant_type" : "authorization_code",
    "redirect_uri" : "http://127.0.0.1:5000/authorize",
    })
    access_token = r.json()['access_token']
    #print(access_token)
    r = requests.get(f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}")

    #connection = db.session.connection()
    print(r.json())

    result = Userinfo.query.filter_by(Id=r.json()['id']).all()
    resulttype = type(result)
    result = len(result)
    print(resulttype)
    print(result)
    def set_session():
        #session['username'] = (r.json()['email']).split('@')[0]
        session['id'] = r.json()['id']
        session['name'] = r.json()['name']
        #session['email'] = r.json()['email']
        session['profilepicture'] = r.json()['picture']
        return redirect(url_for('index'))

    if(result>=1):#result==1 waali condition use krna hai!
        return (set_session())
    else:
        #entry = Userinfo(UserName = (r.json()['email']).split('@')[0], Name = r.json()['name'], Email = r.json()['email'], ProfilePicture = r.json()['picture'])
        entry = Userinfo(Id = r.json()['id'], Name = r.json()['name'], ProfilePicture = r.json()['picture'])
        db.session.add(entry)
        db.session.commit()
        return (set_session())
        #return Userinfo.query.filter_by(Email='rohantelang10@gmail.com').all() #clean up
    #user_info = resp.json()
    # do something with the token and profile
    # session['email'] = user_info['email']
    #
    #
    # return redirect('/')
    #print("Response here")
    #print(resp.json())
    # return "Authorize me aa gaya"

@app.route('/documentupload', methods=['GET', 'POST'])
def documentupload():
    if not session.get("id") is None:
        if request.method == 'POST':
            Id = session['id']
            #UploaderUN = session['']
            DocumentName = request.form['DocumentName']
            Source = request.form['Source']
            StreamCourse = request.form['StreamCourse']
            Subject = request.form['Subject']
            Year = request.form['Year']
            Semester = request.form['Semester']
            #Path = request.form['UploadDocument']
            result = Documentrecord.query.all()
            if len(result)==0:
                Next_SNo = 1
            else:
                Next_SNo = (result[-1].SNo)+1
            f = request.files['UploadDocument']
            Path = str(Next_SNo)+'_'+secure_filename(f.filename)
            basedirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            app.config['UPLOAD_FOLDER'] = os.path.join(basedirectory,"NotesPosibleWebsite","uploads",session['id'])
            if not os.path.exists( app.config['UPLOAD_FOLDER'] ):
                os.makedirs( app.config['UPLOAD_FOLDER'] )

            if Path.split(".")[-1].lower() in ['doc', 'docx', 'txt', 'ppt', 'pptx', 'pdf']:
                Extension = Path.split(".")[-1]

                f.save(os.path.join(app.config['UPLOAD_FOLDER'], Path))
                #send_from_directory(app.config['UPLOADER_FOLDER'], Path)

                entry = Documentrecord(Id=Id, DocumentName=DocumentName, Source=Source, StreamCourse=StreamCourse, Subject=Subject, Year=Year, Semester=Semester, Path=Path, Extension=Extension)
                db.session.add(entry)
                db.session.commit()
                return redirect(url_for('documentupload'))
            else:
                return "Please upload one of this extension file 'doc', 'docx', 'txt', 'ppt', 'pptx', 'pdf'"
        return render_template("documentupload.html")
    else:
        return "Oops, something went wrong!"

@app.route('/docopener/<string:sno>')
def docopener(sno):
    fetch = Documentrecord.query.filter_by(SNo=sno).all()
    user = Userinfo.query.filter_by(Id=fetch[0].Id).all()

    docopener.folder = fetch[0].Id
    docopener.filename = fetch[0].Path


    return render_template('docOpener.html', doc_data=fetch, user=user, extension=((docopener.filename).split(".")[-1]).lower())

@app.route('/downloadfile/<string:file>')
def downloadfile(file):

    basedirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(basedirectory, "NotesPosibleWebsite", "uploads", docopener.folder, docopener.filename)
    return send_file(path, attachment_filename=''.join((docopener.filename).split("_")[1:]))

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == '__main__':
    app.debug = True
    app.run()