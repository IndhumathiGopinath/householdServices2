from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Customer, Service, ServiceRequest, Professional, Review
from forms import CustomerProfileForm, ServiceRequestForm, ReviewForm
from functools import wraps
from sqlalchemy import desc
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)

# Customer access decorator
def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    # Check if customer has a profile
    if not current_user.customer_profile:
        return redirect(url_for('customer.create_profile'))
    
    # Get active requests
    active_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.customer_profile.id
    ).filter(
        ServiceRequest.status.in_(['pending', 'assigned', 'accepted'])
    ).order_by(desc(ServiceRequest.created_at)).all()
    
    # Get completed requests
    completed_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.customer_profile.id,
        status='completed'
    ).order_by(desc(ServiceRequest.created_at)).limit(5).all()
    
    return render_template('customer/dashboard.html', 
                           active_requests=active_requests,
                           completed_requests=completed_requests)

@customer_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
@customer_required
def create_profile():
    # Check if customer already has a profile
    if current_user.customer_profile:
        return redirect(url_for('customer.edit_profile'))
    
    form = CustomerProfileForm()
    if form.validate_on_submit():
        customer = Customer(
            user_id=current_user.id,
            address=form.address.data,
            phone=form.phone.data,
            pin_code=form.pin_code.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('Profile created successfully!', 'success')
        return redirect(url_for('customer.dashboard'))
    return render_template('customer/profile.html', form=form, title='Create Profile')

@customer_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@customer_required
def edit_profile():
    # Check if customer has a profile
    if not current_user.customer_profile:
        return redirect(url_for('customer.create_profile'))
    
    form = CustomerProfileForm(obj=current_user.customer_profile)
    if form.validate_on_submit():
        current_user.customer_profile.address = form.address.data
        current_user.customer_profile.phone = form.phone.data
        current_user.customer_profile.pin_code = form.pin_code.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer.dashboard'))
    return render_template('customer/profile.html', form=form, title='Edit Profile')

@customer_bp.route('/book-service', methods=['GET', 'POST'])
@login_required
@customer_required
def book_service():
    # Check if customer has a profile
    if not current_user.customer_profile:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('customer.create_profile'))
    
    form = ServiceRequestForm()
    # Populate service choices
    form.service_id.choices = [(s.id, s.name) for s in Service.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        service_request = ServiceRequest(
            customer_id=current_user.customer_profile.id,
            service_id=form.service_id.data,
            status='pending',
            scheduled_date=form.scheduled_date.data,
            scheduled_time=form.scheduled_time.data,
            address=form.address.data,
            pin_code=form.pin_code.data,
            description=form.description.data,
            price=Service.query.get(form.service_id.data).base_price
        )
        db.session.add(service_request)
        db.session.commit()
        
        # Log notification (previously an async task)
        logger.info(f"New service request created (ID: {service_request.id}). Professionals would be notified.")
        
        flash('Service request submitted successfully!', 'success')
        return redirect(url_for('customer.requests'))
    
    # Pre-fill address and pin_code from customer profile
    if request.method == 'GET':
        form.address.data = current_user.customer_profile.address
        form.pin_code.data = current_user.customer_profile.pin_code
    
    services = Service.query.filter_by(is_active=True).all()
    return render_template('customer/book_service.html', form=form, services=services)

@customer_bp.route('/requests')
@login_required
@customer_required
def requests():
    # Check if customer has a profile
    if not current_user.customer_profile:
        return redirect(url_for('customer.create_profile'))
    
    # Get all customer requests
    service_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.customer_profile.id
    ).order_by(desc(ServiceRequest.created_at)).all()
    
    return render_template('customer/requests.html', requests=service_requests)

@customer_bp.route('/request/<int:request_id>')
@login_required
@customer_required
def view_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current customer
    if service_request.customer_id != current_user.customer_profile.id:
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('customer.requests'))
    
    return render_template('customer/request_detail.html', request=service_request)

@customer_bp.route('/request/cancel/<int:request_id>', methods=['POST'])
@login_required
@customer_required
def cancel_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current customer
    if service_request.customer_id != current_user.customer_profile.id:
        flash('You do not have permission to cancel this request.', 'danger')
        return redirect(url_for('customer.requests'))
    
    # Check if the request can be cancelled
    if service_request.status in ['completed', 'cancelled']:
        flash('This request cannot be cancelled.', 'danger')
    else:
        service_request.status = 'cancelled'
        db.session.commit()
        flash('Service request cancelled successfully!', 'success')
    
    return redirect(url_for('customer.requests'))

@customer_bp.route('/request/complete/<int:request_id>', methods=['POST'])
@login_required
@customer_required
def complete_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current customer
    if service_request.customer_id != current_user.customer_profile.id:
        flash('You do not have permission to complete this request.', 'danger')
        return redirect(url_for('customer.requests'))
    
    # Check if the request can be completed
    if service_request.status != 'accepted':
        flash('This request cannot be marked as completed.', 'danger')
    else:
        service_request.status = 'completed'
        service_request.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service request completed successfully! Please leave a review.', 'success')
        return redirect(url_for('customer.review_service', request_id=request_id))
    
    return redirect(url_for('customer.requests'))

@customer_bp.route('/request/review/<int:request_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def review_service(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current customer
    if service_request.customer_id != current_user.customer_profile.id:
        flash('You do not have permission to review this service.', 'danger')
        return redirect(url_for('customer.requests'))
    
    # Check if the request is completed and not yet reviewed
    if service_request.status != 'completed':
        flash('Only completed services can be reviewed.', 'warning')
        return redirect(url_for('customer.requests'))
    
    # Check if a review already exists
    if service_request.review:
        flash('You have already reviewed this service.', 'info')
        return redirect(url_for('customer.requests'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            service_request_id=service_request.id,
            customer_id=current_user.customer_profile.id,
            professional_id=service_request.professional_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('customer.requests'))
    
    return render_template('customer/review.html', form=form, request=service_request)

@customer_bp.route('/services')
@login_required
@customer_required
def browse_services():
    services = Service.query.filter_by(is_active=True).all()
    return render_template('customer/services.html', services=services)

@customer_bp.route('/service/<int:service_id>')
@login_required
@customer_required
def view_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    # Get top-rated professionals for this service
    professionals = Professional.query.filter_by(
        service_id=service.id,
        is_verified=True
    ).all()
    
    # Sort by avg_rating
    professionals.sort(key=lambda p: p.avg_rating, reverse=True)
    
    return render_template('customer/service_detail.html', service=service, professionals=professionals)
