import json

from flask import Flask
from logging.config import dictConfig

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from .lib.redis import redis_status
from .lib.mysql import mysql_status, populate_initial_data
from .lib.users import UserController
from .lib.util import serialize_users

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("otel-python-app")

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)


@app.route("/")
def index():
    return 'hello '


@app.route("/healthz")
def status():
    result = {
        "mysql": mysql_status(),
        "redis": redis_status()
    }
    return json.dumps(result)


@app.route("/users")
def get_users():
    ctlr = UserController(logger=app.logger, tracer=tracer)
    app.logger.info(f'Getting users from controller: {ctlr}')
    users = ctlr.get_users()
    app.logger.info(f'Getting users from controller: {users} ')
    return serialize_users(users)


@app.route("/init")
def init_data():
    data = populate_initial_data()
    return json.dumps(data)

