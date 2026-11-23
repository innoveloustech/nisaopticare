import os
import sys


sys.path.insert(0, os.path.dirname(__file__))
# sys.path.insert(0, '/home/innovelous/ecom') 


# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     message = 'It works!\n'
#     version = 'Python %s\n' % sys.version.split()[0]
#     response = '\n'.join([message, version])
#     return [response.encode()]


# Set the Django settings module (only needed if not already set)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecom.settings'

# Point to the WSGI application
from ecom.wsgi import application