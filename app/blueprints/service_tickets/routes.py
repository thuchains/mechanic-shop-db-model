from app.extensions import limiter, cache
from flask import request, jsonify
from app.models import db, ServiceTickets, Mechanics, Parts, PartDescriptions
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.mechanics.schemas import mechanics_schema
from .schemas import service_ticket_schema, service_tickets_schema
from app.blueprints.parts.schemas import part_schema, parts_schema
from marshmallow import ValidationError


#Create service ticket
@service_tickets_bp.route('', methods=['POST'])
@limiter.limit("20 per hour")
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    print("------------- Translated Data ---------------")
    print(data)
    new_service_ticket = ServiceTickets(**data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201


#Add mechanic to service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("10 per hour")
def add_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({
            "message": f"Successfully added {mechanic.first_name} to service ticket",
            "Service ticket": service_ticket_schema.dump(service_ticket), #use dump when schema is adding just a piece of return message
            "Mechanics": mechanics_schema.dump(service_ticket.mechanics) 
        }), 200
    
    return jsonify("This mechanic is already assigned to this service ticket"), 400


#Remove mechanic from service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("10 per hour")
def remove_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic in service_ticket.mechanics:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({
            "message": f"Successfully removed {mechanic.first_name} from service ticket",
            "Service ticket": service_ticket_schema.dump(service_ticket), #use dump when schema is adding just a piece of return message
            "Mechanics": mechanics_schema.dump(service_ticket.mechanics) 
        }), 200
    
    return jsonify("This mechanic is not assigned to this service ticket"), 400


#View individual service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
@limiter.limit("10 per hour")
def read_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTickets, service_ticket_id)
    return service_ticket_schema.jsonify(service_ticket), 200


#View all service tickets
@service_tickets_bp.route('', methods=['GET'])
def read_service_tickets():
    service_tickets = db.session.query(ServiceTickets).all()
    return service_tickets_schema.jsonify(service_tickets), 200


#Delete service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
@limiter.limit("2 per hour")
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"message": "Service ticket not found"}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted service ticket {service_ticket_id}"}), 200

#Update service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
@limiter.limit("15 per hour")
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"message": "Service ticket not found"}), 400
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200

#Add part in service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/add-part/<int:part_description_id>', methods=['PUT'])
def add_part(service_ticket_id, part_description_id):
    part = db.session.query(Parts).where(Parts.ticket_id==None, Parts.desc_id==part_description_id).first()

    if not part:
        return jsonify("Part out of stock"), 404
    
    part.ticket_id = service_ticket_id
    db.session.commit()
    return jsonify({
        "message": f"Successfully added {part.part_description.part_name} to service ticket {service_ticket_id}"
    })









