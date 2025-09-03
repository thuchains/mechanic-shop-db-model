from flask import request, jsonify
from app.models import Parts, PartDescriptions, db
from app.extensions import limiter, cache
from app.blueprints.parts import parts_bp
from app.blueprints.parts.schemas import part_schema, parts_schema, part_description_schema, part_descriptions_schema
from marshmallow import ValidationError


#Create Parts 
@parts_bp.route('/<int:description_id>', methods=['POST'])
@limiter.limit ("20 per hour")
def create_part(description_id):
    quantity = request.args.get('qty', 1, type=int)
    count = 0
    while count < quantity:
        new_part = Parts(desc_id=description_id)
        db.session.add(new_part)
        count += 1

    db.session.commit()
    return jsonify(f"You have successfully created {quantity} part {description_id}(s)"), 200


#View part
@parts_bp.route('/<int:part_id>', methods=['GET'])
def read_part(part_id):
    part = db.session.get(Parts, part_id)
    if not part:
        return jsonify({"message": "Part not found"}), 404
    return part_schema.jsonify(part), 200


#View all parts
@parts_bp.route('', methods=['GET'])
def read_parts():
    parts = db.session.query(Parts).all()
    return parts_schema.jsonify(parts), 200


#Delete part
@parts_bp.route('/<int:part_id>', methods=['DELETE'])
@limiter.limit("5 per hour")
def delete_part(part_id):
    part = db.session.get(Parts, part_id)
    if not part:
        return jsonify({"message": "Part not found"}), 404
    
    db.session.delete(part)
    db.session.commit()

    return jsonify({"message": f"Successfully deleted part {part_id}"}), 200


#Update part 
@parts_bp.route('/descriptions/<int:part_description_id>', methods=['PUT'])
@limiter.limit("10 per hour")
def update_part(part_description_id):
    part_desc = db.session.get(PartDescriptions, part_description_id)
    if not part_desc:
        return jsonify({"message": "Part not found"}), 404
    
    try:
        part_desc_data = part_description_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in part_desc_data.items():
        setattr(part_desc, key, value)

    db.session.commit()
    return part_description_schema.jsonify(part_desc), 200

#Create part description
@parts_bp.route('/descriptions', methods=['POST'])
@limiter.limit("10 per hour")
def create_part_description():
    try:
        data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        new_part_description = PartDescriptions(**data)
        db.session.add(new_part_description)
        db.session.commit()
    except:
        return jsonify({"message": "part description is already in inventory"})
    
    return part_description_schema.jsonify(new_part_description), 201


#View part description for a part
@parts_bp.route('/<int:part_id>/descriptions', methods=['GET'])
def read_part_description(part_id):
    part = db.session.get(Parts, part_id)
    if not part:
        return jsonify({"message": "Part not found"}), 404
    
    part_description = part.part_description
    return part_description_schema.jsonify(part_description), 200


#View all part descriptions
@parts_bp.route('/descriptions', methods=['GET'])
@cache.cached(timeout=60)
def read_part_descriptions():
    part_descriptions = db.session.query(PartDescriptions).all()
    return part_descriptions_schema.jsonify(part_descriptions), 200

#Delete part description
@parts_bp.route('/descriptions/<int:part_description_id>', methods=['DELETE'])
@limiter.limit("10 per hour")
def delete_part_description(part_description_id):
    part_description = db.session.get(PartDescriptions, part_description_id)
    db.session.delete(part_description)
    db.session.commit()

    return jsonify({"message": "Successfully deleted part description"})
