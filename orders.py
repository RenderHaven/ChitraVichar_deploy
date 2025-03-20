import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import DatabaseError
from models import Order,OrderItems,db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/get_all', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@orders_bp.route('/get/<string:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify(order.to_dict())
    else:
        return jsonify({"error": "Order not found"}), 404


@orders_bp.route('/edit/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.json
        for key, value in data.items():
            setattr(order, key, value)
        db.session.commit()
        return jsonify(order.to_dict()), 200
    else:
        return jsonify({"error": "Order not found"}), 404

@orders_bp.route('/delete/<string:order_id>', methods=['DELETE'])
def delete_order(order_id):
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
            payINFO=order_data.get("payINFO")
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

