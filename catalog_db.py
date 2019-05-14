#!/user/bin/env python

# catalog_db.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

# Create User object with id, username, picture, email, and password_hash
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    # Create hash of password and store
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    # Verify hash of supplied password with stored password hash
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # Create authorization token using random 32 bit secret key, with 10 minute (600s) lifetime
    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id': self.id })

    # Make static method so User entry does not have to exist to attempt token verification
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        # Token is valid and not expired, use 'id' extracted from token as user_id
        user_id = data['id']
        return user_id

# Create Category entry with id, name, user_id (from User), and table relationship (User)
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return info in JSON format when serialize is called
    @property
    def serialize(self):
        return {
            #JSON info here
        }

# Create Item entry with the following info and table relationships
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return info in JSON format when serialize is called
    @property
    def serialize(self):
        return {
            #JSON info here
        }

# Create database with name x. Change x to desired db name
engine = create_engine('sqlite:///x.db')


Base.metadata.create_all(engine)

