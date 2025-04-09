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
        is_promotion = bool(data.get('is_promotion')) if data.get('is_promotion') is not None else None
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
            is_promotion=is_promotion,
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
        is_promotion = bool(data.get('is_promotion')) if data.get('is_promotion') is not None else None
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
        if is_promotion is not None:
            product.is_promotion = is_promotion
        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "p_id": product.p_id,
                "name": product.name,
                "type": product.Type,
                "discount": product.discount,
                "is_active": product.is_active,
                "is_new": product.is_new,
                "is_promotion": product.is_promotion
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500

@product_bp.route('/move_product/<string:product_id>', methods=['PUT'])
def move_product(product_id):
    """
    Edits an existing product, allowing updates to name, type, discount, is_active, and is_new.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        # Parse request data
        data = request.json
        parent_productId=data.get('c_id')

        # Find the product
        product = Product.query.get_or_404(product_id)
        parent_product = Product.query.get_or_404(parent_productId)
        # Update the product fields only if new values are provided
        if(parent_productId):
            product.parent_id=parent_productId

        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "p_id": product.p_id,
                "name": product.name,
                "type": product.Type,
                "discount": product.discount,
                "is_active": product.is_active,
                "is_new": product.is_new,
                "is_promotion": product.is_promotion
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

        all_products = Product.query_active(g.get("is_valid_request", False)).filter_by(parent_id=c_id).all()
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
        product = Product.query_active(g.get("is_valid_request", False)).options(joinedload(Product.product_items)).filter_by(p_id=product_id).first()
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
    
    products = Product.query_active(g.get("is_valid_request", False)).all()

    result = [{
            "p_id": p.p_id,
            "c_id" :p.parent_id,
            "name": p.name,
            # "is_promotion": p.is_promotion,
            # "type": p.Type,
            # "discount": p.discount,
        } for p in products]
    return jsonify(result), 200


@product_bp.route('/remove_item_from_product/<product_id>', methods=['POST'])
def remove_item_from_product(product_id):
    """
    Remove an item from a specific product.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        item_id = data.get('item_id')

        if not item_id:return jsonify({'error': 'Item ID is required'}), 400

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
    


@product_bp.route('/get_items_by_product_list', methods=['POST'])
def item_from_products():
    """
    Retrieve all product items linked to a list of products, grouped by product_id.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Invalid content type. Expected application/json'}), 415

        data = request.get_json()
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400

        grouped_items = {pid: [] for pid in product_ids}

        # Eagerly load variations using joinedload
        product_items = db.session.query(ProductItem, ProToItem.p_id).join(ProToItem).filter(
            ProToItem.p_id.in_(product_ids)
        ).options(joinedload(ProductItem.variations)).all()

        for item, p_id in product_items:
            grouped_items.setdefault(p_id, []).append(item.to_small_dict())

        return jsonify(grouped_items), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

    

@product_bp.route('/get_products_tree', methods=['POST'])
def product_tree():
    """
    Retrieve all product items under the product tree rooted at a given product_id.
    Excludes any product IDs provided in 'product_ids_exclude'.
    Returns full tree structure but skips actual data and children of excluded IDs.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid content type. Expected application/json'}), 415

        root_product_id ='Home'
        product_ids_exclude = []

        if not root_product_id:
            return jsonify({'error': 'No product_id provided'}), 400

        # Recursive CTE: track if a node is excluded, skip recursion if parent is excluded
        query = text("""
            WITH RECURSIVE product_tree AS (
                SELECT p_id, parent_id, name, image_url, is_new,"Type",is_promotion,
                       (p_id = ANY(:exclude_ids)) AS is_excluded
                FROM products 
                WHERE p_id = :root_id AND is_active = TRUE
                UNION ALL
                SELECT p.p_id, p.parent_id, p.name, p.image_url, p.is_new, p."Type",p.is_promotion,
                       (p.p_id = ANY(:exclude_ids)) AS is_excluded
                FROM products p
                INNER JOIN product_tree pt ON p.parent_id = pt.p_id
                WHERE p.is_active = TRUE AND pt.is_excluded = FALSE
            )
            SELECT * FROM product_tree;
        """)

        result = db.session.execute(query, {
            "root_id": root_product_id,
            "exclude_ids": product_ids_exclude
        })
        products = result.fetchall()

        if not products:
            return jsonify({'error': 'No products found'}), 404

        product_dict = {}
        parent_map = {}

        for row in products:
            p_id, parent_id, name, image_url, is_new,type,is_promotion, is_excluded= row
            parent_map[p_id] = parent_id

            if not is_excluded:
                product_dict[p_id] = {
                    "p_id": p_id,
                    "c_id":parent_id,
                    "name": name,
                    "image_url": image_url,
                    "is_new": is_new,
                    "type":type,
                    "is_promotion": is_promotion,
                    "sub_products": [],
                }

        # Link children (even excluded ones) to their parent’s sub_products
        for child_id, parent_id in parent_map.items():
            if parent_id in product_dict:
                product_dict[parent_id]["sub_products"].append(child_id)

        return jsonify(product_dict), 200

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