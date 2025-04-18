from flask import Blueprint, request, jsonify,g
from models import db, Variation, VariationOption ,ProductItem ,ProductItemVariation
from sqlalchemy.exc import IntegrityError

variation_bp = Blueprint('variation_bp', __name__)

# Route to add a new variation
@variation_bp.route('/add_variation', methods=['POST'])
def add_variation():
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        # Get data from request body
        data = request.get_json()

        # Debugging: Check the input data
        print("Received data:", data)

        # Validate input
        if not data.get('name') or not data.get('options'):
            return jsonify({"error": "Name and options are required"}), 400


        variation = Variation(
            name=data['name'],
        )
        
        db.session.add(variation)
        db.session.commit()
        
        # Debugging: Check if the variation was added
        print("Variation added:", variation.id)

        # Add options (values) to the variation
        i=0
        for option_value in data['options']:
            option = VariationOption(value=option_value,variation_name=data['name'], variation_id=variation.id,disc=data['discs'][i] if len(data['discs'])>i else None)
            db.session.add(option)
            i+=1
        db.session.commit()
        
        # Return success response
        return jsonify({"message": "Variation added successfully", "name": variation.name}), 201

    except IntegrityError as e:
        db.session.rollback()
        print("IntegrityError:", e)
        return jsonify({"error": "Database error. Could not add variation."}), 500
    except Exception as e:
        # Catch all other exceptions and return the error
        print("Error:", e)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Route to get all variations with id and name
@variation_bp.route('/get_variation', methods=['GET'])
def get_all_variations():
    variations = Variation.query.all()
    variation_list = [{"id": variation.id, "name": variation.name} for variation in variations]
    return jsonify(variation_list)




@variation_bp.route('/attach_variation', methods=['POST'])
def attach_variation_to_item():
    """
    Attach a variation option to a product item.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        
        # Validate input
        item_id = data.get('item_id')
        variation_option_id = data.get('variation_option_id')

        if not item_id or not variation_option_id:
            return jsonify({"error": "item_id and variation_option_id are required"}), 400

        # Check if product item exists
        product_item = ProductItem.query.get(item_id)
        if not product_item:
            return jsonify({"error": f"ProductItem with id {item_id} does not exist"}), 404

        # Check if variation option exists
        variation_option = VariationOption.query.get(variation_option_id)
        if not variation_option:
            return jsonify({"error": f"VariationOption with id {variation_option_id} does not exist"}), 404

        # Check if this variation is already attached
        existing_relation = ProductItemVariation.query.filter_by(
            product_item_id=item_id,
            variation_option_id=variation_option_id
        ).first()
        if existing_relation:
            return jsonify({"message": "Variation is already attached to the item"}), 200

        # Create a new relationship
        new_relation = ProductItemVariation(
            product_item_id=item_id,
            variation_option_id=variation_option_id
        )
        db.session.add(new_relation)
        db.session.commit()

        return jsonify({"message": "Variation successfully attached to the item"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@variation_bp.route('/get_variations_by_item/<string:item_id>', methods=['GET'])
def get_variations_by_item(item_id):
    """
    Get variations (names and values) associated with a product item by its item_id.
    """
    try:
        # Query the ProductItemVariation table for the given item_id
        item_variations = ProductItemVariation.query.filter_by(product_item_id=item_id).all()

        if not item_variations:
            return jsonify({"error": "No variations found for the given item_id"}), 404

        # Prepare a list of variation details
        variations = []
        variation_ids = set()  # Track unique variation_id's

        for item_variation in item_variations:
            variation_option = VariationOption.query.get(item_variation.variation_option_id)
            if variation_option:
                variation_id = variation_option.variation_id
                if variation_id not in variation_ids:
                    get_name = lambda name: ("", "") if not name else (name.split("::", 1)[0], name.split("::", 1)[1] if "::" in name else name)
                    variation_name, _ = get_name(variation_option.name)
                    # Get all options for this variation_id
                    options = VariationOption.query.filter_by(variation_id=variation_id).all()
                    variations.append({
                        "variation_id": variation_id,
                        "variation_name": variation_name,
                        "option_values": [opt.value for opt in options],
                        "option_ids": [opt.id for opt in options]
                    })
                    variation_ids.add(variation_id)

        return jsonify(variations), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

@variation_bp.route('/search', methods=['GET'])
def search_variations():
    """
    Search for variations by name, or return all variations if the query is 'all'.
    """
    try:
        query = request.args.get('query', '').strip()

        # If 'query' is '<all>', return all variations
        if query == '<all>':
            variations = Variation.query.all()
        elif query:
            # If the query is not empty, filter by name
            variations = Variation.query.filter(Variation.name.ilike(f"%{query}%")).all()
        else:
            return jsonify({"error": "Query parameter is required"}), 400

        if not variations:
            return jsonify({"message": "No variations found"}), 404

        result = [variation.to_dict() for variation in variations]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@variation_bp.route('/edit_variation/<string:variation_id>', methods=['PUT'])
def edit_variation(variation_id):
    """
    Edit a variation's name or options while preserving foreign key integrity.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        new_name = data.get('name')
        new_options = data.get('options', [])

        if not new_name:
            return jsonify({"error": "Name is required"}), 400

        # Find the variation
        variation = Variation.query.get(variation_id)
        if not variation:
            return jsonify({"error": "Variation not found"}), 404

        # Update variation name
        variation.name = new_name

        # Fetch existing options for this variation
        existing_options = {opt.id: opt for opt in VariationOption.query.filter_by(variation_id=variation_id).all()}

        # Track option IDs that should remain
        received_option_ids = set()
        
        for option in new_options:
            option_id = option.get('id')
            option_value = option.get('value')
            option_disc = option.get('disc')

            if not option_value:
                return jsonify({"error": "Option value is required"}), 400

            if option_id in existing_options:
                # Update existing option
                existing_options[option_id].value = option_value
                existing_options[option_id].disc = option_disc
                existing_options[option_id].variation_name = new_name
                received_option_ids.add(option_id)
            else:
                # Add new option
                new_option = VariationOption(value=option_value, variation_id=variation_id, disc=option_disc,variation_name=new_name)
                db.session.add(new_option)

        # Remove options that were not included in the request
        for opt_id in set(existing_options.keys()) - received_option_ids:
            db.session.delete(existing_options[opt_id])

        db.session.commit()
        return jsonify({"message": "Variation updated successfully","data":variation.to_dict()}), 200

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





@variation_bp.route('/delete_variation/<string:variation_id>', methods=['DELETE'])
def delete_variation(variation_id):
    """
    Delete a variation and its options.
    """
    try:
        if not g.is_valid_request:
            return jsonify({"error": "Unauthorized"}), 401
        # Find the variation
        variation = Variation.query.get(variation_id)
        if not variation:
            return jsonify({"error": "Variation not found"}), 404

        # Delete all associated options
        VariationOption.query.filter_by(variation_id=variation_id).delete()
        
        # Delete the variation
        db.session.delete(variation)
        db.session.commit()

        return jsonify({"message": "Variation deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


