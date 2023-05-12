from flask import Flask
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_compress import Compress

from config import *

app = Flask(__name__)

CORS(app)
Compress(app)

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db.init_app(app)

migrate = Migrate(app, db)
