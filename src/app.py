import json
import os
import redis
import pymysql.cursors


from flask import Flask

app = Flask(__name__)


@app.route("/")
def status():
    result = {
        "mysql": mysql_status(),
        "redis": redis_status()
    }
    return json.dumps(result)


def mysql_status():
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_user = os.environ.get("MYSQL_USER", "hackweek")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "password")
    mysql_db = os.environ.get("MYSQL_DB", "hackweek")
    mysql_port = os.environ.get("MYSQL_PORT", 3306)
    try:
        connection = pymysql.connect(host=mysql_host,
                                     user=mysql_user,
                                     password=mysql_password,
                                     db=mysql_db,
                                     port=mysql_port,
                                     cursorclass=pymysql.cursors.DictCursor)
        if connection.open:
            return {
                "status": "OK",
                "host": mysql_host,
                "port": mysql_port,
                "user": mysql_user,
                "db": mysql_db,
            }
    except Exception as e:
        return f'CONNECTION FAILED: {e}'


def redis_status():
    s = {
        "status": "OK"
    }
    try:
        if os.environ.get("REDIS_URL", None) is not None:
            r = redis.from_url(url=os.environ["REDIS_URL"])
            s["url"] = os.environ.get("REDIS_URL")

        elif os.environ.get("REDIS_HOST", None) is not None:
            r = redis.Redis(host=os.environ["REDIS_HOST"],
                            port=os.environ.get("REDIS_PORT", 6379),
                            db=os.environ.get("REDIS_DB", 0))
            s["host"] = os.environ.get("REDIS_HOST")
            s["port"] = os.environ.get("REDIS_PORT")
        else:
            return "REDIS_URL or REDIS_HOST is not set"

        if r.ping():
            return s
    except Exception as e:
        return f'CONNECTION FAILED: {e}'
