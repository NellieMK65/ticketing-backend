from flask_restful import Resource, reqparse
from flask import request
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
            # Check if 'ids' query parameter is provided for batch fetching
            # Example: /events?ids=1,2,3 or /events?ids=[1,2,3]
            ids_param = request.args.get("ids")

            if ids_param:
                # Parse the ids parameter - supports both "1,2,3" and "[1,2,3]" formats
                ids_param = ids_param.strip("[]")
                event_ids = [int(id.strip()) for id in ids_param.split(",") if id.strip()]

                # Fetch only events matching the provided IDs
                events = Event.query.filter(Event.id.in_(event_ids)).all()
            else:
                # Fetch all events if no ids parameter provided
                events = Event.query.all()

            results = []
            for event in events:
                results.append(
                    event.to_dict(rules=("-tickets.event", "-tickets.payments"))
                )

            return results

        event = Event.query.filter(Event.id == id).first()

        return event.to_dict(rules=("-tickets.event", "-tickets.payments"))
