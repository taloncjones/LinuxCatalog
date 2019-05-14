#!/user/bin/env python

# catalog_server.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from catalog_db import Base, User, Category, Item

import json, random, string, requests

app = Flask(__name__)

# Load in client id from client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog Project'

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Logged in decorator
def login_required(object):
    def is_logged_in():
        if 'user_id' not in login_session:
            return redirect(url_for('login'))
    return is_logged_in

###
# API functions
###

###
# User functions
###

# Create a new user with the username, email, and picture pulled from login_session
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(user).filter_by(email=login_session['email']).one()
    return user.id

# Get user info for supplied user_id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user.id).one()
    return user

# Get user id for supplied email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return none

###
# Category functions
###

# Read Category and Item tables for catalog home page
# Order items by descending item id for most recently added items
def showCatalog():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories, items=items)
    else:
        return render_template('catalog.html', categories=categories, items=items)

# Read Category and Item tables for category page
def showCategory(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).all()
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories, category=category, items=items)
    else:
        return render_template('catalog.html', categories=categories, category=category, items=items)

###
# Item functions
###


###
# Login handling for FB/Google/Etc
###
