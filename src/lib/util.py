import json

from .users import User


def serialize_users(users: [User]) -> [dict]:
    if users is not None:
        return json.dumps([user.__serialize__() for user in users])
    return {}