from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename


with open('config.json', 'r') as c:
    parameters = json.load(c)['params']

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/timeragency'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = "static/uploaded"


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=parameters['gmail_username'],
    MAIL_PASSWORD=parameters['gmail_pass']
)
mail = Mail(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(12), nullable=False)
    subject = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(11), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(12), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    img_file = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(11), nullable=False)


@app.route('/')
def home():
    return render_template('index.html', parameters=parameters)


@app.route('/about')
def about():
    return render_template('about.html', parameters=parameters)


@app.route('/service')
def service():
    return render_template('service.html', parameters=parameters)


@app.route('/404')
def page404():
    return render_template('404.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def signin():
    if 'user' in session and session['user'] == parameters['username']:
        posts = Posts.query.all()
        return render_template('dashboard.html', posts=posts, parameters=parameters)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == parameters['username'] and password == parameters['password']:
            session['user'] = username
            posts = Posts.query.filter_by().all()
            return render_template("dashboard.html", parameters=parameters, posts=posts)

    return render_template('signin.html')


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == parameters['username']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            role = request.form.get('role')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno == '0':
                post = Posts(title=box_title, role=role, slug=slug,
                             content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.role = role
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', post=post, sno=sno)
    return redirect('/dashboard')


@app.route('/site-editor', methods=['GET', 'POST'])
def site_editor():
    if 'user' in session and session['user'] == parameters['username']:
        if request.method == 'POST':
            site_name = request.form.get('site-title')
            about_text = request.form.get('about-text')
            service_text = request.form.get('service-text')
            username = request.form.get('username')
            password = request.form.get('password')
            gmail_username = request.form.get('gmail-user')
            gmail_pass = request.form.get('gmail-pass')
            fb_link = request.form.get('fb-link')
            twitter_link = request.form.get('twitter-link')
            linkedin_link = request.form.get('linkedin-link')
            gmail_link = request.form.get('gmail-link')
            # dictionary for managing parameters
            parameters_to_be_passed = {
                'site_name': site_name,
                'about_text': about_text,
                'service_text': service_text,
                'username': username,
                'password': password,
                'gmail_username': gmail_username,
                'gmail_pass': gmail_pass,
                'fb_link': fb_link,
                'twitter_link': twitter_link,
                'linkedin_link': linkedin_link,
                'gmail_link': gmail_link
            }
            length = len(parameters_to_be_passed)
            with open('config.json', 'w') as f:
                f.write('{\n\t\"params\":{\n')
                for key, value in parameters_to_be_passed.items():
                    if length == 1:
                        f.write(f"\t\t\"{key}\":\"{value}\"\n")
                        continue
                    else:
                        f.write(f"\t\t\"{key}\":\"{value}\",\n")
                        length -= 1
                        continue
                f.write('\t}\n}')
                return redirect('/site-editor')
        else:
            return render_template('site-editor.html', parameters=parameters)
    else:
        return redirect('/dashboard')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == parameters['username']:
        if request.method == "POST":
            f = request.files['file1']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"


@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user'] == parameters['username']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/single-post/<string:post_slug>')
def single_post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('single-post.html', post=post)


@app.route('/single-portfolio')
def singleportfolio():
    return render_template('single-portfolio.html')


@app.route('/blog-fullwidth')
def blog_fullwidth():
    posts = Posts.query.filter_by().all()
    return render_template('blog-fullwidth.html', posts=posts)


@app.route('/blog-left-sidebar')
def blog_left_sidebar():
    return render_template('blog-left-sidebar.html')


@app.route('/blog-right-sidebar')
def blog_right_sidebar():
    return render_template('blog-right-sidebar.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        msg = request.form.get('message')
        date = datetime.now()
        contacts = Contact(name=name, email=email, subject=subject, msg=msg, date=date)
        db.session.add(contacts)
        db.session.commit()

        mail_msg = Message(subject=subject, sender=email, recipients=[parameters['gmail_username']],
                           body=f"Name:\t{name}\n\nEmail:\t{email}\n\nMessage:\t{msg}")
        mail.send(mail_msg)

    return render_template('contact.html')


app.run(debug=True, host='localhost')
