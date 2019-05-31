#!/user/bin/env python

# catalog_server.py for Udacity Course 4 Item Catalog project
# Created by Talon Jones

import httplib2
import json
import random
import requests
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, abort
from flask import session as login_session
from functools import wraps
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db import Base, User, Category, Item

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
# Checks if user is logged in. If not, redirect to showLogin page.
def login_required(object):
    @wraps(object)
    def is_logged_in(*args, **kwargs):
        try:
            login_session['user_id']
        except:
            return redirect(url_for('showLogin'))
        return object(*args, **kwargs)

    return is_logged_in


# Login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Disconnect 'page'.
# When user clicks 'Log Out', clears login_session info and redirects to catalog page.
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'alert alert-success')
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", 'alert alert-danger')
        return redirect(url_for('showCatalog'))


###
# API functions
###

@app.route('/JSON')
@app.route('/catalog/JSON')
def showCatalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<category_x>/JSON')
@app.route('/catalog/<category_x>/items/JSON')
def showCategoryJSON(category_x):
    category = getTableObject(Category, category_x)
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/<category_x>/<item_x>/JSON')
def showItemJSON(category_x, item_x):
    category = getTableObject(Category, category_x)
    item = getTableObject(Item, item_x, category.id)
    return jsonify(item=item.serialize)


###
# Table search function
###

# This function takes a table name and id_or_name variable (int or string) and looks up based on id or name
# If any of the look ups fail, 404 is returned
# Optional cat_id parameter, limits searches to category_id=cat_id in case of duplicate item names
def getTableObject(table, id_or_name, cat_id=''):
    if str(id_or_name).isdigit():
        # If int, look up based on id
        try:
            if cat_id:  # If cat_id is given
                object = session.query(table).filter_by(
                    id=id_or_name).filter_by(category_id=cat_id).one()
            else:  # Else
                object = session.query(table).filter_by(id=id_or_name).one()
        except:  # If try fails, exit with 404
            abort(404)
    else:
        # Must be string, look up based on name
        try:
            if cat_id:  # If cat_id is given
                object = session.query(table).filter_by(
                    name=id_or_name).filter_by(category_id=cat_id).one()
            else:  # Else
                object = session.query(table).filter_by(name=id_or_name).one()
        except:  # If try fails, exit with 404
            abort(404)
    return object


###
# User functions
###

# Create a new user with the username, email, and picture pulled from login_session
def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
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
        return None


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
    return render_template('catalog.html', categories=categories, items=items)


# Read Category and Item tables for category page
@app.route('/catalog/<category_x>')
@app.route('/catalog/<category_x>/items')
def showCategory(category_x):
    categories = session.query(Category).all()
    category = getTableObject(Category, category_x)
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('catalog.html', categories=categories, category=category, items=items)


# New Category
@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required  # Requires user to log in before proceeding to newCategory()
def newCategory():
    if request.method == 'POST':
        name = request.form['name']
        try:  # Looks for existing category matching 'name'
            category = session.query(Category).filter_by(name=name).one()
            # If found, flash message is given and redirect called
            flash('Category Already Exists!', 'alert alert-danger')
        except:  # If not found, except is triggered and object added
            newCategory = Category(name=name, user_id=login_session['user_id'])
            session.add(newCategory)
            session.commit()
            flash('New Category %s Successfully Created!' % newCategory.name, 'alert alert-success')
        return redirect(url_for('showCategory', category_x=name))
    else:
        categories = session.query(Category).all()
        return render_template('newCategory.html', categories=categories)


# Edit Category
@app.route('/catalog/<category_x>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_x):
    editCategory = getTableObject(Category, category_x)
    # If user is not creator
    if editCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        try:  # Look up for existing object
            category = getTableObject(Category, request.form['name'])
            flash('Category Already Exists!', 'alert alert-danger')
        except:  # If not found, make changes
            if request.form['name']:
                editCategory.name = request.form['name']
                session.add(editCategory)
                session.commit()
                flash('Category Successfully Renamed: %s' %
                      editCategory.name, 'alert alert-success')
        return redirect(url_for('showCategory', category_x=editCategory.name))
    else:
        categories = session.query(Category).all()
        return render_template('editCategory.html', categories=categories, category=editCategory)


# Delete Category
@app.route('/catalog/<category_x>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_x):
    deleteCategory = getTableObject(Category, category_x)
    if deleteCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    # Check if category is empty for render_template and delete all items for loop
    deleteCategoryItems = session.query(Item).filter_by(
        category_id=deleteCategory.id).all()
    if request.method == 'POST':
        session.delete(deleteCategory)
        for item in deleteCategoryItems:  # For any items in deleteCategory, delete
            session.delete(item)
        session.commit()
        flash('Category %s Deleted!' % deleteCategory.name, 'alert alert-success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.html', category=deleteCategory, items=deleteCategoryItems)


###
# Item functions
###

# Show Item page
@app.route('/catalog/<category_x>/<item_x>')
def showItem(category_x, item_x):
    category = getTableObject(Category, category_x)
    items = session.query(Item).filter_by(category_id=category.id).all()
    item = getTableObject(Item, item_x, category.id)
    creator = getTableObject(User, item.user_id)
    return render_template('item.html', category=category, items=items, item=item, creator=creator)


# New Item
@app.route('/catalog/<category_x>/new', methods=['GET', 'POST'])
@login_required
def newItem(category_x):
    category = getTableObject(Category, category_x)
    if request.method == 'POST':
        try:  # Look up item, if found trigger flash and redirect
            item = session.query(Item).filter_by(
                name=request.form['name']).filter_by(category_id=category.id).one()
            flash('Item Already Exists!', 'alert alert-danger')
        except:  # If not found, add item
            newItem = Item(
                name=request.form['name'],
                description=request.form['description'],
                category_id=category.id,
                user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('New Item %s  Successfully Created' % newItem.name, 'alert alert-success')
        return redirect(url_for('showItem', category_x=category.name, item_x=request.form['name']))
    else:
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('newItem.html', category=category, items=items)


# Edit Item
@app.route('/catalog/<category_x>/<item_x>/edit', methods=['GET', 'POST'])
@login_required
def editItem(category_x, item_x):
    category = getTableObject(Category, category_x)
    editItem = getTableObject(Item, item_x, category.id)
    if editItem.user_id != login_session['user_id']:  # If not creator
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        try:  # Duplicate item lookup
            item = session.query(Item).filter_by(name=request.form['name']).filter_by(
                category_id=request.form['category']).one()
            flash('Item Already Exists!', 'alert alert-danger')
        except:  # If not found
            if request.form['name']:
                editItem.name = request.form['name']
            if request.form['description']:
                editItem.description = request.form['description']
            if request.form['category']:
                editItem.category_id = request.form['category']
            session.add(editItem)
            session.commit()
            flash('Item Successfully Updated!', 'alert alert-success')
        return redirect(url_for('showItem', category_x=editItem.category.name, item_x=editItem.name))
    else:
        categories = session.query(Category).all()
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('editItem.html', categories=categories, category=category, items=items, item=editItem)


# Delete Item
@app.route('/catalog/<category_x>/<item_x>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(category_x, item_x):
    category = getTableObject(Category, category_x)
    deleteItem = getTableObject(Item, item_x, category.id)
    if deleteItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"
    if request.method == 'POST':  # Delete item and commit
        session.delete(deleteItem)
        session.commit()
        flash('Item %s Deleted!' % deleteItem.name, 'alert alert-success')
        return redirect(url_for('showCategory', category_x=category_x))
    else:
        items = session.query(Item).filter_by(category_id=category.id).all()
        return render_template('deleteItem.html', category=category, items=items, item=deleteItem)


###
# Login handling for FB/Google/Etc
###

# Facebook login handler
# Takes POST message sent via JS in login.html page, triggered when user clicks 'Log in with Facebook'
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'], 'alert alert-success')
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


###
# Main function
###

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
