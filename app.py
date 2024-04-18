from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pickle
import os
from dotenv import load_dotenv


app = Flask(__name__, static_folder='static')
load_dotenv()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

DEFAULT_SESSION_DURATION = 3600  
EXTENDED_SESSION_DURATION = 604800 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

loaded_model = pickle.load(open('heart_disease_model.pkl', 'rb'))
loaded_scaler = pickle.load(open('heart_disease_scaler.pkl', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            print(session)
            return redirect(url_for('heart_disease_prediction'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/heart_disease_prediction')
@login_required
def heart_disease_prediction():
    if current_user.is_authenticated:
        return render_template('heart_disease_prediction.html')
    else:
        return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    age = request.form.get('age')
    sex = request.form.get('sex')
    cp = request.form.get('cp')
    trestbps = request.form.get('trestbps')
    chol = request.form.get('chol')
    fbs = request.form.get('fbs')
    restecg = request.form.get('restecg')
    thalach = request.form.get('thalach')
    exang = request.form.get('exang')
    oldpeak = request.form.get('oldpeak')

    try:
        age = int(age) if age else None
        sex = int(sex) if sex else None
        cp = int(cp) if cp else None
        trestbps = int(trestbps) if trestbps else None
        chol = int(chol) if chol else None
        fbs = int(fbs) if fbs else None
        restecg = int(restecg) if restecg else None
        thalach = int(thalach) if thalach else None
        exang = int(exang) if exang else None
        oldpeak = float(oldpeak) if oldpeak else None
    except ValueError:
         return render_template('error.html', error_message='Invalid value provided for one or more fields.'), 400

    if None in([age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak]):
        return render_template('error.html', error_message='Please fill out all required fields.'), 400
    
    input_data = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak]
    input_data_reshaped = np.asarray(input_data).reshape(1, -1)
    standardized_data = loaded_scaler.transform(input_data_reshaped)

    prediction = loaded_model.predict(standardized_data)

    if prediction[0] == 0:
        return render_template('negative.html')
    else:
        return render_template('positive.html')

if __name__ == '__main__':
    app.run(debug=True)