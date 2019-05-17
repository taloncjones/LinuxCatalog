#!/user/bin/env python

# catalog_server.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, abort
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from catalog_db import Base, User, Category, Item

from functools import wraps

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

###
# Log in handlers
###

# Logged in decorator
def login_required(object):
    @wraps(object)
    def is_logged_in():
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin'))
    return is_logged_in

# Login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

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
@app.route('/')
def goToCatalog():
    return redirect(url_for('showCatalog'))

@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories, items=items)
    else:
        return render_template('catalog.html', categories=categories, items=items)

# Read Category and Item tables for category page
# If route contains category_id (from course script or manual input), look up category name and redirect
@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def goToShowCategory(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        abort(404)
    return redirect(url_for('showCategory', category_name=category.name))

@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    categories = session.query(Category).all()
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except:
        abort(404)
    items = session.query(Item).filter_by(category_id=category.id).all()
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories, category=category, items=items)
    else:
        return render_template('catalog.html', categories=categories, category=category, items=items)

# New Category
@app.route('/catalog/new', methods=['GET', 'POST'])
#@login_required
def newCategory():
    if request.method == 'POST':
        name = request.form['name']
        try:
            category = session.query(Category).filter_by(name=name).one()
            flash('Category Already Exists!', 'error')
        except:
            newCategory = Category(name=name, user_id=login_session['user_id'])
            session.add(newCategory)
            flash('New Category %s Successfully Created!' % newCategory.name)
            session.commit()
        return redirect(url_for('showCategory'), category_name=name)
    else:
        return render_template('newCategory.html')

# Edit Category
# If route contains category_id (from course script or manual input), look up category name and redirect
@app.route('/catalog/<int:category_id>/edit')
def goToEditCategory(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        abort(404)
    return redirect(url_for('editCategory', category_name=category.name))

@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
#@login_required
def editCategory(category_name):
    try:
        editCategory = session.query(Category).filter_by(name=category_name).one()
    except:
        abort(404)
    if editCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            flash('Category Successfully Renamed: %s' % editCategory.name, 'success')
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editCategory.hmtl', category=editCategory)
    return

# Delete Category
# If route contains category_id (from course script or manual input), look up category name and redirect
@app.route('/catalog/<int:category_id>/delete')
def goToDeleteCategory(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        abort(404)
    return redirect(url_for('deleteCategory', category_name=category.name))

@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
#@login_required
def deleteCategory(category_name):
    try:
        deleteCategory = session.query(Category).filter_by(name=category_name).one()
    except:
        abort(404)
    if deleteCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    # Check if category is empty
    deleteCategoryItems = session.query(Item).filter_by(category_id=deleteCategory.id).all()
    if deleteCategoryItems:
        isEmpty = False
    else:
        isEmpty = True
    if request.method == 'POST':
        session.delete(deleteCategory)
        flash('Category %s Deleted!' % deleteCategory.name, 'success')
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.hmtl', category=deleteCategory, isEmpty=isEmpty)


###
# Item functions
###

# Read Item table for item page
## Show 'Edit' and 'Delete' buttons
def showItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicitem.html', item=item)
    else:
        return render_template('item.html', item=item, creator=creator)

# New Item

# Edit Item

# Delete Item


###
# Login handling for FB/Google/Etc
###


###
# Main function
###

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
