import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Float,Text
from sqlalchemy.orm import relationship
from collections import defaultdict
db = SQLAlchemy()


class Description(db.Model):
    __tablename__ = 'descriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(Text, nullable=False)  # The description content
    tag_name = db.Column(db.String(50), nullable=False)  # Optional tag name for the description

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "tag_name": self.tag_name,  # Include the tag name in the serialized data
        }
    

class Product(db.Model):
    __tablename__ = 'products'

    p_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = db.Column(db.String(36), db.ForeignKey('products.p_id', ondelete="CASCADE"), nullable=True) 
    name = db.Column(db.String(200), nullable=False)
    disc_id = db.Column(db.String(36), ForeignKey('descriptions.id'), nullable=True)  # Reference to Description
    image_url = db.Column(db.String(500))
    # c_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=False)
    Type = db.Column(db.String(200), nullable=False, default="Other")
    discount = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True)  # Boolean column
    is_new = db.Column(db.Boolean, default=False)  # Boolean column
    # category = relationship("Category", back_populates="products")
    description = relationship("Description", backref="products")  # Relationship with Description table
    product_items = relationship('ProductItem', secondary='product_to_items', back_populates="products")

    sub_products = db.relationship(
        "Product",
        cascade="all, delete-orphan",  # Automatically delete sub-products when parent is deleted
        backref=db.backref("parent", remote_side=[p_id])
    )

    def to_dict(self):
        return {
            "p_id": self.p_id,
            "c_id" :self.parent_id,
            "name": self.name,
            # "description": self.description.content if self.description else None,  # Use the Description relation
            # "tag_name": self.description.tag_name if self.description else None,
            # 'disc_id': self.description.id if self.description else None,
            "image_url": self.image_url,
            "Type": self.Type,
            "discount": self.discount,
            "items_id": [item.i_id for item in self.product_items],
            "is_active": self.is_active,
            "is_new": self.is_new,
        }
    def to_small_dict(self):
        return {
            "p_id": self.p_id,
            "c_id" :self.parent_id,
            "name": self.name,
            "image_url": self.image_url,
            "Type": self.Type,
            "discount": self.discount,
            "is_active": self.is_active,
            "is_new": self.is_new,
        }


class ProductItem(db.Model):
    __tablename__ = 'product_items'

    i_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False, default=0.0)
    disc_id = db.Column(db.String(36), ForeignKey('descriptions.id'), nullable=True)  # Reference to Description
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    description = relationship("Description", backref="product_items")  # Relationship with Description table
    products = relationship('Product', secondary='product_to_items', back_populates="product_items",lazy='select')
    variations = relationship("ProductItemVariation", back_populates="product_item", cascade="all, delete-orphan",lazy='select')
    orders = db.relationship('Order', backref='item', lazy='select')
    carts = db.relationship('Cart', backref='item', lazy='select',cascade="all, delete-orphan")

    
    def _group_variation_data(self,all=True):
        grouped_data = defaultdict(lambda: {"variation_name": "", "options": []})
        
        # Process products and variations in one loop for efficiency
        products = []
        my_options=[]
        max_discount = self.discount
        
        for product in self.products:
            products.append({"name": product.name, "p_id": product.p_id})
            if isinstance(product.discount, (int, float)):
                max_discount = max(max_discount, float(product.discount))

        result = []
        for var in self.variations:
            my_options.append(var.variation_option_id)
            if(all):
                item = var.variation_option.to_dict()
                variation_id = item["variation_id"]

                grouped_data[variation_id]["variation_name"] = item["variation_name"]
                grouped_data[variation_id]["options"].append({
                    "id": item["id"],
                    "value": item["value"]
                })

        # Final result conversion in a separate loop for clarity
        if all:
            result = [
                {
                    "variation_id": var_id,
                    "variation_name": data["variation_name"],
                    "options": data["options"]
                }
                for var_id, data in grouped_data.items()
            ]

        return result, max_discount,my_options, products

        
    def to_dict(self):
        grouped_variations, max_discount,my_options,products = self._group_variation_data()

        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "description": self.description.content if self.description else None,
            "tag_name": self.description.tag_name if self.description else None,
            "disc_id": self.description.id if self.description else None,
            "stock_quantity": self.stock_quantity,
            "images": [image.to_dict() for image in self.images],
            "products": products,
            "variations": grouped_variations,
            "discount": max_discount,
        }

    def to_small_dict(self):
        grouped_variations, max_discount,my_options,products = self._group_variation_data(all=False)
        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "my_options":my_options, 
            "discount": max_discount,
        }
    
    def to_search_dict(self):
        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
        }
    def to_cart_dict(self):
        grouped_variations, max_discount = self._group_variation_data()
        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "variations": grouped_variations,
            "discount": max_discount,
        }



class ProToItem(db.Model):
    __tablename__ = 'product_to_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.String(36),ForeignKey('products.p_id',ondelete="CASCADE"), nullable=False)
    i_id = db.Column(db.String(36), ForeignKey('product_items.i_id',ondelete="CASCADE"),nullable=False)


class Variation(db.Model):
    __tablename__ = 'variations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)

    options = relationship("VariationOption", back_populates="variation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "options": [option.to_dict() for option in self.options],
        }


class VariationOption(db.Model):
    __tablename__ = 'variation_options'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id = db.Column(db.String(36), ForeignKey('variations.id'), nullable=False)
    variation_name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    disc = db.Column(db.String(300), nullable=True)  
    variation = relationship("Variation", back_populates="options")
    product_items = relationship("ProductItemVariation", back_populates="variation_option" ,cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "variation_id": self.variation_id,
            "value": self.value,
            "variation_name": self.variation_name,
            'disc':self.disc,
        }



class ProductItemVariation(db.Model):
    __tablename__ = 'product_item_variations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_item_id = db.Column(db.String(36), ForeignKey('product_items.i_id',ondelete="CASCADE"), nullable=False)
    variation_option_id = db.Column(db.String(36), ForeignKey('variation_options.id',ondelete="CASCADE"),nullable=False)

    product_item = relationship("ProductItem", back_populates="variations",lazy='select')
    variation_option = relationship("VariationOption", back_populates="product_items",lazy='select')

    def to_dict(self):
        return {
            "id": self.id,
            "product_item_id": self.product_item_id,
            "variation_option_id": self.variation_option_id,
            # "product_item": self.product_item.to_dict() if self.product_item else None,
            # "variation_option": self.variation_option.to_dict() if self.variation_option else None,
        }


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(500),nullable=True)
    last_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    dob= db.Column(db.String(50), nullable=True)
    gender= db.Column(db.String(50), nullable=True)
    number = db.Column(db.String(15), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False,default='123456')
    addresses = db.relationship('Address', backref='user', lazy='select',cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy='select',cascade="all, delete-orphan") 

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "first_name" :self.name,
            "last_name" :self.last_name,
            "email":self.email,
            'dob':self.dob,
            'gender':self.gender,
            'profile_picture':self.image_url,
            'my_addresses':[add.to_dict() for add in self.addresses],
            # 'my_orders':[order.to_dict() for order in self.orders]
        }


class Address(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)


    def to_dict(self):
        return {
            "id": self.id,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
        }

class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)  # Reference to User
    i_id = db.Column(db.String(36), db.ForeignKey('product_items.i_id',ondelete="CASCADE"), nullable=False)  # Reference to ProductItem

    
    
    def to_dict(self):
        data=self.item.to_small_dict()
        return {
            'cart_id':self.id,
            **data
        }

class Order(db.Model):
    __tablename__ = 'orders'

    o_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  # Reference to User
    i_id = db.Column(db.String(36), db.ForeignKey('product_items.i_id'), nullable=False)  # Reference to ProductItem
    address = db.Column(db.String(500), nullable=True)  # Store address as a string
    status = db.Column(db.String(50), nullable=False, default='IN_CART')  # Status of the order
    datetime = db.Column(db.DateTime, nullable=False, default=db.func.now())  # Timestamp for the order
    short_note = db.Column(db.String(300), nullable=True)  
    delivery_charge = db.Column(db.Integer, nullable=True)
    total_price = db.Column(db.Integer, nullable=True)
    oi_id = db.Column(db.String(36), db.ForeignKey('order_items.oi_id'), nullable=False)  # Reference to ProductItem

    def to_dict(self):
        return {
            "id": self.o_id,
            "user_id": self.user_id,
            "i_id": self.i_id,
            "address": self.address,  # Now storing the address directly as a string
            "item_name": self.item.name if self.item else None,
            "quantity": self.quantity,
            "status": self.status,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "user": self.user.to_dict() if self.user else None,  # Include user information
        }
    
class OrderItems(db.Model):
    __tablename__ = 'order_items'
    oi_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    i_id = db.Column(db.String(36), db.ForeignKey('product_items.i_id'), nullable=True)  # Reference to ProductItem
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False, default=0.0)
    original_price = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    other_details = db.Column(db.Text, nullable=True)  
    
    
# New model for storing image URLs
class ImgItem(db.Model):
    __tablename__ = 'img_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = db.Column(db.String(36), db.ForeignKey('product_items.i_id',ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    product_item = relationship("ProductItem", backref=db.backref("images", cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "image_url": self.image_url,
        }
    
