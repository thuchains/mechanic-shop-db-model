from flask import request, jsonify
from app.models import db, Mechanics
from app.extensions import limiter, cache
from app.blueprints.mechanics import mechanics_bp
from . schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError 

#create mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("6 per day")
def create_mechanic():
    try: 
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    print("------------- Translated Data ---------------")
    print(data)
    new_mechanic = Mechanics(**data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

#View individual mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@cache.cached(timeout=20)
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    return mechanic_schema.jsonify(mechanic), 200

#View all mechanics
@mechanics_bp.route('/', methods=['GET'])
@limiter.limit("20 per hour")
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200

#Delete mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("10 per day")
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    db.session.delete(mechanic)
    db.commit()
    return jsonify({"Message": f"Successfully deleted mechanic {mechanic_id}"}), 200

#Update mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=["PUT"])
@limiter.limit("1 per day")
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"Message": "Mechanic not found"}), 404
    
    try:
        mechanic_data = mechanic_schema.load()
    except ValidationError as e:
        return jsonify({"Message": e.messages}), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200