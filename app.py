import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///household_services.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Upload folder configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database with the app
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Create database tables within application context
with app.app_context():
    # Import models here to ensure they're registered with SQLAlchemy
    import models
    db.create_all()

    # Initialize the admin account if it doesn't exist
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@household.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Admin user created")

# Import and register blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.customer import customer_bp
from routes.professional import professional_bp
from routes.service import service_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(professional_bp, url_prefix='/professional')
app.register_blueprint(service_bp, url_prefix='/service')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Route for the home page
@app.route('/')
def home():
    from flask import render_template
    return render_template('home.html')
