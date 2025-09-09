from app import create_app
from app.models import ServiceTickets, db, Parts, PartDescriptions
import unittest
from sqlalchemy import select


class TestParts(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.app.config.update(
            TESTING=True, 
            RATELIMIT_ENABLED=False,
            CACHE_TYPE="null")
        

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.part_desc = PartDescriptions(part_name = "K&N oil filter 271B", price = 27.99)
            db.session.add(self.part_desc)
            db.session.commit()
            self.part = Parts(desc_id=self.part_desc.id, ticket_id=None)
            db.session.add(self.part)
            db.session.commit()

        self.client = self.app.test_client()


    def test_create_part_desc(self):
        part_description_payload = {
            "part_name": "RedLine 10W-40 full synthetic oil, 1 gallon",
            "price": 74.99
        }

        response = self.client.post('/parts/descriptions', json=part_description_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], "RedLine 10W-40 full synthetic oil, 1 gallon")

    #Negative check
    def test_invalid_create(self):
        part_description_payload = { #Missing price which should be required
            "part_name": "RedLine 10W-40 full synthetic oil, 1 gallon",
        }

        response = self.client.post('/parts/descriptions', json=part_description_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json) #check that price is in the response json


    def test_create_part(self):
        with self.app.app_context():
            part_desc = PartDescriptions(
                part_name = "oil filter",
                price = 27.99
            )
            db.session.add(part_desc)
            db.session.commit()
            part_desc_id = part_desc.id
        part_payload = {
            "desc_id": part_desc_id,
            "ticket_id": 1
        }

        response = self.client.post(f'/parts/{part_desc_id}', json=part_payload)
        self.assertEqual(response.status_code, 201)


    #Negative check
    def test_invalid_create(self):
        part_payload = {
            "desc_id": 3, #part_desc doesn't exist/ is out of stock
            "ticket_id": 1
        }

        response = self.client.post('/parts/3', json=part_payload)
        self.assertEqual(response.status_code, 404)


    def test_get_part_desc(self):
        part_id = 1

        response = self.client.get(f'/parts/{part_id}/descriptions')
        self.assertEqual(response.status_code, 200)


    def test_get_part(self):

        response = self.client.get('/parts')
        self.assertEqual(response.status_code, 200)


    def test_delete_part_desc(self):
        with self.app.app_context():
            desc_id = db.session.scalar(select(PartDescriptions.id))
            db.session.query(Parts).filter(Parts.desc_id == desc_id).delete(synchronize_session=False)
            db.session.commit()

        response = self.client.delete(f'/parts/descriptions/{desc_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted part description')


    def test_delete_part_desc_blocked(self):
        part_desc_id = 1

        response = self.client.delete(f'/parts/descriptions/{part_desc_id}')
        self.assertEqual(response.status_code, 409)

    def test_delete_part(self):
        part_id = 1

        response = self.client.delete(f'/parts/{part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted part 1')
   
   
    def test_delete_part(self):
        part_id = 1

        response = self.client.delete(f'/parts/{part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted part 1')


    def test_update_part(self):
        part_desc_id = 1
        update_payload = {
            "part_name": "Belray 10W-40 full synthetic oil, 1 gallon",
            "price": 74.99
        }

        response = self.client.put(f'/parts/descriptions/{part_desc_id}', json=update_payload) 
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json['part_name'], 'Belray 10W-40 full synthetic oil, 1 gallon')
   

    