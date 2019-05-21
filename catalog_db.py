#!/user/bin/env python

# catalog_db.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Create User object with id, username, picture, and email
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)

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
engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
