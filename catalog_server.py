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

# API functions

# User functions

# Category functions

# Item functions

# Login handling for FB/Google/Etc
