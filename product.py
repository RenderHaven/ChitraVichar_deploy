from flask import Blueprint, request, jsonify,g
from models import db, Product, ProductItem, ProToItem, Description
import category as Cat
from sqlalchemy import or_,text,and_
from sqlalchemy.orm import joinedload
import config
# Create the Blueprint
product_bp = Blueprint('product', __name__)

@product_bp.route('/add_product', methods=['POST'])
def add_product():
    """
    Adds a new product and creates a corresponding category with the product name.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Parse request data
        data = request.json
        pc_id = data.get('c_id')  # Parent category ID
        product_name = data.get('name')  # Product name
        # description_content = data.get('description', '')  # Optional product description
        # tag_name = data.get('tag_name', ' ')  # Tagname
        # disc_id = data.get('disc_id')  # Description ID
        typ = data.get('type')
        discount=data.get('discount')
        is_active = bool(data.get('is_active')) if data.get('is_active') is not None else None
        is_new = bool(data.get('is_new')) if data.get('is_new') is not None else None
        print(data)
        if not pc_id or not product_name:
            return jsonify({"error": "pc_id and name are required"}), 400

        # Check if the parent category exists
        parent_product = Product.query.get(pc_id)
        if not parent_product:
            return jsonify({"error": "Parent category not found"}), 404
        
        # Create a new product under the newly created category
        new_product = Product(
            name=product_name,
            parent_id=pc_id,
            # disc_id=disc_id,  # Use the provided description ID if available
            discount=discount,
            Type=typ,
            is_active=is_active,
            is_new=is_new,
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            "message": "Product added successfully",
            "product_id": new_product.p_id,
            "category_id": pc_id,
        }), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500
    
@product_bp.route('/edit_product/<string:product_id>', methods=['PUT'])
def edit_product(product_id):
    """
    Edits an existing product, allowing updates to name, type, discount, is_active, and is_new.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        # Parse request data
        data = request.json
        new_name = data.get('name')
        new_type = data.get('type')
        new_discount = data.get('discount')
        is_active = bool(data.get('is_active')) if data.get('is_active') is not None else None
        is_new = bool(data.get('is_new')) if data.get('is_new') is not None else None

        # Find the product
        product = Product.query.get_or_404(product_id)

        # Update the product fields only if new values are provided
        if new_name is not None and new_name.strip():
            product.name = new_name
        if new_type is not None and new_type.strip():
            product.Type = new_type
        if new_discount is not None:
            product.discount = new_discount
        if is_active is not None:
            product.is_active = is_active
        if is_new is not None:
            product.is_new = is_new

        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "p_id": product.p_id,
                "name": product.name,
                "type": product.Type,
                "discount": product.discount,
                "is_active": product.is_active,
                "is_new": product.is_new
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500

    
@product_bp.route('/upload_product_image', methods=['POST'])
def upload_product_image():
    """
    Uploads an image for an existing product and updates its image_url.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.json
        product_id = data.get('product_id')
        base64_image = data.get('display_img')

        if not product_id or not base64_image:
            return jsonify({"error": "product_id and image are required"}), 400

        # Find the product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Upload image to Cloudinary
        image_url=config.uploadImg(base64_image)
        print(image_url)
        # Update product image_url
        product.image_url = image_url
        db.session.commit()

        return jsonify({"message": "Image uploaded successfully", "image_url": image_url}), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@product_bp.route('/get_product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """
    Retrieves a specific product by its ID.
    """
    try:
        # Find the product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Return product details
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@product_bp.route('/get_products_by_category/<string:c_id>', methods=['GET'])
def get_products_by_category(c_id):
    """
    Retrieves a list of product IDs for a given parent category ID (pc_id),
    including products of all subcategories.
    """
    try:
        if(c_id=='null'):c_id=None
        # Find the subcategories under the given category_id\
        if g.is_valid_request:
            all_products = Product.query.filter_by(parent_id=c_id).all()
        else :
            all_products = Product.query.filter(
            and_(
                Product.parent_id == c_id,
                Product.is_active == True   # Inverts the boolean condition
            )
            ).all()

        if not all_products:
            return jsonify({"message": "No products found for this category"}), 401

        products_data = []
        for product in all_products:
            products_data.append(product.to_small_dict())
        return jsonify(products_data), 200
    

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@product_bp.route('/get_items_by_product/<string:product_id>', methods=['GET'])
def get_items_by_product_id(product_id):
    try:
        product = Product.query.options(joinedload(Product.product_items)).filter_by(p_id=product_id).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Fetch linked items using explicit join
        items_data = [
            {'i_id': item.i_id, 'name': item.name, 'image_url': item.image_url, 'price': item.price}
            for item in product.product_items
        ]

        return jsonify(items_data), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@product_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    if len(query) < 3:
        return jsonify({"error": "Search query must be at least 3 characters long"}), 400
    
    if g.is_valid_request:
        products = Product.query.all()
    else:
        products = Product.query.filter(Product.is_active == True).all()

    result = [{
            "p_id": p.p_id,
            "c_id" :p.parent_id,
            "name": p.name,
            # "Type": p.Type,
            # "discount": p.discount,
        } for p in products]
    return jsonify(result), 200

# @product_bp.route('/search_query', methods=['GET'])
# def search_products_byquery():
#     query = request.args.get('query', '').strip()
#     if len(query) < 3:
#         return jsonify({"error": "Search query must be at least 3 characters long"}), 400
    
        

#     # Search products by name (case-insensitive)
#     if g.is_valid_request:
#         products = Product.query.all()
#     else:
#         products = query.filter(Product.is_active == True).all()

#     result = [{
#             "p_id": p.p_id,
#             "c_id" :p.parent_id,
#             "name": p.name,
#             "Type": p.Type,
#             "discount": p.discount,
#         } for p in products if p.is_active]
#     return jsonify(result), 200


@product_bp.route('/remove_item_from_product/<product_id>', methods=['POST'])
def remove_item_from_product(product_id):
    """
    Remove an item from a specific product.
    """
    try:
        auth_error = config.verify_api_key()
        if auth_error:
            return auth_error
        
        data = request.get_json()
        item_id = data.get('item_id')

        if not item_id:
            return jsonify({'error': 'Item ID is required'}), 400

        # Find the product-item relationship
        product_item = ProToItem.query.filter_by(p_id=product_id, i_id=item_id).first()

        if not product_item:
            return jsonify({'error': 'Item not found in this product'}), 404

        # Remove the relationship
        db.session.delete(product_item)
        db.session.commit()

        return jsonify({'message': 'Item removed from product successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    



@product_bp.route('/get_products_of_gender/', methods=['GET'])
def get_products_by_gender():
    """
    Retrieves a list of products filtered by gender type (Man, Woman, UniSex).
    """
    try:
        # Query subcategories based on the Type field
        all_products = Product.query.filter(
            or_(
                Product.Type == 'Man',
                Product.Type == 'Women',
                Product.Type == 'UniSex',
            )
        ).all()

        if not all_products:
            return jsonify([]), 200

        # Prepare product data
        data = [
            {
                "p_id": product.p_id,
                "name": product.name,
                "image_url": product.image_url,
                "type": product.Type
            }
            for product in all_products
        ]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@product_bp.route('/get_new_products/', methods=['GET'])
def get_new_products():
    """
    Retrieves a list of products filtered by gender type (Man, Woman, UniSex).
    """
    try:
        # Query subcategories based on the Type field
        all_products = Product.query.filter(
            and_(
                Product.is_new==True,
                Product.is_active==True,
            )
        ).all()

        if not all_products:
            return jsonify([]), 200

        # Prepare product data
        data = [
            {
                "p_id": product.p_id,
                "name": product.name,
                "image_url": product.image_url,
            }
            for product in all_products
        ]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@product_bp.route('/get_items_by_productlist', methods=['POST'])
def item_from_product():
    """
    Retrieve all product items linked to a list of products, including their sub-products.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Invalid content type. Expected application/json'}), 415

        data = request.get_json()
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400

        # Recursive CTE query to get all products and their sub-products
        query = text("""
            WITH RECURSIVE product_tree AS (
                SELECT p_id, parent_id FROM products WHERE p_id = ANY(:product_ids)
                UNION
                SELECT p.p_id, p.parent_id FROM products p
                INNER JOIN product_tree pt ON p.parent_id = pt.p_id
            )
            SELECT p_id FROM product_tree;
        """)

        result = db.session.execute(query, {"product_ids": product_ids})
        all_product_ids = [row[0] for row in result.fetchall()]

        if not all_product_ids:
            return jsonify({'error': 'No products found'}), 404

        # Fetch product items in a single query
        product_items = db.session.query(ProductItem).join(ProToItem).filter(
            ProToItem.p_id.in_(all_product_ids)
        ).all()

        # Prepare response
        items_data = [item.to_small_dict() for item in product_items]

        return jsonify(items_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/remove_product/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        # Find the product by its ID
        product = Product.query.get(product_id)
        if(product_id in ('Home','Pro','New')):
            return jsonify({"message": "Products are imutable"}), 200
        if not product :
            return jsonify({"error": "Product not found"}), 404

        
        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Products and related entries removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500