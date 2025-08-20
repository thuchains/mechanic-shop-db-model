from app.extensions import limiter, cache
from flask import request, jsonify
from app.models import db, Service_tickets, Mechanics
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.mechanics.schemas import mechanics_schema
from .schemas import service_ticket_schema, service_tickets_schema
from marshmallow import ValidationError


#Create service ticket
@service_tickets_bp.route('', methods=['POST'])
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    print("------------- Translated Data ---------------")
    print(data)
    new_service_ticket = Service_tickets(**data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

#Add mechanic to service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
def add_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({
            "Message": f"Successfully added {mechanic.first_name} to service ticket",
            "Service ticket": service_ticket_schema.dump(service_ticket), #use dump when schema is adding just a piece of return message
            "Mechanics": mechanics_schema.dump(service_ticket.mechanics) 
        }), 200
    
    return jsonify("This mechanic is already assigned to this service ticket"), 400


#Remove mechanic to service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic in service_ticket.mechanics:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({
            "Message": f"Successfully removed {mechanic.first_name} from service ticket",
            "Service ticket": service_ticket_schema.dump(service_ticket), #use dump when schema is adding just a piece of return message
            "Mechanics": mechanics_schema.dump(service_ticket.mechanics) 
        }), 200
    
    return jsonify("This mechanic is not assigned to this service ticket"), 400


#View individual service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
def read_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    return service_ticket_schema.jsonify(service_ticket), 200

#View all service tickets
@service_tickets_bp.route('', methods=['GET'])
def read_service_tickets():
    service_tickets = db.session.query(Service_tickets).all()
    return service_tickets_schema.jsonify(service_tickets), 200

#Delete service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"Message": f"Successfully deleted service ticket {service_ticket_id}"}), 200


#Update service ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"Message": "Service ticket not found"}), 400
    try:
        service_ticket_data = service_ticket_schema.load()
    except ValidationError as e:
        return jsonify({"Message": e.messages}), 400
    
    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200









