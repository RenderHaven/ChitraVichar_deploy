from flask import Blueprint, request, jsonify,g
from models import db, Product, ProductItem, ProToItem, ProductItemVariation,Description,ImgItem
import uuid
import base64
import config
# Create the Blueprint for handling product items
item_bp = Blueprint('item', __name__)


@item_bp.route('/add_item', methods=['POST'])
def add_item():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        print(data)
        product_id = data.get('product_id')
        item_name = data.get('name')
        price = data.get('price')
        discount= data.get('discount',0)
        description_content = data.get('description', None)
        quantity_in_stock = data.get('stock_quantity')
        variation_value_ids = data.get('variation_value_ids', [])
        disc_id = data.get('disc_id',None)
        tag_name = data.get('tag_name', ' ')  # Tagname
        if  not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "product_id, item name, price, and stock quantity are required"}), 400


        image_url = None

        new_item = ProductItem(
            name=item_name,
            price=price,
            stock_quantity=quantity_in_stock,
            image_url=image_url,
            discount=discount
        )
        db.session.add(new_item)
        db.session.commit()
        
        if(product_id):
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404
            new_pro_to_item = ProToItem(
                i_id=new_item.i_id,
                p_id=product_id
            )
            db.session.add(new_pro_to_item)
            db.session.commit()
        if(variation_value_ids):
            for variation_id in variation_value_ids:
                new_relation = ProductItemVariation(product_item_id=new_item.i_id, variation_option_id=variation_id)
                db.session.add(new_relation)
            db.session.commit()

        # Check if a disc_id was provided
        if disc_id:
            # Use the existing description
            existing_description = Description.query.get(disc_id)
            if existing_description:
                new_item.disc_id = disc_id  # Assign the existing description to the product
                db.session.commit()
            else:
                return jsonify({"error": "Description not found for the provided disc_id"}), 404
        else:
            print("gus aaya")
            # Add a new description with tagline and content
            if description_content and tag_name and description_content!='':
                new_description = Description(
                    content=description_content,
                    tag_name=tag_name
                )
                db.session.add(new_description)
                db.session.commit()
                new_item.disc_id=new_description.id
                print(new_description.id)
                db.session.commit()
        print("sucsess")
        return jsonify({
            "message": "Item added and linked to product successfully",
            "item_id": new_item.i_id,
            "product_id": product_id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500
    

@item_bp.route('/edit_item', methods=['PUT'])
def edit_item():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        item_id = data.get('item_id')
        item_name = data.get('name')
        price = data.get('price')
        discount= data.get('discount')
        quantity_in_stock = data.get('stock_quantity')
        description_content = data.get('description', '')
        variation_value_ids = data.get('variation_value_ids', [])
        disc_id = data.get('disc_id')
        tag_name = data.get('tag_name', ' ')
        if not item_id:
            return jsonify({"error": "item_id is required"}), 400

        existing_item = ProductItem.query.get(item_id)
        if not existing_item:
            return jsonify({"error": "Item not found"}), 404

        if not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "item name, price, and stock quantity are required"}), 400

        # Update item details
        existing_item.name = item_name
        existing_item.price = price
        existing_item.stock_quantity = quantity_in_stock
        if discount:existing_item.discount=discount
        print(discount)
        # Update description
        if disc_id:
            existing_description = Description.query.get(disc_id)
            if existing_description:
                existing_item.disc_id = disc_id
            else:
                return jsonify({"error": "Description not found for the provided disc_id"}), 404
        elif description_content and tag_name:
            new_description = Description(
                content=description_content,
                tag_name=tag_name
            )
            db.session.add(new_description)
            db.session.commit()
            existing_item.disc_id = new_description.id
        # Remove existing variation relationships
        ProductItemVariation.query.filter_by(product_item_id=item_id).delete()
        # Add new variation relationships
        for variation_id in variation_value_ids:
            new_relation = ProductItemVariation(product_item_id=item_id, variation_option_id=variation_id)
            db.session.add(new_relation)

        db.session.commit()

        return jsonify({
            "message": "Item updated successfully",
            "item_id": item_id
        }), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@item_bp.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        if(item_id=='Lable'):return jsonify({"error": "Not Allowed"}), 401
        item = ProductItem.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # ProToItem.query.filter_by(i_id=item_id).delete()
        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Item removed successfully"}), 200

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_products_by_item/<string:item_id>', methods=['GET'])
def get_products_by_item_id(item_id):
    try:

        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Product not found"}), 404

        products = Product.query.join(ProToItem, ProToItem.p_id == Product.p_id)\
            .filter(ProToItem.i_id == item_id).all()

        products_data = [{'p_id': product.p_id, 'name': product.name} for product in products]

        return jsonify({
            "item_id": item.i_id,
            "product_name": item.name,
            "products": products_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_item/<string:item_id>/<string:all>', methods=['GET'])
def get_item_by_id(item_id, all='false'):
    try:

        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404

        if(all=='true'):
            item_data=item.to_dict()
        else :item_data=item.to_small_dict()

        return jsonify(item_data), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@item_bp.route('/search', methods=['GET'])
def search_items():
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        if query == '<all>':
            items = ProductItem.query.all()
        else:
            items = ProductItem.query.filter(
                (ProductItem.name.ilike(f"%{query}%"))
            ).all()

        search_results = [item.to_search_dict() for item in items]

        return jsonify(search_results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@item_bp.route('/add_items_to_product/<string:product_id>', methods=['POST'])
def add_items_to_product(product_id):
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        item_ids = request.json.get('item_ids', [])
        product = Product.query.get_or_404(product_id)

        for item_id in item_ids:
            if(item_id=='Lable'):pass
            product_item = ProductItem.query.get(item_id)
            if product_item and product_item not in product.product_items:
                product.product_items.append(product_item)

        db.session.commit()
        return jsonify({'message': 'Items added to product successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_items_by_filter', methods=['GET'])
def get_items():
    try:
        product_ids = request.args.getlist('ProductIds')

        query = db.session.query(ProductItem)

        if product_ids and 'all' not in product_ids:
            query = query.join(ProductItem.products).filter(Product.p_id.in_(product_ids))

        items = query.all()

        result = []
        for item in items:
            result.append(item.to_search_dict())

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@item_bp.route('/upload_item_images', methods=['POST'])
def upload_item_images():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        item_id = data.get('item_id')
        base64_images = data.get('images', [])

        if not item_id:
            return jsonify({"error": "item_id is required"}), 400

        if not base64_images:
            return jsonify({"error": "No images provided"}), 400

        existing_item = ProductItem.query.get(item_id)
        if not existing_item:
            return jsonify({"error": "Item not found"}), 404

        uploaded_urls = []
        for base64_image in base64_images:
            try:
                image_url = config.uploadImg(base64_image)
                # Save image URL to ImgItem table
                new_img_item = ImgItem(item_id=item_id, image_url=image_url)
                db.session.add(new_img_item)
                uploaded_urls.append(new_img_item.to_dict())
            except Exception as e:
                return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500
        
        if(uploaded_urls):existing_item.image_url=uploaded_urls[0]['image_url']
        db.session.commit()

        return jsonify({
            "message": "Images uploaded successfully",
            "uploaded_images": uploaded_urls
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@item_bp.route('/edit_item_images', methods=['POST'])
def edit_item_images():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        item_id = data.get('item_id')
        images = data.get('images', [])

        if not item_id:
            return jsonify({"error": "item_id is required"}), 400

        if not images:
            return jsonify({"error": "No images provided"}), 400

        # Check if the item exists
        existing_item = ProductItem.query.get(item_id)
        if not existing_item:
            return jsonify({"error": "Item not found"}), 404

        # Remove all existing images for the item
        ImgItem.query.filter_by(item_id=item_id).delete()

        updated_urls = []
        for image in images:
            image_id = image.get('id')
            image_url = image.get('image_url')

            if not image_url:
                return jsonify({"error": "image_url is required for all images"}), 400
            if image_id=='New' or 'http' not in image_url:  # Upload new image to Cloudinary
                try:
                    # Decode and upload the base64 image
                    uploaded_url = config.uploadImg(image_url)

                    # Save new image in the database
                    new_img_item = ImgItem(item_id=item_id, image_url=uploaded_url)
                    db.session.add(new_img_item)
                    updated_urls.append(new_img_item.to_dict())
                except Exception as e:
                    return jsonify({"error": f"Failed to upload new image: {str(e)}"}), 500
            else:  # Add existing image directly
                new_img_item = ImgItem(item_id=item_id, image_url=image_url)
                db.session.add(new_img_item)
                updated_urls.append(new_img_item.to_dict())
        
        if(updated_urls):existing_item.image_url=updated_urls[0]['image_url']

        # Commit all changes
        db.session.commit()

        return jsonify({
            "message": "Images updated successfully",
            "updated_images": updated_urls
        }), 200

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    
