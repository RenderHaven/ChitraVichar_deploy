
from flask import Blueprint
from flask import Blueprint,jsonify
from models import ImgItem,ProductItem

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