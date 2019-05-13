#!/user/bin/env python

# catalog_server.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from catalog import Base, User, Category, Item

import json
