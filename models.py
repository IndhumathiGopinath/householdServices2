from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'professional', 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    professional_profile = db.relationship('Professional', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer) # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    professionals = db.relationship('Professional', backref='service', lazy='dynamic')
    service_requests = db.relationship('ServiceRequest', backref='service', lazy='dynamic')
    
    def __repr__(self):
        return f'<Service {self.name}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    pin_code = db.Column(db.String(10))
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy='dynamic')
    reviews = db.relationship('Review', backref='customer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Customer {self.user.username}>'

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    description = db.Column(db.Text)
    experience = db.Column(db.Integer) # in years
    hourly_rate = db.Column(db.Float)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    pin_code = db.Column(db.String(10))
    certificate_file = db.Column(db.String(255))  # Path to the uploaded certificate file
    certificate_name = db.Column(db.String(100))  # Name of the certificate
    certificate_verified = db.Column(db.Boolean, default=False)  # Whether admin has verified the certificate
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy='dynamic')
    reviews = db.relationship('Review', backref='professional', lazy='dynamic')
    
    def __repr__(self):
        return f'<Professional {self.user.username}>'
    
    @property
    def avg_rating(self):
        reviews = Review.query.filter_by(professional_id=self.id).all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'assigned', 'accepted', 'rejected', 'completed', 'cancelled'
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    review = db.relationship('Review', backref='service_request', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ServiceRequest {self.id}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'
