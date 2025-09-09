from app import create_app
from app.models import ServiceTickets, db, Mechanics, Parts, PartDescriptions
import unittest
from datetime import date

class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.service_ticket = ServiceTickets(customer_id=1, service_desc="oil change", price=120, vin="usa21hj35489fd84342j2", service_date=date(1900, 1, 1))
        

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.service_ticket)
            db.session.commit()

        self.client = self.app.test_client()


    def test_create_service_ticket(self):
        service_ticket_payload = {
            "customer_id": 1,
            "service_desc": "replace brake pads",
            "price": "200",
            "vin": "usa234j40499a893k932",
            "service_date": "1900-02-02",
        }

        response = self.client.post('/service_tickets', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_desc'], "replace brake pads")

    #Negative check
    def test_invalid_create(self):
        service_ticket_payload = { #Missing price, which should be required
            "customer_id": 1,
            "service_desc": "replace brake pads",
            "vin": "usa234j40499a893k932",
            "service_date": "1900-02-02",
        }

        response = self.client.post('/service_tickets', json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json) #check that first_name is in the response json


    def test_get_service_tickets(self):

        response = self.client.get('/service_tickets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], 'oil change')


    def test_delete(self):
        service_ticket_id = 1

        response = self.client.delete(f"/service_tickets/{service_ticket_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted service ticket 1')


    def test_update(self):
        service_ticket_id = 1
        update_payload = {
            "customer_id": 1,
            "service_desc": "replace brake pads",
            "price": "200",
            "vin": "usa21hj35489fd84342j2",
            "service_date": "1900-01-01",
        }

        response = self.client.put(f'/service_tickets/{service_ticket_id}', json=update_payload) 
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json['service_desc'], 'replace brake pads')
   
   
    def test_add_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanics(
            email = "test@email.com",
            password = "123",
            first_name = "John",
            last_name = "Doe",
            address = "123 Test Rd",
            salary = 100000
            )

            db.session.add(mechanic)
            db.session.commit()
            mechanic_id = mechanic.id

        service_ticket_id = 1


        response = self.client.put(f'/service_tickets/{service_ticket_id}/add-mechanic/{mechanic_id}') 
        self.assertEqual(response.status_code, 200) 


    def test_invalid_add_mechanic(self):
        mechanic_id = 2
        service_ticket_id = 1

        response = self.client.put(f'/service_tickets/{service_ticket_id}/add-mechanic/{mechanic_id}')
        self.assertEqual(response.status_code, 404)

    def test_remove_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanics(
            email = "test@email.com",
            password = "123",
            first_name = "John",
            last_name = "Doe",
            address = "123 Test Rd",
            salary = 100000
            )

            db.session.add(mechanic)
            db.session.commit()
            mechanic_id = mechanic.id
            service_ticket = db.session.query(ServiceTickets).first()
            service_ticket_id = service_ticket.id
            service_ticket.mechanics.append(mechanic)
            db.session.commit()

        response = self.client.put(f'/service_tickets/{service_ticket_id}/remove-mechanic/{mechanic_id}')
        self.assertEqual(response.status_code, 200)

    
    def test_invalid_remove_mechanic(self):
        mechanic_id = 2
        service_ticket_id = 1

        response = self.client.put(f'/service_tickets/{service_ticket_id}/remove-mechanic/{mechanic_id}')
        self.assertEqual(response.status_code, 400) #mechanic not assigned to this service ticket
        
    
    def test_add_part(self):
        service_ticket_id = 1
        with self.app.app_context():
            part_desc = PartDescriptions(
                part_name = "oil filter",
                price = 27.99
            )
            db.session.add(part_desc)
            db.session.commit()
            part_desc_id = part_desc.id

            part = Parts(
                desc_id = part_desc_id,
                ticket_id = None
            )
            db.session.add(part)
            db.session.commit()
            part_id = part.id
            

        response = self.client.put(f'/service_tickets/{service_ticket_id}/add-part/{part_desc_id}')
        self.assertEqual(response.status_code, 200)

    def test_invalid_add_part(self):
        service_ticket_id = 1
        part_desc_id = 2

        response = self.client.put(f'/service_tickets/{service_ticket_id}/add-part/{part_desc_id}')
        self.assertEqual(response.status_code, 404)


