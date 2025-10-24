from flask import request, jsonify
from app.models import db, Mechanics
from app.extensions import limiter, cache
from app.blueprints.mechanics import mechanics_bp
from . schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from marshmallow import ValidationError 
from app.util.auth import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.blueprints.service_tickets.schemas import service_tickets_schema


#Login
@mechanics_bp.route('/login', methods=['POST'])
@limiter.limit("50 per hour")
def login():
    try: 
        data = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    mechanic = db.session.query(Mechanics).where(Mechanics.email==data['email']).first()

    if mechanic and check_password_hash(mechanic.password, data['password']):
        token = encode_token(mechanic.id)
        return jsonify({
            "message": f"Welcome {mechanic.first_name} {mechanic.last_name}",
            "token": token,
            "id": mechanic.id
        }), 200
    
    return jsonify("Invalid email or password"), 403


#create mechanic
@mechanics_bp.route('', methods=['POST'])
@limiter.limit("10 per day")
def create_mechanic():
    try: 
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    data['password'] = generate_password_hash(data['password'])

    mechanic = db.session.query(Mechanics).where(Mechanics.email==data['email']).first()
    if mechanic:
        return jsonify({"message": "Email already taken"}), 400
    
    new_mechanic = Mechanics(**data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


#View individual mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@limiter.limit("10 per hour")
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    return mechanic_schema.jsonify(mechanic), 200


#View all mechanics
@mechanics_bp.route('', methods=['GET'])
@cache.cached(timeout=30)
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200


#Delete mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("5 per day")
@token_required
def delete_mechanic(mechanic_id):
    token_id = request.mechanic_id

    mechanic = db.session.get(Mechanics, token_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted mechanic {token_id}"}), 200


#Update mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=["PUT"])
@limiter.limit("5 per hour")
@token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    if 'password' in mechanic_data:
        mechanic_data['password'] = generate_password_hash(mechanic_data['password'])

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#Get popular mechanics
@mechanics_bp.route('/popularity', methods=['GET'])
def get_popular_mechanics():
    mechanics = db.session.query(Mechanics).all()
    mechanics.sort(key=lambda mechanic:len(mechanic.service_tickets), reverse=True)

    output = []
    for mechanic in mechanics:
        mechanic_format = {
            "first name": mechanic_schema.dump(mechanic.first_name),
            "last name": mechanic_schema.dump(mechanic.last_name)
        }
        output.append(mechanic_format)

    return jsonify(output), 200

#Get service tickets related to mechanic
@mechanics_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_related_tickets():
    token_id = request.mechanic_id
    mechanic = db.session.get(Mechanics, token_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404
    
    tickets = mechanic.service_tickets
    tickets.sort(key=lambda ticket: ticket.service_date, reverse=True)
    return service_tickets_schema.jsonify(tickets), 200
    
