from flask_app import create_app
from app.models import Customers, db
import unittest

class TestCustomers(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customers(email="tester@email.com", first_name="Jane", last_name="Doe", address="123 Fun St", phone="555-555-5555")


        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()

        self.client = self.app.test_client()


    def test_create_customer(self):
        customer_payload = {
            "email": "test@email.com",
            "phone": "222-222-2222",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Test Rd",
        }

        response = self.client.post('/customers', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['email'], "test@email.com")

    #Negative check
    def test_invalid_create(self):
        customer_payload = { #Missing first_name, which should be required
            "email": "test@email.com",
            "last_name": "Doe",
            "phone": "333-333-3333",
            "address": "123 Test Rd",
        }

        response = self.client.post('/customers', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json) #check that first_name is in the response json


    def test_nonunique_email(self):
        customer_payload = {
            "email": "tester@email.com",
            "phone": "222-222-2222",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Test Rd",
        }

        response = self.client.post('/customers', json=customer_payload)
        self.assertEqual(response.status_code, 400)


    def test_get_customers(self):

        response = self.client.get('/customers')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['first_name'], 'Jane')


    def test_delete(self):
        customer_id = 1

        response = self.client.delete(f"/customers/{customer_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted customer 1')


    def test_update(self):
        customer_id = 1
        update_payload = {
            "email": "new_email@email.com",
            "phone": "555-555-5555",
            "first_name": "Jane",
            "last_name": "Doe",
            "address": "123 Test Rd",
        }

        response = self.client.put(f'/customers/{customer_id}', json=update_payload) 
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json['email'], 'new_email@email.com')
   
   
    def test_search_customers(self):

        response = self.client.get('/customers/search')
        self.assertEqual(response.status_code, 200)