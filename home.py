
from flask import Blueprint
from flask import Blueprint,jsonify
from models import ImgItem

home_bp = Blueprint('home', __name__)
@home_bp.route('/get_banners', methods=['GET'])
def get_banner():
    try:

        item =ImgItem.query.filter_by(item_id='Lable').all()
        if not item:
            return jsonify({"error": "Banner Not Found"}), 404

        banners=[img.image_url for img in item]

        return jsonify(banners), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500