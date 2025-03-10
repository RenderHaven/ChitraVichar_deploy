from models import db, Product,Variation,VariationOption,User
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
    "Pro4": {
        "PId": 'Test',
        "name": "Testing",
        "CId": 'Home',  # Link this product to the "Home" category
    },
}
# Sample category data
category_data = {
    "Cat1": {
        "CId": 'Cat1',
        "PId": None,  # Parent ID is None for top-level categories
        "name": "Base",
    },
    "Cat2": {
        "CId": 'Home',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "HomePage",
    },
    "Cat3": {
        "CId": 'Pro',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "Prmotions",
    },
    "Cat4": {
        "CId": 'New',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "NewProducts",
    },
    "Cat5": {
        "CId": 'Home',
        "PId": 'Home',  # Parent ID is 'Cat1'
        "name": "Testing",
    },
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

    for id,info in variation_data.items():
        variation = Variation(
            name=info['name'],
        )
        db.session.add(variation)
        db.session.commit()
        for option_value in info['options']:
            option = VariationOption(value=option_value, variation_id=variation.id,variation_name=info['name'])
            db.session.add(option)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        print("Database Path:", db.engine.url.database)
        db.drop_all()  # Drops all tables to start fresh
        db.create_all()  # Re-creates the tables
        insert_data()  # Inserts the sample data
    print("Data inserted successfully")
