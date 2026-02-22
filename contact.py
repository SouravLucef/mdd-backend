from flask import Blueprint, request, jsonify
from extensions import db

from models import ContactMessage

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/', methods=['POST'])
def submit_contact():
    data = request.get_json()
    print(data)
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'All fields are required'}), 400

    new_msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_msg)
    db.session.commit()
    print("Saving contact message:", name, email, message)


    return jsonify({'message': 'Your query has been submitted successfully'}), 201
