# utf-8 coding style /usr/bin
import os
from flask import Flask, url_for
from datetime import datetime
from flask import render_template
from flask import flash, session, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, UserMixin, LoginManager, current_user
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24).hex()
user_manager = LoginManager(app)
db = SQLAlchemy(app)
CKEditor(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Username %r>' % self.username


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.title


@user_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('log_page'))
    return render_template('main_reg.html')


@app.route('/main')
@login_required
def log_page():
    return render_template('main.html')


@app.route('/about')
@login_required
def about():
    return render_template('about.html')


@app.route('/blogs')
@login_required
def blogs():
    blog = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blogs.html', blog=blog)


@app.route('/posts/<int:id>/update', methods=["GET", "POST"])
@login_required
def blog_update(id):
    blog = Blog.query.get(id)
    if request.method == "POST":
        blog.title = request.form['title']
        blog.body = request.form['body']
        if blog.title and blog.body > str(0):
            db.session.commit()
            return redirect('/blogs')
        else:
            return redirect('/blogs')
    else:
        return render_template('blog_update.html', blog=blog)


@app.route('/write-blog', methods=["GET", "POST"])
@login_required
def write_blog():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']

        blog = Blog(title=title, body=body)
        if blog.title and blog.body > str(0):
            db.session.add(blog)
            db.session.commit()
            return redirect('/blogs')
        else:
            return "ошибка"
    else:
        return render_template('write-blog.html')


@app.route('/blogs/<int:id>')
@login_required
def my_blogs(id):
    blog = Blog.query.get(id)
    return render_template('my_blogs.html', blog=blog)


@app.route('/blogs/<int:id>/delete')
@login_required
def my_blog_delete(id):
    blog = Blog.query.get_or_404(id)
    try:
        db.session.delete(blog)
        db.session.commit()
        return redirect('/blogs')
    except:
        return "Ошибка при удалении статьи :/"


@app.route('/edit-blog/<int:id>')
@login_required
def edit_blog(id):
    return render_template('edit-blog.html', block_id=id)


@app.route('/delete-blog/<int:id>', methods=["POST"])
@login_required
def delete_blog(id):
    return "Successufully Deleted"


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Password don\'t match! Try again!')
            return render_template('register.html')
        else:

            password = generate_password_hash(password)
            user = User(first_name=first_name,
                        last_name=last_name,
                        username=username,
                        email=email,
                        password=password)
            flash('Registration successful! Please login!')
            db.session.add(user)
            db.session.commit()

            return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if login and password:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
                # flash('Welcome' + session['username'] + 'You have been successfully logged in!')
            else:
                flash('Please is incorret!')
                return render_template('login.html')
        else:
            flash('Please fill login and password fields')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
