from flask import request, jsonify
from app.models import db, Customers
from app.extensions import limiter, cache
from app.blueprints.customers import customers_bp
from .schemas import customer_schema, customers_schema
from marshmallow import ValidationError 

#Create customer
@customers_bp.route('', methods=['POST'])
@limiter.limit("5 per day")
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    print("------------- Translated Data ---------------")
    print(data)
    new_customer = Customers(**data)
    db.session.add(new_customer)
    db.session.commit()
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
    return jsonify({"Message": f"Successfully deleted customer {customer_id}"}), 200


#Update customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit("3 per month")
def update_customers(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"Message": "Customer not found"}), 404
    
    try:
        customer_data = customer_schema.load()
    except ValidationError as e:
        return jsonify({"Message": e.messages}), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200
