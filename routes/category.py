from flask_restful import Resource, reqparse
from sqlalchemy import func
from models import Category, Event, db

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True, help="Category name is required")


class CategoryResource(Resource):
    def post(self):
        data = parser.parse_args()

        # We check name is not taken
        exists = Category.query.filter(Category.name == data["name"]).first()

        if exists is not None:
            return {"message": "Category exists"}, 422

        category = Category(**data)

        db.session.add(category)

        db.session.commit()

        return {"message": "Category created successfully"}, 201

    def get(self):
        results = []

        categories = (
            db.session.query(Category, func.count(Event.id).label("event_count"))
            .outerjoin(Event)
            .group_by(Category.id)
            .all()
        )

        for category, count in categories:
            data = category.to_dict()
            data["event_count"] = count
            results.append(data)

        return results
