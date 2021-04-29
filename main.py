from flask import Flask, render_template, redirect, url_for, request, flash, abort,
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, login_manager
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CafeForm, LogInForm, RegisterForm
from functools import wraps
from tkinter import messagebox

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

# connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Configure database for users:
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    user_name = db.Column(db.String(100))


# create database for cafes
class Cafes(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    location_link = db.Column(db.String(250), nullable=False)
    open_hours = db.Column(db.String(250))
    close_hours = db.Column(db.String(250))
    coffee_rating = db.Column(db.String(20))
    wifi_rating = db.Column(db.String(250))
    power_rating = db.Column(db.String(20))


db.create_all()


# Decorators to restrict access
# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user.id != 1:
#             return abort(403)
#         return f(*args, **kwargs)
#     return decorated_function
# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafes(
            name=form.cafe.data,
            location_link=form.location.data,
            open_hours=form.open.data,
            close_hours=form.close.data,
            coffee_rating=form.coffee.data,
            wifi_rating=form.wifi.data,
            power_rating=form.power.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    all_cafes = db.session.query(Cafes).all()
    return render_template('cafes.html', cafes=all_cafes)


@app.route('/delete')
# @admin_only
def delete():
    cafe_id = request.args.get('id')
    cafe_to_delete = Cafes.query.get(cafe_id)
    is_ok = messagebox.askokcancel(title=delete, message=f"Are you sure you want to delete this cafe?")
    if is_ok:
        db.session.delete(cafe_to_delete)
        db.session.commit()
    return redirect(url_for('cafes'))


@app.route('/login', methods=['GET', "POST"])
def login():
    # Login isnt working
    form = LogInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password is incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('cafes'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('cafes'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            user_name=form.user_name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("cafes"))

    return render_template("register.html", form=form, current_user=current_user)


if __name__ == '__main__':
    app.run(debug=False)
