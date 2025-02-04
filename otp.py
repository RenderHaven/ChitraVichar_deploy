import random
import requests
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models import db

# Blueprint for OTP routes
otp_bp = Blueprint('otp', __name__)

# Brevo (Sendinblue) Configuration
BREVO_API_KEY = "your_brevo_api_key"  # Replace with your actual API key
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact = db.Column(db.String(50), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MobileOTP:
    @staticmethod
    def send_otp(number):
        otp_code = f"{random.randint(100000, 999999)}"
        existing_otp = OTP.query.filter_by(contact=number).first()
        if existing_otp:
            db.session.delete(existing_otp)
        
        new_otp = OTP(contact=number, otp=otp_code)
        db.session.add(new_otp)
        db.session.commit()
        
        return otp_code
    
    @staticmethod
    def verify_otp(number, otp):
        record = OTP.query.filter_by(contact=number).first()
        if not record:
            return False, 'Invalid OTP or number.'
        if datetime.utcnow() > record.created_at + timedelta(minutes=5):
            db.session.delete(record)
            db.session.commit()
            return False, 'OTP expired. Please request a new one.'
        if record.otp != otp:
            return False, 'Invalid OTP.'
        
        db.session.delete(record)
        db.session.commit()
        return True, 'OTP verified successfully.'

class EmailOTP:
    @staticmethod
    def send_otp(email):
        otp_code = f"{random.randint(100000, 999999)}"
        existing_otp = OTP.query.filter_by(contact=email).first()
        if existing_otp:
            db.session.delete(existing_otp)
        
        new_otp = OTP(contact=email, otp=otp_code)
        db.session.add(new_otp)
        db.session.commit()
        
        payload = {
            "sender": {"name": "YourApp", "email": "no-reply@yourapp.com"},
            "to": [{"email": email}],
            "subject": "Your OTP Code",
            "htmlContent": f"<p>Your OTP code is <strong>{otp_code}</strong>. It expires in 5 minutes.</p>"
        }
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        response = requests.post(BREVO_URL, json=payload, headers=headers)
        
        if response.status_code != 201:
            raise Exception(response.text)
        
        return otp_code
    
    @staticmethod
    def verify_otp(email, otp):
        return MobileOTP.verify_otp(email, otp)

@otp_bp.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    contact = data.get('contact')
    contact_type = data.get('type')  # 'email' or 'mobile'
    
    if not contact or not contact_type:
        return jsonify({'message': 'Contact and type are required.'}), 400
    
    try:
        if contact_type == 'mobile':
            MobileOTP.send_otp(contact)
        elif contact_type == 'email':
            EmailOTP.send_otp(contact)
        else:
            return jsonify({'message': 'Invalid contact type.'}), 400
    except Exception as e:
        return jsonify({'message': f'Failed to send OTP: {str(e)}'}), 500
    
    return jsonify({'message': 'OTP sent successfully.'}), 200

@otp_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    contact = data.get('contact')
    otp = data.get('otp')
    contact_type = data.get('type')
    
    if not contact or not otp or not contact_type:
        return jsonify({'message': 'Contact, OTP, and type are required.'}), 400
    
    success, message = (MobileOTP.verify_otp(contact, otp) if contact_type == 'mobile' 
                        else EmailOTP.verify_otp(contact, otp))
    
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'message': message}), 400
