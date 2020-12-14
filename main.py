from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
import pymysql
import os
from werkzeug.utils import secure_filename
# from flask_login import logout_user

pymysql.install_as_MySQLdb()


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = "Secret-Key"
UPLOAD_FOLDER = params['upload_location']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    serial_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(6), nullable=True)


class Posts(db.Model):
    # serial_number, title, subtitle, slug, content, image, date, blogger name
    serial_number = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=False, nullable=False)
    subtitle = db.Column(db.String(40), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    img_file = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(6), nullable=True)
    blogger_name = db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['post_num']]
    return render_template('index.html', params=params, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    session = {}
    if request.method == 'POST':

        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    #     redirect to admin signin panel
    else:
        return render_template('signin.html', params=params)


@app.route("/edit/<string:serial_number>", methods=['GET', 'POST'])
def edit(serial_number):
    session = {}
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            image = request.form.get('img_file')
            date = datetime.now()

            if serial_number == '0':
                post = Posts(serial_number=serial_number, title=title,
                             subtitle=tagline, slug=slug, content=content,
                             img_file=image, date=date)
                db.session.add(post)
                db.session.commit()
        # return render_template('edit.html', params=params)
            else:
                post = Posts.query.filter_by(serial_number=serial_number).first()
                post.title = title
                post.subtitle = tagline
                post.slug = slug
                post.content = content
                post.img_file = image
                post.date = date
                db.session.commit()
                return redirect('/edit/' + serial_number)
    # The post is not getting editted.
    post = Posts.query.filter_by(serial_number=serial_number).first()
    db.session.commit()
    return render_template('edit.html', params=params, post=post)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    session = {}
    if 'user' in session and session['user'] == params['admin_user']:
        f = request.files('file1')
        if f.filename == '':
            return "No selected file"

        if request.method == 'POST':
            f.save(os.path.join(app.config('UPLOAD_FOLDER'), secure_filename(f.filename)))
    return "Successfully uploaded  the file"


@app.route("/logout")
def logout():
    session = {}
    if 'user' in session and session['user'] == params['admin_user']:
        session.pop('user', None)
        # logout_user()
        return redirect('/dashboard.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )
    return render_template('contact.html', params=params)


app.run(debug=True)



























