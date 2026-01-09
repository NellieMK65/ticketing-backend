from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from models import db
from routes.users import UserResource, UserSignup, LoginResource

app = Flask(__name__)

# link flask + flask-restful
api = Api(app)
# link flask + flask-bcrypt
bcrypt = Bcrypt(app)
# link flask + flask-jwt-extended
jwt = JWTManager(app)

# provide database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
# enable query logging
app.config["SQLALCHEMY_ECHO"] = True

# create a migration object to manage migrations
migrate = Migrate(app, db)

# link our db to the flask instance
db.init_app(app)

api.add_resource(UserResource, "/users")
api.add_resource(UserSignup, "/sign-up")
api.add_resource(LoginResource, "/login")
