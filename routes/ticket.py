from flask_restful import Resource, reqparse
from models import Ticket, db

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True, help="Ticket name is required")
parser.add_argument("price", type=int, required=True, help="Price is required")
parser.add_argument(
    "tickets_available", type=int, required=True, help="Provide tickets available"
)
parser.add_argument("event_id", type=int, required=True, help="Event is required")


class TicketResource(Resource):
    def post(self):
        data = parser.parse_args()

        # for a single event, we cannot have the same ticket name
        # so we add a check for that using both the name and event id
        exists = Ticket.query.filter_by(
            name=data["name"], event_id=data["event_id"]
        ).first()

        if exists is not None:
            return {"message": f"Ticket with name {data['name']} already exists"}, 422

        ticket = Ticket(**data)

        db.session.add(ticket)

        db.session.commit()

        return {"message": "Ticket created successfully"}, 201
