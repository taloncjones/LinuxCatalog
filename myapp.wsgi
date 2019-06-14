#!/usr/bin/env python

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/LinuxCatalog/')

from LinuxCatalog import app as application
application.secret_key = 'super_secret_key'
