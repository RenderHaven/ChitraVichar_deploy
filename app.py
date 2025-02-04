from flask import Flask, render_template,jsonify
from flask_cors import CORS
from models import db, Category, Product
from users import user_bp
from product import product_bp  # Import the Blueprint
from iteam import item_bp  # Import the Blueprint
from category import category_bp
from variation import variation_bp
from orders import orders_bp
from disc import disc_bp
import os
from flask_migrate import Migrate
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


# Enable CORS for all origins (ensure this is intentional for security reasons)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type"]}})



# Configure the database connection string from environment variables, fallback to SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///app.db')  #"postgresql://chitravihar_database_user:5L8PZ52f1fSrYREgBbpoah0W9619KoK9@dpg-cugt3i1u0jms73fqq2v0-a.singapore-postgres.render.com/chitravihar_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)


# Register Blueprints with proper url_prefix
app.register_blueprint(product_bp, url_prefix='/product')
app.register_blueprint(item_bp, url_prefix='/item')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(category_bp, url_prefix='/category')
app.register_blueprint(variation_bp, url_prefix='/variation')
app.register_blueprint(disc_bp, url_prefix='/description')
app.register_blueprint(orders_bp, url_prefix='/order')


@app.route('/')
def index():
    return jsonify("hii")

if __name__ == '__main__':
    with app.app_context():  # This establishes an application context
        db.create_all() 
        migrate.init_app(app, db)
    # Running the app with debug mod
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
