# Project_Item_Catalog

Welcome to my implementation of the Item Catalog Database project from Udacity.
This program's intended purpose is to keep a database of Catalog Categories (e.g. sports, music), their respective 
items, and item details, while providing a user-friendly webpage to navigate the database. The main objectives of this
course were:
 - Allow the user to navigate a database of categories and items
 - Allow the user to log in via a third-party (e.g. Facebook)
 - Allow the user to add, edit, or remove categories
 - Allow the user to add, edit, or remove category items
 - Add API calls for: a list of categories, a specific category's items, a particular item
 - Display html pages in a user-friendly manner by adding css

While some files and code were based off of course supplied resources (e.g. FBconnect to handle Facebook logins),
all files and code were developed as part of this project. With the exception of fb_client_secrets.json
(you'll need to supply your own secrets) and client_secrets.json (Google login not implemented), everything is used for
the final project.

## Initialize the database with:
```python catalog_db.py```

## (Optional) Populate the database with values:
Note: Based off of another Udacity Item Catalog project with personal changes  
```python fakeitems.py```

## Run the web server with:
```python catalog_server.py```
#### Or to detach it:
```python catalog_server.py &```

## JSON
Responses can be requested from the following paths:
#### showCatalogJSON: (Lists all categories in the database)
```
/JSON/
or
/catalog/JSON/
```
#### showCategoryJSON: (Lists all items for category supplied by <category_x>)
```
/catalog/<category_x>/JSON/
or
/catalog/<category_x>/items/JSON/
```
Note: Because of getTableObject(), category_x can be either an int or string!
#### Item: (Lists details of a single menu item supplied by <item_id>)
```
/catalog/<category_x>/<item_x>/JSON/
or
/catalog/<category_x>/items/<item_x>/JSON/
```
Note: Because of getTableObject(), category_x and item_x can be either an int or string!

## Steps for dependencies:
```
## Install dependencies.
apt-get -qqy install make zip unzip postgresql

apt-get -qqy install python3 python3-pip
pip3 install --upgrade pip
pip3 install flask packaging oauth2client redis passlib flask-httpauth
pip3 install sqlalchemy flask-sqlalchemy psycopg2-binary bleach requests

apt-get -qqy install python python-pip
pip2 install --upgrade pip
pip2 install flask packaging oauth2client redis passlib flask-httpauth
pip2 install sqlalchemy flask-sqlalchemy psycopg2-binary bleach requests
```