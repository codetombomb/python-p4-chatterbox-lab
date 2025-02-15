from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages_query = Message.query.all()
        messages_serialized = [message.to_dict() for message in messages_query]
        resp = make_response(
            messages_serialized,
            200
        )

        return resp
    elif request.method == 'POST':
        new_message = Message(
            body=request.json.get("body"),
            username=request.json.get("username")
        )

        db.session.add(new_message)
        db.session.commit()

        new_message_serialized = new_message.to_dict()
        # breakpoint()
        resp = make_response(
            new_message_serialized,
            201
        )

        resp.headers.add("Content-Type", "application/json")

        return resp

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message_query = Message.query.filter_by(id=id).first()
    if request.method == 'PATCH':
        for attr in request.json:
            setattr(message_query, attr, request.json.get(attr))
            db.session.add(message_query)
            db.session.commit()

            message_dict = message_query.to_dict()
            resp = make_response(
                message_dict,
                200
            )

            return resp
    elif request.method == 'DELETE':
        db.session.delete(message_query)
        db.session.commit()

        resp_body = {
            "delete_successful": True,
            "message": "Message deleted"
        }

        resp = make_response(
            resp_body,
            200
        )

        return resp

if __name__ == '__main__':
    app.run(port=5555)
