import os
from flask import Flask
from flask_cors import CORS
from extensions import db
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Create Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173","https://mdd-frontendd.vercel.app/"])

# Absolute DB path
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Initialize db with app
db.init_app(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Delayed import of models BEFORE creating tables
from models import User, PredictionHistory, ContactMessage

# Register blueprints AFTER models
from auth import auth_bp
from predict import predict_bp
from history import history_bp
from contact import contact_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(contact_bp, url_prefix='/api/contact')

# Create tables ONLY AFTER everything is fully set up
with app.app_context():
    db.create_all()
    print("✔ Tables created in:", db_path)

#6. Start server
if __name__ == '__main__':
    print("🔥 Using DB:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True, port=5000)
