from flask_restful import Resource, reqparse
from models import Category, db

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True,help="Category name is required")

class CategoryResource(Resource):
    def post(self):
        data = parser.parse_args()

        # We check name is not taken
        exists = Category.query.filter(Category.name == data['name']).first()

        if exists is not None:
            return {"message": "Category exists"}, 422

        category = Category(**data)

        db.session.add(category)

        db.session.commit()

        return {"message": "Category created successfully"}, 201

    def get(self):
        results = []

        categories = Category.query.all()

        for category in categories:
            results.append(category.to_dict())

        return results


