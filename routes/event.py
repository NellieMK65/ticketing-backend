from flask_restful import Resource, reqparse
from models import Event, db

parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("description")
parser.add_argument("venue")
parser.add_argument("poster")
parser.add_argument("status")
parser.add_argument("category_id")
parser.add_argument("start_date")
parser.add_argument("end_date")


class EventResource(Resource):
    def post(self):
        data = parser.parse_args()

        event = Event(**data)

        db.session.add(event)

        db.session.commit()

        return {"message": "Event created successfully"}

    def get(self, id=None):
        if id is None:
            results = []

            events = Event.query.all()

            for event in events:
                results.append(
                    event.to_dict(rules=("-tickets.event", "-tickets.payments"))
                )

            return results

        event = Event.query.filter(Event.id == id).first()

        return event.to_dict(rules=("-tickets.event", "-tickets.payments"))
