import json
import logging
import time

from dataclasses import dataclass
from opentelemetry import trace

from .mysql import get_mysql_connection, MySQLConfig
from .redis import RedisClient

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("otel-python-app")


@dataclass
class User(object):
    id: int
    email: str
    firstName: str
    lastName: str

    @tracer.start_as_current_span("user-save")
    def save(self):
        mysql_con = get_mysql_connection(config=MySQLConfig())
        with tracer.start_as_current_span("save-user") as span:
            span.set_attribute("user.id", self.id)
            span.set_attribute("user.email", self.email)
            with mysql_con.cursor() as cursor:
                cursor.execute("UPDATE `users` SET email=%s, firstName=%s, lastName=%s WHERE id=%s",
                               (self.email, self.firstName, self.lastName, self.id))
            mysql_con.commit()
            mysql_con.close()
        span.end()

    def __serialize__(self):
        return {
            'id': self.id,
            'email': self.email,
            'firstName': self.firstName,
            'lastName': self.lastName
        }


class UserController(object):
    def __init__(self, logger: logging.Logger, tracer: trace.Tracer):
        self.users = []
        self.logger = logger
        self.tracer = tracer
        self.mysql = get_mysql_connection(config=MySQLConfig())
        self.redis = RedisClient()

    def add_user(self, user: User):
        self.users.append(user)

    @tracer.start_as_current_span("get-users-redis")
    def _get_users_redis(self) -> [User] or None:
        self.logger.debug(f'UserController._get_users_redis()')
        users = self.redis.get_dict(key='users')
        self.logger.debug(f'UserController._get_users_redis(): users: {users}')
        user_objects = []
        if len(users.keys()) != 0:
            for user in users:
                user_dict = json.loads(users[user])
                user_objects.append(User(**user_dict))
            self.logger.debug(f'UserController._get_users_redis(): user_objects: {user_objects}')
            return user_objects
        else:
            return None

    @tracer.start_as_current_span("get-users-mysql")
    def _get_users_mysql(self) -> [User] or None:
        users = []
        self.logger.debug(f'UserController._get_users_mysql()')
        # Simulate a slow query
        time.sleep(2)
        with self.mysql.cursor() as cursor:
            cursor.execute("SELECT * FROM `users`")
            result = cursor.fetchall()
        self.logger.debug(f'UserController._get_users_mysql() result: {result}')
        for row in result:
            users.append(User(id=row['id'], email=row['email'], firstName=row['firstName'], lastName=row['lastName']))
        return None if len(users) == 0 else users

    @tracer.start_as_current_span("set-users-redis")
    def _cache_users(self, users: [User]) -> None:
        user_dict = {}
        self.logger.debug(f'UserController._cache_users(): users: {users}')
        if users is not None:
            for user in users:
                user_dict[user.id] = json.dumps(user.__serialize__())
            self.logger.debug(f'UserController._cache_users(): user_dict: {user_dict}')
            self.redis.set_dict('users', user_dict)
        return None

    @tracer.start_as_current_span("get-users")
    def get_users(self) -> [User]:
        self.logger.debug(f'UserController.get_users()')
        cached_users = self._get_users_redis()
        self.logger.debug(f'UserController.get_users() cached_users: {cached_users}')
        if cached_users is None:
            users = self._get_users_mysql()
            self.logger.debug(f'UserController._get_users_mysql() users: {users}')
            self._cache_users(users)
        else:
            users = cached_users
        return users
