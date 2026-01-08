# flask restful
from flask_restful import Resource, reqparse
from models import User, db
import phonenumbers
from sqlalchemy.exc import IntegrityError


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

signup_parser = reqparse.RequestParser()
signup_parser.add_argument("name", required=True, type=str, help="User name is required")
signup_parser.add_argument("phone", required=True, type=str, help="Phone number is required")
signup_parser.add_argument("email", required=True, type=str, help="Email address is required")

class UserSignup(Resource):
    def post(self):
        try:
            # validate on the route level
            data = signup_parser.parse_args()

            # check for unique columns
            email = User.query.filter(User.email == data['email']).first()

            if email:
                return {"message": "Email already taken"}, 422

            phone = User.query.filter(User.phone == data['phone']).first()

            if phone:
                return {"message": "Phone number already taken"}, 422

            # handover to sqlalchemy
            user = User(
                name=data['name'],
                phone=data['phone'],
                email=data['email']
            )

            db.session.add(user)
            db.session.commit()

            return {"message": "User created successfully"}, 201
        except phonenumbers.NumberParseException as e:
            return {"message": str(e), "error": "ValidationError"}, 422
        except ValueError as e:
            return {"message": str(e), "error": "ValueError" }, 422
        except IntegrityError as e:
            print(str(e))
            return {"message": "Missing Values", "error": "IntegrityError"}, 422
