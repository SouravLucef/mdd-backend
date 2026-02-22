from flask import Blueprint, jsonify, session
from extensions import db

from models import PredictionHistory

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    records = PredictionHistory.query.filter_by(user_id=session['user_id']).order_by(PredictionHistory.timestamp.desc()).all()

    return jsonify([
        {   "patient_name": r.patient_name,
            "age": r.age,
            "filename": r.filename,
            "knn": {"result": r.knn_result, "confidence": r.knn_confidence},
            "lstm": {"result": r.lstm_result, "confidence": r.lstm_confidence},
            "cnn": {"result": r.cnn_result, "confidence": r.cnn_confidence},
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for r in records
    ])
