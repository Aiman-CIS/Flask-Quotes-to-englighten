from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json 
import os
from werkzeug.utils import secure_filename #secure_filename function is used to ensure that the filename is safe for use
import math

with open('config.json','r') as c: #reading the contents of a JSON file 
    Parameters=json.load(c) ["Parameters"]
local_server=True




app = Flask(__name__) #instance of a Flask application.
app.secret_key = 'super-secret-key'
app.config["upload_file"]=Parameters['upload_file_loc']#sets the path where uploaded files will be stored. 
app.config.update (
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=Parameters["Gmail_user"],
    MAIL_PASSWORD=Parameters["Gmail_password"]
 
)
mail=Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = Parameters["local_URI"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = Parameters["produ_URI"]

db = SQLAlchemy(app)
@app.route("/")

def home(): ##This line defines a function named home().
    posts = Posts.query.filter_by().all() #This line retrieves all the Posts
    last = math.ceil(len(posts)/int(Parameters['No_of_posts'])) # calculates the total number of pages required to display 
    page=request.args.get("page") # retrieve the value of the page parameter from the URL query string. return a string value
    if (not str(page).isnumeric()):#if page is not a number, it sets page to 1.
         page = 1
    page = int(page)
    posts = posts[(page-1)*int(Parameters['No_of_posts']):(page-1)*int(Parameters['No_of_posts'])+ int(Parameters['No_of_posts'])]
    if page==1:#current page is the first page,
        prev = "#"#button is disabled 
        next = "/?page="+ str(page+1)#"Next" button points to the second page.
    elif page==last:#current page is the last page
        prev = "/?page="+ str(page-1) #points to the previous page
        next = "#"#button is disabled
    else:
        prev = "/?page="+ str(page-1)#you cannot concatenate a string and an integer directly.thats why str(page-1)
        next = "/?page="+ str(page+1)
    return render_template('index.html', Parameters=Parameters, posts=posts,prev=prev,next=next)#The render_template() function uses the Jinja2 templating engine to substitute the variables into the HTML template




@app.route("/about")
def about():
    return render_template('about.html',Parameters=Parameters)



class Contacts(db.Model):#Contacts class to interact with the contacts table in the database 
    ''' sno,name,email,phone_num,mesg,date'''
    sno = db.Column(db.Integer, primary_key=True) #db.Column class is used to specify the data type and other attributes of the column
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    mesg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phonenum = request.form.get('phonenum')
        message = request.form.get('message')
        if not name:
            return render_template('contact.html', error='Name field is required')
        entry = Contacts(name=name, phone_num=phonenum, mesg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit() #commit the changes made to the database
        mail.send_message("New update from "+ name,sender=email,recipients=[Parameters["Gmail_user"]],body=message+"\n"+phonenum)#ends an email notification to the admin

    return render_template('contact.html',Parameters=Parameters)



class Posts(db.Model):
    ''' sno,title,slug,content,date,imgfile,tagline'''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    imgfile = db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)


@app.route("/post/<string:post_slug>",methods=['GET'])#<string:post_slug> is a dynamic part of the URL, and it is used to indicate that the route should match any string value in the place of post_slug

def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
   

    return render_template('post.html',Parameters=Parameters,post=post)



@app.route("/dashboard",methods=['GET', 'POST'])
def dashboard():
    if ("useremail" in session and session['useremail']==Parameters['admin_login']):#"useremail" key is in the session dictionary and its value is the admin email
        posts = Posts.query.all()#retrieves all posts 
        
        return render_template("dashboard.html", Parameters=Parameters,posts=posts)
    if request.method == 'POST':
                useremail = request.form.get("useremail")
                userpass = request.form.get("password")
                if (useremail==Parameters['admin_login'] and userpass==Parameters['admin_pass']):
                      # set the session variable
                      session['useremail']=useremail #used to store the email of the logged-in user so that the server can recognize that the user is logged in 
                      posts = Posts.query.all()
                      
                      return render_template("dashboard.html", Parameters=Parameters,posts=posts)
        
    return render_template("login.html", Parameters=Parameters)



   
@app.route("/uploader", methods=['GET', 'POST'])

def uploader():
    if ("useremail" in session and session['useremail']==Parameters['admin_login']):
         if(request.method == 'POST'):
              f=request.files['file']#used to get the file object from the POST request 
              f.save(os.path.join(app.config ["upload_file"],secure_filename(f.filename))) #saves it to the server's designated upload directory
              #os.path.join function is used to concatenate the app.config["upload_file"] directory path with the filename of the uploaded file
              return " File Uploaded"
         

    return render_template('index.html',Parameters=Parameters)



@app.route("/edit/<string:sno>",methods=['GET','Post'])

def edit(sno):
    if ("useremail" in session and session['useremail']==Parameters['admin_login']):
         if request.method == 'POST':
              edit_title=request.form.get('title')
              edit_tagline=request.form.get('tagline')
              edit_slug=request.form.get('slug')
              edit_content=request.form.get('content')
              edit_imagefile=request.form.get('imgfile')
              date=datetime.now()
              ''' sno,title,slug,content,date,imgfile,tagline'''
              if sno=="0":
                   post=Posts(title=edit_title,slug=edit_slug,tagline=edit_tagline,imgfile=edit_imagefile,content=edit_content,date=date)
                   db.session.add(post)
                   db.session.commit()
                   return redirect('/edit/'+sno)
              else:  
                   post = Posts.query.filter_by(sno=sno).first()
                   post.title=edit_title
                   post.tagline=edit_tagline
                   post.slug=edit_slug
                   post.content=edit_content
                   post.imgfile=edit_imagefile
                   post.date=date
                   db.session.commit()
                   return redirect('/edit/'+sno)
         post = Posts.query.filter_by(sno=sno).first()
         return render_template('edit.html',Parameters=Parameters,post=post,sno=sno)





@app.route("/dlt/<string:sno>" , methods=['GET', 'POST'])
def dlt(sno):
       if ("useremail" in session and session['useremail']==Parameters['admin_login']):
          post = Posts.query.filter_by(sno=sno).first()
          db.session.delete(post)#delete post from the database 
          db.session.commit()
       return redirect("/dashboard")

    
@app.route('/logout')
def logout():
    session.pop('useremail')#session dictionary is modified to remove the 'useremail' key, which indicates that the user is no longer logged in.
    return redirect('/dashboard')
    



app.debug = True

app.run()

