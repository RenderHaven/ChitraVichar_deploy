import hashlib
import uuid
from flask import Blueprint, json, request, jsonify,g
import requests
from sqlalchemy.exc import DatabaseError
from models import Order,OrderItems,db
import razorpay
import time

RAZORPAY_KEY_ID = "rzp_live_3HDGImYvtaYcya"
RAZORPAY_KEY_SECRET = "yyNAkeWME5Y7WS1s5Yuu3LeE"
RAZORPAY_BASE_URL = "https://api.razorpay.com/v1/payment_links"


orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/get_all', methods=['GET'])
def get_orders():
    if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
    orders = Order.query.all()
    return jsonify([order.to_small() for order in orders])

@orders_bp.route('/get/<string:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify(order.to_dict())
    else:
        return jsonify({"error": "Order not found"}), 404

    
@orders_bp.route('/update_status/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
    order = Order.query.get(order_id)
    if order:
        data = request.json
        status=data.get('status')
        if status:
            order.status=status
            db.session.commit()
        return jsonify(order.to_dict()), 200
    else:
        return jsonify({"error": "Order not found"}), 404
    


@orders_bp.route('/delete/<string:order_id>', methods=['DELETE'])
def delete_order(order_id):
    if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"}), 200
    else:
        return jsonify({"error": "Order not found"}), 404
    
@orders_bp.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.json
        # Extract order details
        order_data = data.get("order", {})
        items_data = data.get("items", [])
        if not order_data or not items_data:
            return jsonify({"error": "Invalid data"}), 400

        # Create Order
        new_order = Order(
            o_id=str(uuid.uuid4()),
            user_id=order_data.get("user_id"),
            total_price=order_data.get("total_price", 0.0),
            address=order_data.get("address"),
            short_note=order_data.get("short_note"),
            payINFO=order_data.get("payINFO",'NA')
        )
        db.session.add(new_order)
        # Create Order Items
        for item in items_data:
            order_item = OrderItems(
                order_id=new_order.o_id,
                i_id=item.get("i_id"),
                name=item.get("name"),
                image_url=item.get("image_url"),
                price=item.get("price", 0.0),
                original_price=item.get("original_price", 0.0),
                quantity=item.get("quantity", 1),
                other_details=item.get("other_details")
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"message": "Order created successfully", "order_id": new_order.o_id}), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@orders_bp.route('/create_payment_orderId', methods=['POST'])
def create_paymentId():
    try:
        data = request.json
        amount = int(float(data.get("amount", 0)) * 100)  # Convert INR to paise

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        payload = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,  # Auto-capture payment
        }

        headers = {"Content-Type": "application/json"}
        auth = (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)

        response = requests.post("https://api.razorpay.com/v1/orders", json=payload, auth=auth, headers=headers)
        res_data = response.json()

        if response.status_code in [200, 201]:
            return jsonify({"order_id": res_data["id"], "amount": res_data["amount"]}), 201
        else:
            return jsonify({"error": res_data}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@orders_bp.route('/verify_payment/<order_id>', methods=['GET'])
def verify_payment(order_id):
    try:
        print('Fetching payments for order:', order_id)
        auth = (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        response = requests.get(f"https://api.razorpay.com/v1/orders/{order_id}/payments", auth=auth)
        res_data = response.json()

        if response.status_code in [200, 201]:
            print("Razorpay API Response:", res_data)
            payment_captured = False
            if isinstance(res_data, dict) and 'items' in res_data:
                for payment in res_data['items']:
                    if payment['status'] == 'captured':
                        payment_captured = True
                        break
            elif isinstance(res_data, list):
                for payment in res_data:
                    if payment['status'] == 'captured':
                        payment_captured = True
                        break

            return str(payment_captured).lower(), 200 
        else:
            print("Razorpay API Error:", res_data)
            return jsonify(False), response.status_code

    except Exception as e:
        print("Exception during verification:", e)
        return jsonify({"error": str(e)}), 500