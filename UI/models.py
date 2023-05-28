from app_config import db, login_manager
import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
  user_id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(120),nullable=False,unique=False)
  last_name = db.Column(db.String(120),nullable=False,unique=False)
  email = db.Column(db.String(255),nullable=False,unique=True)
  password = db.Column(db.String(120),nullable=False)
  created_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
  patient = db.relationship('Patients',cascade="all,delete",backref='user_id', lazy=True)

  def get_id(self):
      return (self.user_id)

class Patients(db.Model):
  patient_id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(120),nullable=False,unique=False)
  last_name = db.Column(db.String(120),nullable=False,unique=False)
  sex = db.Column(db.String(120), nullable=False,unique=False)
  date_of_birth = db.Column(db.Date, nullable=False,unique=False)
  address = db.Column(db.String(255), nullable=False,unique=False)
  email = db.Column(db.String(255),nullable=False,unique=True)
  phone_number = db.Column(db.String(120),nullable=False,unique=True)
  id_user = db.Column(db.Integer, db.ForeignKey('users.user_id'))

class Tests(db.Model):
  test_id = db.Column(db.Integer, primary_key=True)
  pregnancies = db.Column(db.Integer,nullable=False,unique=False)
  glucose = db.Column(DOUBLE_PRECISION,nullable=False,unique=False)
  bmi = db.Column(DOUBLE_PRECISION,nullable=False,unique=False)
  age = db.Column(db.Integer,nullable=False,unique=False)
  date = db.Column(db.DateTime,nullable=False,unique=False, default=datetime.datetime.now())
  patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
  outcome = db.Column(db.String, nullable=False,unique=False)

# class Prediction(db.model):
#   pred_id = db.Column(db.Integer, primary_key=True)
#   outcome = db.Column(db.Double,nullable=False,unique=False)
#   patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
#   test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'))
#   date = db.Column(db.DateTime,nullable=False,unique=False)