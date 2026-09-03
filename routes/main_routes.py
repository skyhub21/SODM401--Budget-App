from flask import Blueprint, render_template, session, request, jsonify
from datetime import datetime
from models import db, User
import re

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    # Check if user is logged in
    if 'user_id' in session:
        user_id = session.get('user_id')
        user = User.query.filter_by(UserId=user_id).first()
        
        if user:
            return render_template('index.html', 
                                 logged_in=True,
                                 user_name=f"{user.FirstName} {user.LastName}",
                                 current_year=datetime.now().year)
    
    return render_template('index.html', 
                         logged_in=False,
                         current_year=datetime.now().year)

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@main_bp.route('/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submissions"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    
    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address.'}), 400
    
    # Here you would typically send an email or save to database
    print(f"Contact Form Submission:\nName: {name}\nEmail: {email}\nMessage: {message}\n")
    
    return jsonify({'success': True, 'message': 'Thank you for your message. We\'ll get back to you soon.'})