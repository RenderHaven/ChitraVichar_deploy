from flask import Blueprint, request, jsonify
from models import CouponCode, UserCouponUsage,User,db
from sqlalchemy import and_
import uuid

coupon_bp = Blueprint("coupon", __name__, url_prefix="/coupon")

# Get all coupons
@coupon_bp.route("/get_all", methods=["GET"])
def get_all_coupons():
    coupons = CouponCode.query.all()
    return jsonify([
        {
            "id": coupon.id,
            "code": coupon.code,
            "discount_amount": str(coupon.discount_amount),
            "discount_type": coupon.discount_type,
            "max_uses": coupon.max_uses,
            "times_used": coupon.times_used,
            "min_order_amount": str(coupon.min_order_amount),
            "created_at": coupon.created_at
        }
        for coupon in coupons
    ]), 200

# Get a single coupon by ID
@coupon_bp.route("/get/<string:coupon_id>", methods=["GET"])
def get_coupon(coupon_id):
    coupon = CouponCode.query.get(coupon_id)
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404
    return jsonify({
        "id": coupon.id,
        "code": coupon.code,
        "discount_amount": str(coupon.discount_amount),
        "discount_type": coupon.discount_type,
        "max_uses": coupon.max_uses,
        "times_used": coupon.times_used,
        "min_order_amount": str(coupon.min_order_amount),
        "created_at": coupon.created_at
    }), 200

@coupon_bp.route("/get_by_code/<string:couponCode>/<string:userId>", methods=["GET"])
def get_coupon_by_code(couponCode, userId):
    coupon = CouponCode.query.filter_by(code=couponCode).first()
    
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404

    user_usage_count = UserCouponUsage.query.filter(
        and_(UserCouponUsage.coupon_code == couponCode, UserCouponUsage.user_id == userId)
    ).count()

    if user_usage_count >= coupon.max_uses:
        return jsonify({"error": "Limit Exceeded For U"}), 400

    return jsonify({
        "id": coupon.id,
        "code": coupon.code,
        "discount_amount": str(coupon.discount_amount),
        "discount_type": coupon.discount_type,
        "max_uses": coupon.max_uses,
        "times_used": coupon.times_used,
        "min_order_amount": str(coupon.min_order_amount),
        "created_at": coupon.created_at
    }), 200

# Add a new coupon
@coupon_bp.route("/add", methods=["POST"])
def add_coupon():
    try:
        data = request.json
        new_coupon = CouponCode(
            id=str(uuid.uuid4()),
            code=data["code"],
            discount_amount=data["discount_amount"],
            discount_type=data["discount_type"],
            max_uses=data.get("max_uses", 1),
            min_order_amount=data.get("min_order_amount", 0),
        )
        db.session.add(new_coupon)
        db.session.commit()
        return jsonify({"message": "Coupon added successfully!", "coupon": new_coupon.code}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Update a coupon
@coupon_bp.route("/update/<string:coupon_id>", methods=["PUT"])
def update_coupon(coupon_id):
    coupon = CouponCode.query.get(coupon_id)
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404

    try:
        data = request.json
        print(data)
        if "code" in data:
            coupon.code = data["code"]
        if "discount_amount" in data:
            coupon.discount_amount = data["discount_amount"]
        if "discount_type" in data:
            coupon.discount_type = data["discount_type"]
        if "max_uses" in data:
            coupon.max_uses = data["max_uses"]
        if "min_order_amount" in data:
            coupon.min_order_amount = data["min_order_amount"]

        db.session.commit()
        return jsonify({"message": "Coupon updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete a coupon
@coupon_bp.route("/delete/<string:coupon_id>", methods=["DELETE"])
def delete_coupon(coupon_id):
    coupon = CouponCode.query.get(coupon_id)
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404
    
    db.session.delete(coupon)
    db.session.commit()
    return jsonify({"message": "Coupon deleted successfully"}), 200

# Check if a coupon is valid
@coupon_bp.route("/check/<string:coupon_code>", methods=["GET"])
def check_coupon(coupon_code):
    coupon = CouponCode.query.filter_by(code=coupon_code).first()
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404

    if coupon.times_used >= coupon.max_uses:
        return jsonify({"error": "Coupon usage limit reached"}), 400

    return jsonify({
        "message": "Coupon is valid",
        "code": coupon.code,
        "discount_amount": str(coupon.discount_amount),
        "discount_type": coupon.discount_type,
        "max_uses": coupon.max_uses,
        "times_used": coupon.times_used,
        "min_order_amount": str(coupon.min_order_amount),
    }), 200
