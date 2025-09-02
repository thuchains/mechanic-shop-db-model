from flask import request, jsonify
from app.models import db, Customers
from app.extensions import limiter, cache
from app.blueprints.customers import customers_bp
from .schemas import customer_schema, customers_schema, customer_login_schema
from marshmallow import ValidationError 
from app.util.auth import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash


# #Login
# @customers_bp.route('/login', methods=['POST'])
# def customer_login():
#     try:
#         data = customer_login_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     customer = db.session.query(Customers).where(Customers.email==data['email']).first()

#     if customer and check_password_hash(customer.password, data['password']):
#         token = encode_token(customer.id)
#         return jsonify({
#             "message": f"Welcome {customer.first_name} {customer.last_name}",
#             "token": token
#         }), 200
    
#     return jsonify("Invalid email or password"), 403

#Create customer
@customers_bp.route('', methods=['POST'])
@limiter.limit("5 per day")
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
         
    try: 
        new_customer = Customers(**data)
        db.session.add(new_customer)
        db.session.commit()
    except:
        return jsonify({"message": "email already taken"}), 400
    
    return customer_schema.jsonify(new_customer), 201


#View individual customer
@customers_bp.route('/<int:customer_id>', methods=['GET'])
@limiter.limit("15 per hour")
@cache.cached(timeout=30)
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    return customer_schema.jsonify(customer), 200


#View all customers
@customers_bp.route('', methods=['GET'])
def read_customers():
    customers = db.session.query(Customers).all()
    return customers_schema.jsonify(customers), 200


#Delete customer
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("5 per day")
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200


#Update customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit("2 per day")
def update_customers(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    try:
        customer_data = customer_schema.load()
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#Search
@customers_bp.route('/search', methods=['GET'])
def search_customer():
    
    email = request.args.get('email')
    customers = db.session.query(Customers).where(Customers.first_name.ilike(f"%{email}%")).all()
    return customers_schema.jsonify(customers), 200