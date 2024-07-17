import os
import logging
import pymysql.cursors

from dataclasses import dataclass
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("otel-python-app")


@dataclass
class MySQLConfig(object):
    def __init__(self):
        self.host = os.environ.get("MYSQL_HOST", "localhost")
        self.user = os.environ.get("MYSQL_USER", "hackweek")
        self.password = os.environ.get("MYSQL_PASSWORD", "password")
        self.db = os.environ.get("MYSQL_DB", "hackweek")
        self.port = 3306


@tracer.start_as_current_span("get-mysql-connection")
def get_mysql_connection(config: MySQLConfig) -> pymysql.Connection:
    try:
        return pymysql.connect(host=config.host,
                               user=config.user,
                               password=config.password,
                               db=config.db,
                               port=3306,
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        raise f'CONNECTION FAILED: {e}: {config.host}:{config.port}'


@tracer.start_as_current_span("mysql-status")
def mysql_status() -> dict:
    config = MySQLConfig()
    connection = get_mysql_connection(config)
    status = {
        "status": "OK",
        "host": config.host,
        "port": config.port,
        "user": config.user,
        "db": config.db,
    }
    if not connection.open:
        status['status'] = 'FAILED'

    return status


@tracer.start_as_current_span("populate-initial-data")
def populate_initial_data() -> [{}]:
    config = MySQLConfig()
    connection = get_mysql_connection(config)
    data = [
        {
            'email': 'alice@example.com',
            'firstName': 'Alice',
            'lastName': 'Smith'
        },
        {
            'email': 'bob@example.com',
            'firstName': 'Bob',
            'lastName': 'Jones'
        },
        {
            'email': 'charlie@example.com',
            'firstName': 'Charlie',
            'lastName': 'Brown'
        },
    ]
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS `users` ("
                       "id INT AUTO_INCREMENT PRIMARY KEY, "
                       "email VARCHAR(255) NOT NULL, "
                       "firstName VARCHAR(255) NOT NULL, "
                       "lastName VARCHAR(255) NOT NULL)")
        for user in data:
            cursor.execute("SELECT * FROM `users` WHERE email=%s", (user['email'],))
            result = cursor.fetchall()
            if len(result) > 0:
                continue
            else:
                cursor.execute("INSERT INTO `users` (email, firstName, lastName) VALUES (%s, %s, %s)",
                           (user['email'], user['firstName'], user['lastName']))
    connection.commit()
    connection.close()
    return data
