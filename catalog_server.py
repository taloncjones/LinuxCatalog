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

