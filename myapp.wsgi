#!/usr/bin/env python

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/LinuxCatalog/')

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello Udacity!'

    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

