from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

from models import User
from flask import jsonify


auth_bp = Blueprint('auth', __name__)

#Signup
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    mobile = data.get('mobile')
    profession = data.get('profession')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    hashed_pw = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        mobile=mobile,
        profession=profession,
        password=hashed_pw,
        is_admin=False
    )
    db.session.add(new_user)
    db.session.commit()
    print(f"[DEBUG] Added user {username} to DB")


    return jsonify({'message': 'User created successfully'}), 201


@auth_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({'error': 'Admin access only'}), 403

    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "name": u.username,
            "email": u.email,
            "mobile": u.mobile,
            "profession": u.profession
        }
        for u in users
    ])

#Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful',
        'username': user.username,   }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

#Logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

#Check session
@auth_bp.route('/check', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({'loggedIn': True, 'username': session.get('username')}), 200
    else:
        return jsonify({'loggedIn': False}), 200
