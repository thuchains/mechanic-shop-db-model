from app import create_app
from app.models import Mechanics, db
import unittest
from werkzeug.security import check_password_hash, generate_password_hash
from app.util.auth import encode_token

class TestMechanics(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanics(email="tester@email.com", password=generate_password_hash("123"), first_name="Jane", last_name="Doe", address="123 Fun St", salary=90000)


        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()

        self.token = encode_token(1)
        self.client = self.app.test_client()


    def test_create_mechanic(self):
        mechanic_payload = {
            "email": "test@email.com",
            "password": "123",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Test Rd",
            "salary": 100000
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['email'], "test@email.com")
        self.assertTrue(check_password_hash(response.json['password'], "123")) 

    #Negative check
    def test_invalid_create(self):
        mechanic_payload = { #Missing first_name, which should be required
            "email": "test@email.com",
            "password": "123",
            "last_name": "Doe",
            "address": "123 Test Rd",
            "salary": 100000
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json) #check that first_name is in the response json

    def test_nonunique_email(self):
        mechanic_payload = {
            "email": "tester@email.com",
            "password": "123",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Test Rd",
            "salary": 100000
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    # def test_get_mechanics(self):

    #     response = self.client.get('/mechanics')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json[0]['first_name', 'Jane'])

