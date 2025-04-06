from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import User, Customer, Professional
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            next_page = request.args.get('next')
            
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'professional':
                if not user.professional_profile:
                    return redirect(url_for('professional.create_profile'))
                return redirect(next_page or url_for('professional.dashboard'))
            else:  # customer
                if not user.customer_profile:
                    return redirect(url_for('customer.create_profile'))
                return redirect(next_page or url_for('customer.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully for {form.username.data}. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))
