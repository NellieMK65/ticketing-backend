# flask restful
from flask_restful import Resource, reqparse
from models import User, db
import phonenumbers
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt


class UserResource(Resource):
    @jwt_required()
    def get(self):
        print("JWT", get_jwt())
        role = get_jwt()["role"]

        # if role != 'admin':
        #     return {"message": "Unauthorized request"}, 401

        data = User.query.all()

        result = []

        print(data)

        for user in data:
            # result.append(user.to_dict(rules=("-updated_at", "-created_at")))
            result.append(user.to_dict(only=("id", "name")))

        print(result)

        return result


signup_parser = reqparse.RequestParser()
signup_parser.add_argument(
    "name", required=True, type=str, help="User name is required"
)
signup_parser.add_argument(
    "phone", required=True, type=str, help="Phone number is required"
)
signup_parser.add_argument(
    "email", required=True, type=str, help="Email address is required"
)
signup_parser.add_argument(
    "password", required=True, type=str, help="Password is required"
)


"""
For security reasons, look into supporting the following
    1. Oauth
    2. 2fa (especially if using password auth)
    3. Passwordless auth -> provide an email where will a link that will automatically login in the user
    4. Rate limiting (i.e 3 attempts to login the disable the account temporarily)
"""


class UserSignup(Resource):
    def post(self):
        try:
            # validate on the route level
            data = signup_parser.parse_args()

            # check for unique columns
            email = User.query.filter(User.email == data["email"]).first()

            if email:
                return {"message": "Email already taken"}, 422

            phone = User.query.filter(User.phone == data["phone"]).first()

            if phone:
                return {"message": "Phone number already taken"}, 422

            pw_hash = generate_password_hash(data["password"]).decode("utf-8")

            # handover to sqlalchemy
            # user = User(
            #     name=data['name'],
            #     phone=data['phone'],
            #     email=data['email']
            # )

            # delete the plain text password
            del data["password"]

            # keyword arguments unpacking (short cut to what is btwn line 50 to 55)
            user = User(**data, password=pw_hash)

            db.session.add(user)
            db.session.commit()

            return {"message": "User created successfully"}, 201
        except phonenumbers.NumberParseException as e:
            return {"message": str(e), "error": "ValidationError"}, 422
        except ValueError as e:
            return {"message": str(e), "error": "ValueError"}, 422
        except IntegrityError as e:
            print(str(e))
            return {"message": "Missing Values", "error": "IntegrityError"}, 422


login_parser = reqparse.RequestParser()
login_parser.add_argument(
    "email", required=True, type=str, help="Email address is required"
)
login_parser.add_argument(
    "password", required=True, type=str, help="Password is required"
)


class LoginResource(Resource):
    def post(self):
        data = login_parser.parse_args()

        # 1. check if user with email exists
        exists = User.query.filter(User.email == data["email"]).first()

        if exists is None:
            return {"message": "Invalid email or password"}, 401

        # generate otp and send to provided email (should have a route that validates the sent otp)
        # use magic links (generate a random unique link and send it to the provided email), once the user clicks on the link, we log them in automatically

        # 2. validate the password
        is_valid_password = check_password_hash(exists.password, data["password"])

        if not is_valid_password:
            return {"message": "Invalid email or password"}, 401

        # 3. create a jwt access token
        access_token = create_access_token(
            identity=exists.id, additional_claims={"role": exists.role}
        )

        return {
            "message": "Login successful",
            "user": exists.to_dict(),
            "access_token": access_token,
        }
