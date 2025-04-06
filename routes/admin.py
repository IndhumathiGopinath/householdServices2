from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, Service, Professional, Customer, ServiceRequest, Review
from forms import ServiceForm
from functools import wraps
from sqlalchemy import desc

admin_bp = Blueprint('admin', __name__)

# Admin access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Count statistics for dashboard
    total_services = Service.query.count()
    total_professionals = Professional.query.count()
    total_customers = Customer.query.count()
    total_requests = ServiceRequest.query.count()
    pending_requests = ServiceRequest.query.filter_by(status='pending').count()
    completed_requests = ServiceRequest.query.filter_by(status='completed').count()
    
    # Recent service requests
    recent_requests = ServiceRequest.query.order_by(desc(ServiceRequest.created_at)).limit(5).all()
    
    # Pending verifications
    pending_verifications = Professional.query.filter_by(is_verified=False).all()
    
    # Pending certificate verifications
    pending_certificate_verifications = Professional.query.filter(
        Professional.certificate_file.isnot(None),
        Professional.certificate_verified == False
    ).all()
    
    return render_template('admin/dashboard.html', 
                           total_services=total_services,
                           total_professionals=total_professionals,
                           total_customers=total_customers,
                           total_requests=total_requests,
                           pending_requests=pending_requests,
                           completed_requests=completed_requests,
                           recent_requests=recent_requests,
                           pending_verifications=pending_verifications,
                           pending_certificate_verifications=pending_certificate_verifications)

@admin_bp.route('/services')
@login_required
@admin_required
def services():
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@admin_bp.route('/service/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data,
            is_active=form.is_active.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/services.html', form=form, title='New Service')

@admin_bp.route('/service/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        service.is_active = form.is_active.data
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/services.html', form=form, title='Edit Service')

@admin_bp.route('/professionals')
@login_required
@admin_required
def professionals():
    professionals = Professional.query.all()
    return render_template('admin/professionals.html', professionals=professionals)

@admin_bp.route('/professional/verify/<int:professional_id>', methods=['POST'])
@login_required
@admin_required
def verify_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.is_verified = True
    db.session.commit()
    flash(f'Professional {professional.user.username} has been verified!', 'success')
    return redirect(url_for('admin.professionals'))

@admin_bp.route('/professional/view-certificate/<int:professional_id>')
@login_required
@admin_required
def view_certificate(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    if not professional.certificate_file:
        flash('This professional has not uploaded a certificate yet.', 'warning')
        return redirect(url_for('admin.professionals'))
    
    return render_template('admin/view_certificate.html', professional=professional)

@admin_bp.route('/professional/verify-certificate/<int:professional_id>', methods=['POST'])
@login_required
@admin_required
def verify_certificate(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.certificate_verified = True
    
    # Also set professional as verified since certificate is verified
    professional.is_verified = True
    
    db.session.commit()
    flash(f'Certificate for {professional.user.username} has been verified!', 'success')
    return redirect(url_for('admin.professionals'))

@admin_bp.route('/user/toggle-active/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}!', 'success')
    
    if user.role == 'professional':
        return redirect(url_for('admin.professionals'))
    else:
        return redirect(url_for('admin.customers'))

@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    customers = Customer.query.all()
    return render_template('admin/customers.html', customers=customers)

@admin_bp.route('/requests')
@login_required
@admin_required
def service_requests():
    requests = ServiceRequest.query.order_by(desc(ServiceRequest.created_at)).all()
    return render_template('admin/requests.html', requests=requests)
