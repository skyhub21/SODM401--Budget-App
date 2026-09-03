from flask import Blueprint, render_template, session, flash, redirect, url_for, request, current_app, jsonify
from datetime import datetime
from models import db, User
import random
import re

account_bp = Blueprint('account_bp', __name__, url_prefix='/account')

@account_bp.route('/login')
def login_page():
    """Render the login page"""
    current_year = datetime.now().year
    return render_template('login.html', 
                         logged_in='user_id' in session, 
                         current_year=current_year)

@account_bp.route('/microsoft-login')
def microsoft_login():
    """Redirect to Microsoft OAuth login"""
    # Get oauth from current app
    oauth = current_app.extensions.get('authlib.integrations.flask_client')
    
    if not oauth:
        flash('Authentication service is not configured properly.', 'error')
        return redirect(url_for('main.index'))
    
    # Redirect to Microsoft login for students
    redirect_uri = url_for('account_bp.auth_callback', _external=True, _scheme='https')
    return oauth.microsoft.authorize_redirect(redirect_uri)

@account_bp.route('/callback')
def auth_callback():
    """Handle OAuth callback from Microsoft"""
    try:
        print("1 - Getting token")
        oauth = current_app.extensions.get('authlib.integrations.flask_client')
        
        token = oauth.microsoft.authorize_access_token()
        
        print("2 - Getting user from Microsoft Graph")
        resp = oauth.microsoft.get('https://graph.microsoft.com/v1.0/me')
        user_info = resp.json()

        print(f"User Info: {user_info}")

        email = (
            user_info.get("mail") or
            user_info.get("userPrincipalName")
        )

        first_name = user_info.get("givenName", "")
        last_name = user_info.get("surname", "")
        microsoft_id = user_info.get("id")

        # Allowed DUT domains
        allowed_domains = ("@dut4life.ac.za", "@dut.ac.za")

        # Restrict to DUT emails
        if not email or not email.lower().endswith(allowed_domains):
            flash("Please login using your DUT email (@dut4life.ac.za or @dut.ac.za).", 'error')
            return redirect(url_for('main.index'))

        # Check if user exists
        user = User.query.filter_by(Email=email.lower()).first()

        if user:
            # Existing user - update last login
            user.LastLogin = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session["user_id"] = user.UserId
            session["user_email"] = user.Email
            session["user_name"] = f"{user.FirstName} {user.LastName}"
            session["user_role"] = getattr(user, 'UserRole', 'Student')
            
            flash(f"Welcome back, {user.FirstName}!", 'success')
            return redirect(url_for('account_bp.dashboard'))
        else:
            # New user - store info in session and redirect to registration
            temp_user_id = f"TEMP{datetime.utcnow().strftime('%y%m%d%H%M%S')}{random.randint(100,999)}"
            
            # Store user info in session for registration
            session["pending_user"] = {
                "temp_id": temp_user_id,
                "microsoft_id": microsoft_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email.lower(),
                "user_role": "Student"
            }
            
            flash("Please complete your profile registration to continue.", 'info')
            return redirect(url_for('account_bp.register'))

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        flash(f"Login failed: {str(e)}", 'error')
        return redirect(url_for('main.index'))




@account_bp.route('/register')
def register():
    """Render registration page for new users"""
    # Check if pending user data exists
    pending_user = session.get("pending_user")
    
    if not pending_user:
        flash("Please sign in first to complete your registration.", 'error')
        return redirect(url_for('main.index'))
    
    # Check if user already exists (in case of duplicate registration attempt)
    existing_user = User.query.filter_by(Email=pending_user.get('email')).first()
    if existing_user:
        # Clear pending user data
        session.pop("pending_user", None)
        # Set session for existing user
        session["user_id"] = existing_user.UserId
        session["user_email"] = existing_user.Email
        session["user_name"] = f"{existing_user.FirstName} {existing_user.LastName}"
        session["user_role"] = getattr(existing_user, 'UserRole', 'Student')
        flash("Your account is already active. Welcome back!", 'success')
        return redirect(url_for('account_bp.dashboard'))
    
    return render_template('profile/register.html', 
                         user=pending_user,
                         logged_in=False)




@account_bp.route('/register/submit', methods=['POST'])
def submit_registration():
    """Process registration form submission"""
    pending_user = session.get("pending_user")
    
    if not pending_user:
        return jsonify({
            'success': False, 
            'message': 'Session expired. Please sign in again.'
        }), 401
    
    # Get form data
    residential_address = request.form.get('residential_address', '').strip()
    cellphone_number = request.form.get('cellphone_number', '').strip()
    terms_accepted = request.form.get('terms_accepted')
    
    # Validate required fields
    if not residential_address:
        return jsonify({
            'success': False, 
            'message': 'Residential address is required.'
        }), 400
    
    if len(residential_address) < 5:
        return jsonify({
            'success': False, 
            'message': 'Please enter a valid residential address (minimum 5 characters).'
        }), 400
    
    # Validate phone number if provided
    if cellphone_number:
        # Remove spaces, dashes, parentheses, plus signs
        cleaned_phone = re.sub(r'[\s\-+()]', '', cellphone_number)
        if not cleaned_phone.isdigit() or len(cleaned_phone) < 10:
            return jsonify({
                'success': False, 
                'message': 'Please enter a valid phone number (minimum 10 digits).'
            }), 400
    
    if not terms_accepted:
        return jsonify({
            'success': False, 
            'message': 'You must accept the Terms and Conditions to register.'
        }), 400
    
    try:
        # Check if user already exists (race condition check)
        existing_user = User.query.filter_by(Email=pending_user["email"]).first()
        if existing_user:
            session.pop("pending_user", None)
            session["user_id"] = existing_user.UserId
            session["user_email"] = existing_user.Email
            session["user_name"] = f"{existing_user.FirstName} {existing_user.LastName}"
            return jsonify({
                'success': True,
                'redirect': url_for('account_bp.dashboard'),
                'message': 'Your account is already active. Redirecting...'
            })
        
        # Create new user
        new_user = User(
            UserId=pending_user["temp_id"],
            FirstName=pending_user["first_name"],
            LastName=pending_user["last_name"],
            Email=pending_user["email"],
            MicrosoftId=pending_user["microsoft_id"],
            ResidentialAddress=residential_address,
            CellphoneNumber=cellphone_number if cellphone_number else None,
            CreatedOn=datetime.utcnow(),
            LastLogin=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Set session for the new user
        session["user_id"] = new_user.UserId
        session["user_email"] = new_user.Email
        session["user_name"] = f"{new_user.FirstName} {new_user.LastName}"
        session["user_role"] = "Student"
        
        # Clear pending user from session
        session.pop("pending_user", None)
        
        return jsonify({
            'success': True,
            'redirect': url_for('account_bp.dashboard'),
            'message': f'Welcome to SmartShopper, {new_user.FirstName}! Your account has been activated.'
        })
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Registration failed: {str(e)}'
        }), 500




@account_bp.route('/dashboard')
def dashboard():
    """User dashboard (placeholder)"""
    if 'user_id' not in session:
        flash("Please sign in to access your dashboard.", 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(UserId=session.get('user_id')).first()
    if not user:
        session.clear()
        flash("Your account could not be found. Please sign in again.", 'error')
        return redirect(url_for('main.index'))
    
    return render_template('dashboard.html',
                         user_name=session.get('user_name', 'User'),
                         user_email=session.get('user_email', ''),
                         logged_in=True)











@account_bp.route('/terms')
def terms():
    """Terms and conditions page"""
    return render_template('terms.html')

@account_bp.route('/check-session')
def check_session():
    """Check if user has a valid session (for AJAX calls)"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name')
        })
    return jsonify({
        'authenticated': False
    })

@account_bp.route('/resend-verification')
def resend_verification():
    """Resend verification email (placeholder for future)"""
    flash('Verification email has been sent to your DUT4Life address.', 'info')
    return redirect(url_for('account_bp.register'))











@account_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash("You have been logged out successfully.", 'info')
    return redirect(url_for('main.index'))
