# models.py
from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150))
    mobile = db.Column(db.String(20))
    profession = db.Column(db.String(100))
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(200))
    patient_name = db.Column(db.String(100))  # ✅ new
    age = db.Column(db.Integer)               # ✅ new

    knn_result = db.Column(db.String(50))
    knn_confidence = db.Column(db.Float)
    lstm_result = db.Column(db.String(50))
    lstm_confidence = db.Column(db.Float)
    cnn_result = db.Column(db.String(50))
    cnn_confidence = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
