import os
import json

from flask import Flask
from logging.config import dictConfig

from opentelemetry import metrics, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from .lib.redis import redis_status, RedisClient
from .lib.mysql import mysql_status, populate_initial_data
from .lib.users import UserController
from .lib.util import serialize_users

otel_service_name = os.environ.get("OTEL_SERVICE_NAME", "otel-python-app")
otel_otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", None)

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: otel_service_name
})

traceProvider = TracerProvider(resource=resource)
if otel_otlp_endpoint is None:
    processor = BatchSpanProcessor(ConsoleSpanExporter())
else:
    processor = BatchSpanProcessor(OTLPSpanExporter(f'{otel_otlp_endpoint}/v1/traces'))
traceProvider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(traceProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f'{otel_otlp_endpoint}/v1/traces')
)

meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(otel_service_name)

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


@app.route("/flush")
def flush_redis():
    r = RedisClient()
    r.delete_key('users')
    return {
        'status': 'OK',
    }


@app.route("/init")
def init_data():
    data = populate_initial_data()
    return json.dumps(data)

