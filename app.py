from flask import Flask, render_template, request, flash, redirect, session
import pickle
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from functools import wraps
import json
import re


app = Flask(__name__)
app.secret_key = 'predictwell'

# Dummy user storage for demonstration purposes
users = {}

def predict(values, dic):
    if len(values) == 8:
        model = pickle.load(open('models/diabetes.pkl', 'rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 26:
        model = pickle.load(open('models/breast_cancer.pkl', 'rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 13:
        model = pickle.load(open('models/heart.pkl', 'rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 18:
        model = pickle.load(open('models/kidney.pkl', 'rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]
    elif len(values) == 10:
        model = pickle.load(open('models/liver.pkl', 'rb'))
        values = np.asarray(values)
        return model.predict(values.reshape(1, -1))[0]

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the user exists
        if email not in users:
            flash('Email not registered. Please sign up.')
        else:
            # Check if the password is correct
            if users[email]['password'] == password:
                session['logged_in'] = True
                session['user_email'] = email
                return redirect('/')
            else:
                flash('Incorrect password. Please try again.')

    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signupPage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Invalid email format. Please enter a valid email address.')
            return render_template('signup.html')

        # Validate password
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return render_template('signup.html')
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.')
            return render_template('signup.html')
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.')
            return render_template('signup.html')
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one digit.')
            return render_template('signup.html')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character.')
            return render_template('signup.html')

        # Check if the user already exists
        if email in users:
            flash('Email already registered. Please log in.')
        else:
            # Store user details
            users[email] = {'password': password}
            flash('Signup successful! You can now log in.')
            return redirect('/login')

    return render_template('signup.html')

@app.route("/logout")
def logoutPage():
    session.pop('logged_in', None)
    session.pop('user_email', None)
    return render_template('logout.html') 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route("/diabetes", methods=['GET', 'POST'])
@login_required
def diabetesPage():
    return render_template('diabetes.html')

@app.route("/heart", methods=['GET', 'POST'])
@login_required
def heartPage():
    return render_template('heart.html')

@app.route("/kidney", methods=['GET', 'POST'])
@login_required
def kidneyPage():
    return render_template('kidney.html')

@app.route("/predict", methods=['POST', 'GET'])
@login_required
def predictPage():
    pred = None
    try:
        if request.method == 'POST':
            to_predict_dict = request.form.to_dict()
            to_predict_list = list(map(float, list(to_predict_dict.values())))
            pred = predict(to_predict_list, to_predict_dict)
    except:
        message = "Please enter valid Data"

    return render_template('predict.html', pred=pred)

if __name__ == '__main__':
    app.run(debug=True)