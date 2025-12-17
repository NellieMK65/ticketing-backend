from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

# provide database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'

# create a migration object to manage migrations
migrate = Migrate(app, db)

# link our db to the flask instance
db.init_app(app)
