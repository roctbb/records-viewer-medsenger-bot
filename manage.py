from flask import Flask
from infrastructure import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_compress import Compress
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk

from config import *

if PRODUCTION:
    sentry_sdk.init(
        dsn=SENTRY,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0,
    )

app = Flask(__name__)

CORS(app)
Compress(app)

db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string

db.init_app(app)

migrate = Migrate(app, db)
