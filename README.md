# Linux Server

This project is an extension of the Item Catalog project. This extends the other project
by requiring the student to configure a linux web server to do the following:
- Create a user _grader_ and add them to _sudo_ group
- Disable root login and modify SSH port (change 22 to 2200)
- Create and configure SSH key for user _grader_
- Configure UFW to block all ports besides SSH (2200), HTTP (80), HTTPS (443), NTP (123) and enable UFW
- Create Apache webserver and use WSGI app to host Item Catalog Project
- Create _catalog_ postgresql database and user
- Reconfigure Item Catalog Project to use postgresql instead of sqlite, and use _catalog_ database

## Linux Server IP: `165.227.63.244` SSH Port: `2200`
## URL: https://165.227.63.244/catalog
Note: Server has been configured to redirect HTTP requests to HTTPS, and '/' requests to '/catalog'

## Summary of changes:
### As Root:  
- Download updated package lists: `apt-get update`  
- Get updates: `apt-get upgrade`  
- Add user _grader_: `adduser grader`  and set password: `udacitygrader`
- Add user to _sudo_: `usermod -a -G sudo grader`  
- Modify `/etc/ssh/sshd_config`:
    - Change port number from 22 to 2200
    - Change root login from "yes" to "no"
- Restart SSH: `service ssh restart`
- Log out

### On local machine:
Generate ssh key files with `ssh-keygen` and transfer .pub file to server

### As Grader (`ssh grader@165.227.63.244 -p 2200`)
#### 1. Secure Linux Server
- Load ssh keys:
    ```
    mkdir .ssh
    touch .ssh/authorized_keys
    - Copy contents of .pub file to authorized_keys
    chmod 700 .ssh
    chmod 644 .ssh/authorized_keys
    ```   
- Modify `/etc/ssh/sshd_config`: Change PasswordAuthentication "yes" to "no"
- Restart SSH: `sudo service ssh restart`
- Configure UFW:
    ```
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 2200/tcp
    sudo ufw allow http
    sudo ufw allow https
    sudo ufw allow ntp
    sudo ufw enable
    sudo ufw status
    ```
    ##### Note: If using VPS provider, you may need to configure provider firewalls. In this case I needed to allow ports 80, 123, 443, and 2200.
- Configure local timezone to UTC with: `sudo dpkg-reconfigure tzdata`
#### 2. Start Configuring Web Server
- Install and configure Apache:
    ```
    sudo apt-get install apache2
    sudo apt-get install libapache2-mod-wsgi    # If using python3 use *-py3
    sudo a2enmod wsgi
    sudo service apache2 restart
    ```
- Install PostgreSQL: `sudo apt-get install postgresql`
- Create catalog database and user:
    ```
    sudo -u postgres psql   # Launch postgres as user psql
    create database catalog;
    create user catalog with password 'supersecret';
    alter role catalog with createdb
    grant all privileges on database catalog to catalog;
    ```
- Go to `/var/www`
- Create catalog directory with `sudo mkdir catalog` and enter directory
- Pull Project_Item_Catalog with `sudo git clone https://github.com/taloncjones/Project_Item_Catalog.git catalog`
    ##### Note: If updating to a different repository, update origin url with `sudo git remote set-url origin <url>`
- Rename `catalog_server.py` to `__init__.py`
- In all database update files (catalog_db.py, fakeitems.py, __init__.py) change:
    ```
    engine = create_engine("sqlite:///catalog.db")
    to
    engine = create_engine('postgresql://catalog:supersecret@localhost/catalog')
    ```
#### 3. Configure Apache
- Create Apache conf file `LinuxCatalog` to handle port 80 and 443 (HTTPS required to use Facebook Oauth)
    ```
    <VirtualHost *:80>
        ...
        Redirect / https://<server_ip>/
        ...
    </VirtualHost>
    
    <VirtualHost _default_:443>
        ...
        WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
        <Directory /var/www/FlaskApp/FlaskApp/>
            Order allow,deny
            Allow from all
        </Directory>
        ...
        SSLEngine on

        SSLCertificateFile      /etc/ssl/certs/apache-selfsigned.crt
        SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key
        
        <FilesMatch "\.(cgi|shtml|phtml|php)$">
                    SSLOptions +StdEnvVars
        </FilesMatch>
        <Directory /usr/lib/cgi-bin>
                    SSLOptions +StdEnvVars
        </Directory>
        ...
    ```
- Load conf file with: `sudo a2ensite LinuxCatalog`
- Create SSL key with:
    ```
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt
    ```
- Create SSL parameter conf file with:
    ```
    sudo nano /etc/apache2/conf-available/ssl-params.conf
    ```
    and paste the following:
    ```
    SSLCipherSuite EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH
    SSLProtocol All -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLHonorCipherOrder On
    # Disable preloading HSTS for now.  You can use the commented out header line that includes
    # the "preload" directive if you understand the implications.
    # Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    # Requires Apache >= 2.4
    SSLCompression off
    SSLUseStapling on
    SSLStaplingCache "shmcb:logs/stapling-cache(150000)"
    # Requires Apache >= 2.4.11
    SSLSessionTickets Off
    ```
- Enable changes with:
    ```
    sudo a2enmod ssl
    sudo a2enmod headers
    sudo a2enmod ssl-params
    ```
- Test configuration with: `sudo apache2ctl configtest`
- If the above step passes, restart Apache: `sudo service apache2 restart`
#### 4. Configure WSGI
- Go to `/var/www/catalog` and create myapp.wsgi with: `sudo nano myapp.wsgi`
- Paste the following:
    ```
    #!/usr/bin/env python

    import sys
    import logging
    logging.basicConfig(stream=sys.stderr)
    sys.path.insert(0,'/var/www/catalog/')
    
    from catalog import app as application
    application.secret_key = 'super_secret_key'
    ```
- Restart Apache with `sudo service apache2 restart`

## Resources
Running Flask application on Apache: [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

Configuring Apache to use SSL: [How To Create a Self-Signed SSL Certificate for Apache in Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-apache-in-ubuntu-18-04)


#
# Original Project_Item_Catalog README from here on:

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
