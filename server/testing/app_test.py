


from datetime import datetime
from app import app
from models import db, Message

class TestApp:
    '''Flask application in app.py'''

    with app.app_context():
        # Ensure clean test data
        messages_to_delete = Message.query.filter(
            Message.body == "Hello 👋"
        ).filter(Message.username == "Liza")

        for message in messages_to_delete:
            db.session.delete(message)

        db.session.commit()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(body="Hello 👋", username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            db.session.delete(hello_from_liza)
            db.session.commit()

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        '''returns a list of JSON objects for all messages in the database.'''
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            assert response.status_code == 200
            assert isinstance(response.json, list)

            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        '''creates a new message in the database.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={"body": "Hello 👋", "username": "Liza"}
            )

            assert response.status_code == 201
            h = Message.query.filter_by(body="Hello 👋").first()
            assert h is not None

            db.session.delete(h)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self):
        '''returns data for the newly created message as JSON.'''
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={"body": "Hello 👋", "username": "Liza"}
            )

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

            h = Message.query.filter_by(body="Hello 👋").first()
            assert h is not None

            db.session.delete(h)
            db.session.commit()

    def test_updates_body_of_message_in_database(self):
        '''updates the body of a message in the database.'''
        with app.app_context():
            m = Message.query.first()

            # Ensure there is a message to update
            if not m:
                m = Message(body="Initial Message", username="TestUser")
                db.session.add(m)
                db.session.commit()

            id = m.id
            original_body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={"body": "Goodbye 👋"}
            )

            assert response.status_code == 200
            g = Message.query.get(id)
            assert g.body == "Goodbye 👋"

            # Revert changes to maintain test consistency
            g.body = original_body
            db.session.add(g)
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        '''returns data for the updated message as JSON.'''
        with app.app_context():
            m = Message.query.first()

            if not m:
                m = Message(body="Initial Message", username="TestUser")
                db.session.add(m)
                db.session.commit()

            id = m.id
            original_body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={"body": "Goodbye 👋"}
            )

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Goodbye 👋"

            g = Message.query.get(id)
            g.body = original_body
            db.session.add(g)
            db.session.commit()

    def test_deletes_message_from_database(self):
        '''deletes the message from the database.'''
        with app.app_context():
            hello_from_liza = Message(body="Hello 👋", username="Liza")

            db.session.add(hello_from_liza)
            db.session.commit()

            response = app.test_client().delete(f'/messages/{hello_from_liza.id}')
            assert response.status_code == 200

            h = Message.query.get(hello_from_liza.id)
            assert h is None
