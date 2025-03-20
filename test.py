from models import db, Product,Variation,VariationOption,ProductItem,OrderItems,Order
from sqlalchemy import text
from app import app
from werkzeug.security import generate_password_hash, check_password_hash

# Sample product data
product_data = {
    "Pro1": {
        "PId": 'Home',
        "name": "Home",
        "CId": None,  # Link this product to the "Home" category
    },
    "Pro2": {
        "PId": 'Pro',
        "name": "Promotion",
        "CId": None,  # Link this product to the "Home" category
    },
    # "Pro4": {
    #     "PId": 'Test',
    #     "name": "Testing",
    #     "CId": 'Home',  # Link this product to the "Home" category
    # },
}

variation_data = {
    "Cat1": {
        "name": "Discount",
        "options":['10','20']
    },
    "Cat2": {
        "name": "Size",
        "options":['S','L','M','XL']
    },
    "Cat3": {
        "name": "Color",
        "options":['Black','Red','Blue','White']
    },
}

def insert_data():
    # Ensure the database schema exists
    db.create_all()
    new_item = ProductItem(
            i_id='Lable',
            name='Lables',
            image_url='dsd',
        )
    db.session.add(new_item)
    db.session.commit()
    # Insert categories
    # for id, info in category_data.items():
    #     new_category = Category(
    #         c_id=info['CId'],
    #         pc_id=info['PId'],  # Parent category ID
    #         name=info['name'],
    #     )
    #     db.session.add(new_category)

    # Insert products
    for id, info in product_data.items():
        new_product = Product(
            p_id=info['PId'],
            name=info['name'],
            parent_id=info['CId'],  # Assign the category ID
        )
        db.session.add(new_product)

    # Commit all changes to the database
    db.session.commit()

def update_all():
    with app.app_context():
        print("Database Path:", db.engine.url.database)

        db.drop_all()
        db.create_all()  # Rebuild tables after dropping
        insert_data()    # Inserts the sample data

    print("Data inserted successfully")

def update_order():
    with app.app_context():
        print("Database Path:", db.engine.url.database)

        # Drop tables with CASCADE to remove dependencies
        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))

        db.create_all()  # Rebuild tables after dropping
        print("Data inserted successfully")
