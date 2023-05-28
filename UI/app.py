
import email
from re import S
from flask import render_template, flash, url_for, request, redirect, make_response
from flask_login import login_required, login_user, current_user, logout_user, login_required
from flask_mail import Message
from app_config import app, db, mail

from form import RegistrationForm
from models import Users, Patients, Tests
from passlib.hash import bcrypt
from sqlalchemy import func, extract, Date, cast
import json

import pickle
import pandas as pd
import os
from dotenv import load_dotenv 

diabetes_model, scaler = pickle.load(open("diabetes.pkl", "rb"))
load_dotenv()

from sklearn.linear_model import LogisticRegression

LogisticRegression()



#-------------------------------------------------------------------------------------------------------------------------------LOG IN---------


@app.route('/', methods=['POST','GET'])
@app.route('/login', methods=['POST','GET'])
def login():
   if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
   if request.method == 'POST':
        # Get Form Fields
      email = request.form['email']
      password_candidate = request.form['password']

      user=Users.query.filter_by(email=email).first()
      if user:

          passwordd=Users.query.filter_by(email=email).first()
          if bcrypt.verify(password_candidate, passwordd.password):
              login_user(user)
              return redirect(url_for('patients'))
          else:
              error = "Invalid Password"
              return render_template('Login.html', error=error)

      else:
          error = "Invalid email"
          return render_template('Login.html', error=error)    
   return render_template('Login.html') 


#-------------------------------------------------------------------------------------------------------------------------------LOG OUT---------


@app.route('/logout')
@login_required
def logout():
   logout_user()
   resp = make_response(redirect(url_for('login')))
   return resp
   #return render_template("Login.html")


#-------------------------------------------------------------------------------------------------------------------------------SIGN UP---------


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
  form = RegistrationForm(request.form)
  if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = bcrypt.hash(str(form.password.data))
        user = Users(first_name=first_name, last_name=last_name, email=email, password= password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered', 'success')
        return redirect(url_for('login'))
    
  return render_template('SignUp.html', form = form)

#----------------------------------------------------------------------------------------------------------------------------PATIENTS---------


@app.route('/patients', methods=['POST','GET'])
@login_required
def patients():
    # page = request.args.get('page', 1, type=int)
    patients = Patients.query.filter(Patients.id_user == current_user.get_id()).all()
    if request.method == 'POST':
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        sex = request.form.get('sex')
        date_of_birth = request.form.get('dateofbirth')
        address = request.form.get('homeaddress')
        email = request.form.get('email')
        phone_number = request.form.get('phonenumber')
        add = Patients(first_name = first_name, last_name = last_name, sex = sex, date_of_birth = date_of_birth, address = address, email = email, phone_number = phone_number, id_user = current_user.get_id())
        db.session.add(add)
        db.session.commit()
        return redirect(url_for('patients'))

    return render_template('Patients.html', patients = patients)

@app.route("/updatepatient/<int:patient_id>", methods=['POST','GET'])
@login_required
def update_product(patient_id):
    patient = Patients.query.get(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form.get('firstname')
        patient.last_name = request.form.get('lastname')
        patient.sex = request.form.get('sex')
        patient.date_of_birth = request.form.get('dateofbirth')
        patient.address = request.form.get('homeaddress')
        patient.email = request.form.get('email')
        patient.phone_number = request.form.get('phonenumber')
        db.session.commit()
        return redirect(url_for('patients'))

    return render_template('update_patient.html', patient = patient)

@app.route("/patient/delete/<int:patient_id>", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patients.query.get(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patients'))


#----------------------------------------------------------------------------------------------------------------------------TESTS---------

@app.route('/tests/<int:patient_id>', methods=['POST', 'GET'])
@login_required
def tests(patient_id):
    tests = Tests.query.filter(Tests.patient_id == patient_id).all()
    if request.method == 'POST':
        pregnancies = request.form.get('pregnancies')
        glucose = request.form.get('glucose')
        bmi = request.form.get('bmi')
        age = request.form.get('age')
        data = {'Pregnancies': [pregnancies], 'Glucose': [glucose],  'BMI': [bmi], 'Age': [age]}
        row = pd.DataFrame.from_dict(data)
        row = scaler.transform(row)
        print(row)
        prediction = diabetes_model.predict_proba(row)
        prediction2 = diabetes_model.predict(row)[0]
        outcome='{0:.{1}f}'.format(prediction[0][1], 2)
        outcomeFinal = str(int(prediction2)) +' (' + str(float(outcome)*100) + "%)"
        add = Tests(pregnancies = pregnancies, glucose = glucose, bmi = bmi, 
                     age = age,  patient_id = patient_id, outcome = outcomeFinal)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for('tests', patient_id = patient_id))

    return render_template('Tests.html', tests = tests)
  
@app.route("/tests/<int:patient_id>/delete/<int:test_id>", methods=['POST'])
@login_required
def delete_test(test_id, patient_id):
    test = Tests.query.get(test_id)
    db.session.delete(test)
    db.session.commit()
    return redirect(url_for('tests', patient_id = patient_id))

@app.route("/tests/<int:patient_id>/sendEmail/<int:test_id>", methods=['POST'])
@login_required
def send_email(test_id, patient_id):
    test = Tests.query.get(test_id)
    patient = Patients.query.get(patient_id)
    print(os.getenv('EMAIL'))
    msg = Message('Diabetes Tests', sender = os.getenv('EMAIL'),  recipients = [patient.email])
    msg.html =  render_template('Email.html', test = test, patient = patient)
    mail.send(msg)
    return redirect(url_for('tests', patient_id = patient_id))


#------------------------------------------------------------------------------------------------------------------------------DASHBOARD---------


@app.route('/dashboard/<int:patient_id>', methods=['POST', 'GET'])
@login_required
def dashboard(patient_id):

    tests = Tests.query.filter(Tests.patient_id == patient_id).all()
    glucose_ = []
    bmi_ = []
    date_ = []
    for test in tests:
        glucose_.append(test.glucose)
        bmi_.append(test.bmi)
        bmi_.append(test.bmi)
        date_.append(test.date)

        
    

    return render_template('Dashboard.html',
     glucose_ = json.dumps(glucose_),
     bmi_ = json.dumps(bmi_),
     date_ = json.dumps(date_, default=str))


#--------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":  # Makes sure this is the main process
	  app.run( # Starts the site
		host='127.0.0.1',  # Establishes the host, required for repl to detect the site
		port=5000  # Randomly select the port the machine hosts on.
	)
