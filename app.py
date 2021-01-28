import uuid
import os

from flask import Flask
from flask import render_template, request, redirect, make_response, url_for

from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date

from database import db_session, init_db
from login import login_manager
from models import User, Topic, Post


app = Flask(__name__)
app.secret_key = "ssucuuh398nuwetubr33rcuhne"
login_manager.init_app(app)
init_db()


@app.teardown_appcontext
def shutdown_context(exception=None):
    db_session.remove()

@app.route('/', methods=['GET', 'POST'])
def homepage():
	if request.method == 'GET':
		topics = Topic.query.all()
		return render_template('homepage.html', topics=topics)
		
@app.route('/post/<topic_id>', methods=['GET', 'POST'])
def post(topic_id):
	if request.method == 'GET':
		return render_template('post.html')
	else:
		username = current_user.username
		title = request.form['title']
		description = request.form['information']
		time = datetime.now()
		
		post = Post(username=username, title=title, description=description,topic_id = topic_id, date=time)
		
		db_session.add(post)
		db_session.commit()
		return redirect('/topic/' + topic_id)
		
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
	delete = Post.query.filter_by(id = id).first()
	
	if current_user.username != delete.username:
		return redirect ("/topic/" + str(delete.topic_id))
	
	if request.method == 'POST':
		db_session.delete(delete)
		db_session.commit()
		return redirect ("/topic/" + str(delete.topic_id))
	return render_template("delete.html", post = delete)
		
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	change = Post.query.filter_by(id = id).first()
	if current_user.username != change.username:
		return render_template('edit.html', post = change)
		
	if request.method == 'POST':
		change.title = request.form['title']
		change.description = request.form['information']
		db_session.commit()
		return redirect("/topic/" + str(change.topic_id))
	return render_template("edit.html", post = change)
	
	
@app.route('/topic/<topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
	if request.method == 'GET':
		posts = Post.query.filter_by(topic_id=topic_id).order_by(Post.id)
		return render_template('topic.html', posts=posts, topic_id=topic_id)
	else:
		return redirect(url_for('post'))
		
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        user = User(username=username, password=password)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('login'))
        
@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
	if request.method == 'GET':
		return render_template('forum.html')
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['information']
		
		topic = Topic(title=title, description=description)
		
		db_session.add(topic)
		db_session.commit()
		return redirect(url_for('homepage'))
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    response = None
    if request.method == 'GET':
        return render_template('login.html')
    else:	
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
        	user.login_id = str(uuid.uuid4())
        	db_session.commit()
        	login_user(user)
    return redirect(url_for('homepage'))
       
@app.route("/logout")
@login_required
def logout():
    current_user.login_id = None
    db_session.commit()
    logout_user()
    return redirect(url_for('login'))
