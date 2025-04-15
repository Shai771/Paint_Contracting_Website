from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


# contact_form table
class ContactForm(db.Model):
    __tablename__ = 'contact_form'

    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    project_type = db.Column(db.String(20), nullable=False)  # Fresh Painting or Re-Painting
    project_space = db.Column(db.String(20), nullable=False)  # Interior or Exterior
    square_feet = db.Column(db.String(10), nullable=False)  # e.g., "2000 sqft"

    def __init__(self, name, email, mobile, pincode, project_type, project_space, square_feet):
        self.name = name
        self.email = email
        self.mobile = mobile
        self.pincode = pincode
        self.project_type = project_type
        self.project_space = project_space
        self.square_feet = square_feet

# user_credential table
class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'  # Ensure it matches phpMyAdmin

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Store hashed passwords in production

    def __init__(self, email, password):
        self.email = email
        self.password = password


# Paint Materials table
class PaintMaterials(db.Model):
    __tablename__ = 'paint_materials'

    paint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paint_name = db.Column(db.String(100), nullable=False)
    paint_brand=db.Column(db.String(100),nullable=False)
    per_cost= db.Column(db.Float, nullable=False)  # Price per square foot
    paint_qty = db.Column(db.Integer, nullable=False)  # Available quantity in stock

    def __init__(self, paint_name,paint_brand, per_cost, paint_qty):
        self.paint_name = paint_name
        self.paint_brand=paint_brand
        self.per_cost = per_cost
        self.paint_qty = paint_qty

        







