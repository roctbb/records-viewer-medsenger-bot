from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_compress import Compress

from managers import *
from infrastructure import *
from config import *

app = Flask(__name__)

CORS(app)
Compress(app)

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db.init_app(app)

migrate = Migrate(app, db)

contract_manager = ContractManager(medsenger_api, db)
category_groups_manager = CategoryGroupsManager(medsenger_api, db)

