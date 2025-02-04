from flask import Blueprint, request, jsonify
from models import db, User, Address,Cart
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import DatabaseError
user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        number = data.get('number')
        password = data.get('password')
        name = data.get('name', 'User')
        email = data.get('email', 'No Email')
        print(data)
        if not number or not password:
            return jsonify({'message': 'Number and password are required.'}), 400

        ext_user = User.query.filter_by(number=number).first()
        if ext_user:
            return jsonify({'message': 'User with this number already exists.'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(number=number, password=hashed_password, name=name,email=email)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully.', 'user_id': new_user.id}), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'message': 'An error occurred during registration.', 'error': str(e)}), 500

@user_bp.route('/chk/<string:num>', methods=['GET'])
def chk(num):
    try:
        if not num:
            return jsonify({'message': 'Number is required.'}), 400

        user = User.query.filter_by(number=num).first()
        if user:
            return jsonify({'message': 'Old User', 'IsNew': 'False'}), 200
        else:
            return jsonify({'message': 'New User', 'IsNew': 'True'}), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred while checking user.', 'error': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        number = data.get('number')
        password = data.get('password')

        if not number or not password:
            return jsonify({'message': 'Number and password are required.'}), 400

        user = User.query.filter_by(number=number).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid number or password.'}), 401

        return jsonify({'message': 'Login successful.', 'user_id': user.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred during login.', 'error': str(e)}), 500

@user_bp.route('/add_address', methods=['POST'])
def add_address():
    try:
        data = request.json
        user_id = data.get('user_id')
        street = data.get('street')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        if not user_id or not street or not city or not state or not zip_code:
            return jsonify({'message': 'All fields are required.'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        new_address = Address(user_id=user_id, street=street, city=city, state=state, zip_code=zip_code)
        db.session.add(new_address)
        db.session.commit()

        return jsonify({'message': 'Address added successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while adding address.', 'error': str(e)}), 500

@user_bp.route('/get_addresses/<string:user_id>', methods=['GET'])
def get_addresses(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        addresses = Address.query.filter_by(user_id=user_id).all()
        address_list = [address.to_dict() for address in addresses]

        return jsonify({'addresses': address_list}), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching addresses.', 'error': str(e)}), 500
    
@user_bp.route('/get_user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404


        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching userdata', 'error': str(e)}), 500

# Edit an existing address
@user_bp.route('/edit_add/<string:address_id>', methods=['PUT'])
def edit_address(address_id):
    data = request.get_json()
    address = Address.query.get(address_id)
    if not address:
        return jsonify({"error": "Address not found"}), 404
    
    address.street = data.get('street', address.street)
    address.city = data.get('city', address.city)
    address.state = data.get('state', address.state)
    address.zip_code = data.get('zip_code', address.zip_code)
    
    db.session.commit()
    return jsonify({"message": "Address updated successfully", "address": address.to_dict()}), 200

# Delete an address
@user_bp.route('/remove_add/<string:address_id>', methods=['DELETE'])
def delete_address(address_id):
    address = Address.query.get(address_id)
    if not address:
        return jsonify({"error": "Address not found"}), 404
    
    db.session.delete(address)
    db.session.commit()
    return jsonify({"message": "Address deleted successfully"}), 200

@user_bp.route('/edit_user/<string:user_id>', methods=['PUT'])
def edit_user(user_id):
    try:
        data = request.json
        user = User.query.get(user_id)

        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Update user details if provided in request
        user.name = data.get('name', user.name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.dob = data.get('dob', user.dob)
        user.gender = data.get('gender', user.gender)
        user.image_url = data.get('image_url', user.image_url)

        db.session.commit()
        return jsonify({'message': 'User data updated successfully.', 'user': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while updating user data.', 'error': str(e)}), 500
    
@user_bp.route('/get_card_item/<string:user_id>', methods=['GET'])
def get_card_item(user_id):
    """
    Fetch all orders for a given user_id in card format.
    """
    try:
        # Query all orders for the given user_id
        orders = Cart.query.filter_by(user_id=user_id).all()
        
        if orders:
            return jsonify([order.to_dict() for order in orders]), 200
        else:
            return jsonify({"message": "No orders found for the given user_id"}), 404
    except Exception as err:
        print(err)
        return jsonify({"error": "An error occurred while fetching the orders"}), 500

@user_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    try:
        order = Cart(**data)
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except DatabaseError as err:
        db.session.rollback()
        print(err)
        return jsonify({"error": str(err)}), 400
    

@user_bp.route('/remove_from_cart/<string:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    order = Cart.query.get(cart_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Cart Item deleted successfully"}), 200
    else:
        return jsonify({"error": "Cart Item not found"}), 404