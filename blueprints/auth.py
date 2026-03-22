from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from utils.email_utils import send_verification_email
from utils.security_utils import validate_password_strength, validate_email
from config import ALLOWED_COUNTRIES, ALLOWED_MAJORS, DEVELOPMENT_MODE

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')
        nationality = request.form.get('nationality', '')
        gender = request.form.get('gender', '')
        status = request.form.get('status', '')
        major = request.form.get('major', '')
        
        # Basic validation
        errors = []
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not gender:
            errors.append('Please select your gender.')
        
        if not status:
            errors.append('Please select your status.')
        
        # Create user object and validate
        user = User(
            email=email,
            password=password,
            name=name,
            role=role,
            nationality=nationality,
            gender=gender,
            status=status,
            major=major if role == 'teacher' else None
        )
        
        validation_errors = user.validate()
        errors.extend(validation_errors)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html', 
                                 allowed_countries=ALLOWED_COUNTRIES,
                                 allowed_majors=ALLOWED_MAJORS)
        
        # Generate verification token
        user.generate_verify_token()
        
        # Save user to database
        if user.save():
            # Send verification email
            if send_verification_email(user):
                if DEVELOPMENT_MODE:
                    flash('Account created successfully! In development mode, verification emails are logged to console. You can now sign in.', 'success')
                else:
                    flash('Account created! Please check your email to verify your account before signing in.', 'success')
            else:
                if DEVELOPMENT_MODE:
                    flash('Account created successfully! Email verification is disabled in development mode. You can now sign in.', 'warning')
                else:
                    flash('Account created but verification email could not be sent. Please contact support.', 'warning')
            return redirect(url_for('auth.signin'))
        else:
            flash('An error occurred while creating your account. Please try again.', 'error')
    
    return render_template('signup.html', 
                         allowed_countries=ALLOWED_COUNTRIES,
                         allowed_majors=ALLOWED_MAJORS)

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('signin.html')
        
        # Find user
        user = User.get_by_email(email)
        if not user:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('signin.html')
        
        # Check password
        if not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('signin.html')
        
        # Check if account is verified
        if not user.is_verified():
            if DEVELOPMENT_MODE:
                flash('Account not verified, but allowing sign-in in development mode.', 'warning')
            else:
                flash('Please verify your email before signing in. Check your inbox.', 'error')
                return render_template('signin.html')
        
        # Set session
        session['user_id'] = user.user_id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['user_role'] = user.role
        
        flash('Welcome back! You have successfully signed in.', 'success')
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    return render_template('signin.html')

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.get_by_verify_token(token)
    if user:
        if user.verify_account():
            flash('Your account has been verified! You can now sign in.', 'success')
        else:
            flash('An error occurred while verifying your account. Please try again.', 'error')
    else:
        flash('Invalid or expired verification link.', 'error')
    
    return redirect(url_for('auth.signin'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('welcome'))

