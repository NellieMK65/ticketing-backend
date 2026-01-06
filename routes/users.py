# flask restful
from flask_restful import Resource
from models import User

class UserResource(Resource):
    def get(self):
        data = User.query.all()

        result = []

        print(data)

        for user in data:
            result.append(user.to_dict())

        print(result)

        return result
