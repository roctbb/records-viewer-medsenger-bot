import sentry_sdk

from medsenger_api import AgentApiClient
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_sqlalchemy import SQLAlchemy

from config import *

db = SQLAlchemy()

if PRODUCTION:
    sentry_sdk.init(
        dsn=SENTRY,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0,
    )


medsenger_api = AgentApiClient(APP_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, use_grpc=USE_GRPC, grpc_host=GRPC_HOST,
                               sentry_dsn=SENTRY)
