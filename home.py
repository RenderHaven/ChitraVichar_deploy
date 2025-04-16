
from flask import Blueprint, request
from flask import Blueprint,jsonify,g
from sqlalchemy import func,case,desc

from models import ImgItem,ProductItem,OrderItems,Order,db
from otp import Email

home_bp = Blueprint('home', __name__)
@home_bp.route('/get_home', methods=['GET'])
def get_banner():
    try:
        item=ProductItem.query.get('Lable')
        if not item:
            return jsonify({"error": "Banner Not Found"}), 404
        
        images =ImgItem.query.filter_by(item_id='Lable').all()

        banners=[img.image_url for img in images]

        return jsonify({
            'price':item.price,
            'banners': banners,
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@home_bp.route('/get_summery', methods=['GET'])
def get_summary():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401

        # --- User Orders Summary: Top 10 by total_orders ---
        user_results = db.session.query(
            Order.user_id,
            func.count(Order.o_id).label('total_orders'),
            func.sum(case((Order.status == 'DELIVERED', 1), else_=0)).label('completed')
        ).group_by(Order.user_id).order_by(desc(func.count(Order.o_id))).limit(10).all()

        user_data = {
            user_id: {
                "total_orders": total,
                "completed": completed
            }
            for user_id, total, completed in user_results
        }

        # --- Order Items Summary: Top 10 by quantity ---
        item_results = db.session.query(
            OrderItems.i_id,
            func.sum(OrderItems.quantity).label('totalOrders'),
            func.max(OrderItems.image_url).label('image_url'),
            func.max(OrderItems.name).label('name')
        ).group_by(OrderItems.i_id).order_by(desc(func.sum(OrderItems.quantity))).limit(10).all()

        item_data = {
            i_id: {
                "totalOrders": total,
                "image_url": image_url,
                "name": name
            }
            for i_id, total, image_url, name in item_results if i_id
        }

        # Final combined response
        return jsonify({
            "userData": user_data,
            "itemData": item_data
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    

@home_bp.route('/send_email', methods=['POST'])
def send_email_to_list():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        emails = data.get('emails')  # List of recipient emails
        subject = data.get('subject', 'No Subject')  # Optional
        body = data.get('message', '')  # Email content

        if not emails or not isinstance(emails, list) or not body:
            return jsonify({'message': 'Invalid request. "emails" (list) and "message" (string) are required.'}), 400

        try:
            Email.send_email(emails, subject, body)
            return jsonify({'message': 'Emails sent successfully.'}), 200
        except Exception as e:
            return jsonify({'message': f'Failed to send emails: {str(e)}'}), 500
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
