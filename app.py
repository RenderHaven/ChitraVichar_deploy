from flask import Flask, jsonify,g,request
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
from home import home_bp
from variation import variation_bp
from orders import orders_bp
from disc import disc_bp
API_SECRET_KEY='<@pap@a123>'
# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Convert DATABASE_URL (Fix for PostgreSQL URL issues)
database_url = os.getenv("DATABASE_URL",'postgresql://finaldb_vhpx_user:tMnuBkVSZTtDw0SSQWxqZuPO6Ng6w3DI@dpg-cv6rm0ogph6c73dpce30-a.singapore-postgres.render.com/finaldb_vhpx')  #"postgresql://finaldb_vhpx_user:tMnuBkVSZTtDw0SSQWxqZuPO6Ng6w3DI@dpg-cv6rm0ogph6c73dpce30-a.singapore-postgres.render.com/finaldb_vhpx"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database & Migrations
db.init_app(app)
migrate = Migrate(app, db)


@app.before_request
def before_request_func():
    
    """Runs before every request to check API key and set a global flag"""
    g.is_valid_request = False  # Default to False

    api_key = request.headers.get("X-API-KEY")
    if api_key == API_SECRET_KEY:
        print('Owner Req')
        g.is_valid_request = True  # Set True only for this request


# Register Blueprints
app.register_blueprint(product_bp, url_prefix='/product')
app.register_blueprint(item_bp, url_prefix='/item')
app.register_blueprint(home_bp, url_prefix='/home')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(variation_bp, url_prefix='/variation')
app.register_blueprint(disc_bp, url_prefix='/description')
app.register_blueprint(orders_bp, url_prefix='/order')

@app.route('/')
def index():
    return jsonify("Hello, Malik")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
