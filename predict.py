from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from extensions import db

from models import PredictionHistory
from utils import preprocess_eeg, extract_features
import joblib
from tensorflow.keras.models import load_model
import numpy as np
from utils import preprocess_eeg, extract_features, extract_eeg_plot_data, common_channels



predict_bp = Blueprint('predict', __name__)

# Load models
knn_model = joblib.load("./models/knn_model.pkl")
lstm_model = load_model("./models/lstm_model.h5",compile=False)
cnn_model = load_model("./models/cnn_model.h5",compile=False)
scaler = joblib.load("./models/scaler.pkl")

@predict_bp.route('/', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    name = request.form.get("name")
    age = request.form.get("age")


    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(filepath)

    try:
        epochs = preprocess_eeg(filepath)
        feats = extract_features(epochs)
        feats_scaled = scaler.transform(feats)
        feats_seq = feats_scaled[..., np.newaxis]

        eeg_plot_data, times_list = extract_eeg_plot_data(filepath, common_channels)



        # Predict
        knn_preds = knn_model.predict(feats_scaled)
        lstm_preds = lstm_model.predict(feats_seq)
        cnn_preds = cnn_model.predict(feats_seq)

        def summarize(preds):
            values, counts = np.unique(np.round(preds).astype(int), return_counts=True)
            label = int(values[np.argmax(counts)])
            confidence = float(np.max(counts) / len(preds))
            return "MDD" if label == 1 else "Healthy", confidence

        knn_result, knn_conf = summarize(knn_preds)
        lstm_result, lstm_conf = summarize(lstm_preds)
        cnn_result, cnn_conf = summarize(cnn_preds)

        # Save to DB
        history = PredictionHistory(
            user_id=session['user_id'],
            filename=filename,
            patient_name=name,       
            age=int(age),
            knn_result=knn_result, knn_confidence=knn_conf,
            lstm_result=lstm_result, lstm_confidence=lstm_conf,
            cnn_result=cnn_result, cnn_confidence=cnn_conf
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({
            "knn": {"result": knn_result, "confidence": knn_conf},
            "lstm": {"result": lstm_result, "confidence": lstm_conf},
            "cnn": {"result": cnn_result, "confidence": cnn_conf},
            "eeg_plot_data": eeg_plot_data,
            "times": times_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
