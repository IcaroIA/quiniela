import uuid
import datetime
from flask import session
from src.common.database import Database


class User(object):
    def __init__( self, email, name,  password, date, _id=None ):
        self.email = email
        self.name = name
        self.password = password
        self.date = date
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__( self ):
        return "User> {}".format(self.name)

    def json( self ):
        return {
            "name": self.name,
            "email": self.email,
            "_id": self._id,
            "password": self.password,
            "date" : self.date
        }

    @classmethod
    def get_by_email( cls, email ):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_name(cls, name):
        data = Database.find_one("users", {"name": name})
        if data is not None:
            return cls(**data)

    @staticmethod
    def is_login_valid(name, password):
        user = User.get_by_name(name)
        if user is not None:
            # Check the password
            return user.password == password
        return False

    @staticmethod
    def login( name ):
        # login_valid has already been called
        user = User.get_by_name(name)
        session['email'] = user.email

    @classmethod
    def register(cls, email, name, password, date):
        user = cls.get_by_name(name)
        if user is None:
            # User doesn't exist, so we can create it
            new_user = cls(email, name, password, date)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            # User exists :(
            return False

    def save_to_mongo( self ):
        Database.insert("users", self.json())

    @classmethod
    def get_users(cls):
        return [cls(**user) for user in Database.find(collection='users', query={})]