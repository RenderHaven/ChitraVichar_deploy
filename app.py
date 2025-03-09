from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.engine.url import make_url
import os
import logging

# Import models & Blueprints
from models import db
from users import user_bp
from product import product_bp
from iteam import item_bp
from variation import variation_bp
from orders import orders_bp
from disc import disc_bp

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Convert DATABASE_URL (Fix for PostgreSQL URL issues)
database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database & Migrations
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(product_bp, url_prefix='/product')
app.register_blueprint(item_bp, url_prefix='/item')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(variation_bp, url_prefix='/variation')
app.register_blueprint(disc_bp, url_prefix='/description')
app.register_blueprint(orders_bp, url_prefix='/order')

@app.route('/')
def index():
    return jsonify("Hello, Railway!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
