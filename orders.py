from flask import Blueprint, request, jsonify
from sqlalchemy.exc import DatabaseError
from models import Order,db

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

@orders_bp.route('/add', methods=['POST'])
def create_order():
    data = request.json
    try:
        order = Order(**data)
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except DatabaseError as err:
        db.session.rollback()
        print(err)
        return jsonify({"error": str(err)}), 400

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
    

