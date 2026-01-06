# flask restful
from flask_restful import Resource
from models import User


class UserResource(Resource):
    def get(self):
        data = User.query.all()

        result = []

        print(data)

        for user in data:
            # result.append(user.to_dict(rules=("-updated_at", "-created_at")))
            result.append(user.to_dict(only=("id", "name")))

        print(result)

        return result
