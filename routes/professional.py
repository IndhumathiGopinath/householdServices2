from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models import Professional, Service, ServiceRequest
from forms import ProfessionalProfileForm
from functools import wraps
from sqlalchemy import desc
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

professional_bp = Blueprint('professional', __name__)

# Professional access decorator
def professional_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'professional':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@professional_bp.route('/dashboard')
@login_required
@professional_required
def dashboard():
    # Check if professional has a profile
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    # Check if professional is verified
    if not current_user.professional_profile.is_verified:
        flash('Your profile is pending verification by the admin.', 'info')
    
    # Get new assignment requests
    new_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.professional_profile.id,
        status='assigned'
    ).order_by(desc(ServiceRequest.created_at)).all()
    
    # Get accepted requests
    accepted_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.professional_profile.id,
        status='accepted'
    ).order_by(ServiceRequest.scheduled_date).all()
    
    # Get completed requests
    completed_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.professional_profile.id,
        status='completed'
    ).order_by(desc(ServiceRequest.updated_at)).limit(5).all()
    
    # Get reviews and calculate average rating
    reviews = current_user.professional_profile.reviews.all()
    avg_rating = current_user.professional_profile.avg_rating
    
    return render_template('professional/dashboard.html',
                           new_requests=new_requests,
                           accepted_requests=accepted_requests,
                           completed_requests=completed_requests,
                           reviews=reviews,
                           avg_rating=avg_rating)

def save_certificate(certificate_file):
    """Save the uploaded certificate and return the filename"""
    # Generate a unique filename to avoid conflicts
    filename = secure_filename(certificate_file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Save the file to the static/uploads/certificates folder
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'certificates')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    certificate_file.save(file_path)
    
    # Return the relative path for database storage (relative to static folder)
    return os.path.join('uploads', 'certificates', unique_filename)


@professional_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
@professional_required
def create_profile():
    # Check if professional already has a profile
    if current_user.professional_profile:
        return redirect(url_for('professional.edit_profile'))
    
    form = ProfessionalProfileForm()
    # Populate service choices
    form.service_id.choices = [(s.id, s.name) for s in Service.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Save the certificate file
        certificate_path = save_certificate(form.certificate_file.data)
        
        professional = Professional(
            user_id=current_user.id,
            service_id=form.service_id.data,
            description=form.description.data,
            experience=form.experience.data,
            hourly_rate=form.hourly_rate.data,
            address=form.address.data,
            phone=form.phone.data,
            pin_code=form.pin_code.data,
            certificate_name=form.certificate_name.data,
            certificate_file=certificate_path,
            certificate_verified=False
        )
        db.session.add(professional)
        db.session.commit()
        flash('Profile created successfully! Your certificate will be verified by the admin soon.', 'success')
        return redirect(url_for('professional.dashboard'))
    
    return render_template('professional/profile.html', form=form, title='Create Profile')

@professional_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@professional_required
def edit_profile():
    # Check if professional has a profile
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    form = ProfessionalProfileForm(obj=current_user.professional_profile)
    # Populate service choices
    form.service_id.choices = [(s.id, s.name) for s in Service.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Store the original service ID to check if it was changed
        original_service_id = current_user.professional_profile.service_id
        
        # Update the basic profile information
        current_user.professional_profile.service_id = form.service_id.data
        current_user.professional_profile.description = form.description.data
        current_user.professional_profile.experience = form.experience.data
        current_user.professional_profile.hourly_rate = form.hourly_rate.data
        current_user.professional_profile.address = form.address.data
        current_user.professional_profile.phone = form.phone.data
        current_user.professional_profile.pin_code = form.pin_code.data
        current_user.professional_profile.certificate_name = form.certificate_name.data
        
        # Handle certificate file upload
        has_certificate_upload = form.certificate_file.data and form.certificate_file.data.filename
        if has_certificate_upload:
            try:
                # Save the new certificate file
                certificate_path = save_certificate(form.certificate_file.data)
                
                # Remove the old certificate file if it exists
                if current_user.professional_profile.certificate_file:
                    old_file_path = os.path.join(
                        current_app.root_path, 'static', 
                        current_user.professional_profile.certificate_file
                    )
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except:
                            # Just log the error, don't fail if we can't remove old file
                            current_app.logger.warning(f"Could not remove old certificate file: {old_file_path}")
                
                # Update the certificate file path
                current_user.professional_profile.certificate_file = certificate_path
                
                # Reset certificate verification status when a new certificate is uploaded
                current_user.professional_profile.certificate_verified = False
                flash('Your certificate will need to be re-verified by the admin.', 'info')
            except Exception as e:
                current_app.logger.error(f"Error uploading certificate: {str(e)}")
                flash('There was an error uploading your certificate. Please try again.', 'danger')
                return render_template('professional/profile.html', form=form, title='Edit Profile')
        
        # Reset verification if service has changed
        if original_service_id != form.service_id.data:
            current_user.professional_profile.is_verified = False
            flash('Your profile will need to be re-verified by the admin as you changed your service type.', 'warning')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('professional.dashboard'))
    
    return render_template('professional/profile.html', form=form, title='Edit Profile')

@professional_bp.route('/requests')
@login_required
@professional_required
def requests():
    # Check if professional has a profile
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    # Get all requests for this professional
    assigned_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.professional_profile.id
    ).order_by(desc(ServiceRequest.created_at)).all()
    
    # Get potential requests matching the professional's service type
    potential_requests = ServiceRequest.query.filter_by(
        status='pending',
        service_id=current_user.professional_profile.service_id
    ).order_by(ServiceRequest.scheduled_date).all()
    
    return render_template('professional/requests.html', 
                          assigned_requests=assigned_requests,
                          potential_requests=potential_requests)

@professional_bp.route('/request/<int:request_id>')
@login_required
@professional_required
def view_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if either this is a pending request for this professional's service type
    # or it's already assigned to this professional
    is_valid_request = (
        (service_request.status == 'pending' and 
         service_request.service_id == current_user.professional_profile.service_id) or
        service_request.professional_id == current_user.professional_profile.id
    )
    
    if not is_valid_request:
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('professional.requests'))
    
    return render_template('professional/request_detail.html', request=service_request)

@professional_bp.route('/request/accept/<int:request_id>', methods=['POST'])
@login_required
@professional_required
def accept_request(request_id):
    # Check if professional has a profile and is verified
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    if not current_user.professional_profile.is_verified:
        flash('Your profile must be verified by the admin before accepting requests.', 'warning')
        return redirect(url_for('professional.requests'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if this is a valid request to accept
    if service_request.status == 'pending' and service_request.service_id == current_user.professional_profile.service_id:
        service_request.professional_id = current_user.professional_profile.id
        service_request.status = 'accepted'
        service_request.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service request accepted successfully!', 'success')
    elif service_request.status == 'assigned' and service_request.professional_id == current_user.professional_profile.id:
        service_request.status = 'accepted'
        service_request.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service request accepted successfully!', 'success')
    else:
        flash('Unable to accept this request.', 'danger')
    
    return redirect(url_for('professional.requests'))

@professional_bp.route('/request/reject/<int:request_id>', methods=['POST'])
@login_required
@professional_required
def reject_request(request_id):
    # Check if professional has a profile
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if this is an assigned request for this professional
    if service_request.status == 'assigned' and service_request.professional_id == current_user.professional_profile.id:
        service_request.professional_id = None
        service_request.status = 'pending'
        service_request.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service request has been rejected and returned to the pool.', 'info')
    else:
        flash('Unable to reject this request.', 'danger')
    
    return redirect(url_for('professional.requests'))

@professional_bp.route('/reviews')
@login_required
@professional_required
def reviews():
    # Check if professional has a profile
    if not current_user.professional_profile:
        return redirect(url_for('professional.create_profile'))
    
    # Get all reviews for this professional
    reviews = current_user.professional_profile.reviews.order_by(desc('created_at')).all()
    avg_rating = current_user.professional_profile.avg_rating
    
    return render_template('professional/reviews.html', 
                         reviews=reviews, 
                         avg_rating=avg_rating)
