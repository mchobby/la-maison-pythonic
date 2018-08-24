# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask
from logging.config import dictConfig
import os.path

# Initialisze l'application Flask
app = Flask( __name__ )
configuration = None

CONFIG_FILE = '/etc/pythonic/dashboard.cfg'
if os.path.exists( CONFIG_FILE ):
	app.config.from_pyfile( CONFIG_FILE )
	print( 'config loaded from %s' % CONFIG_FILE)
	# Load configuration in memory
	import imp
	configuration = imp.load_source( 'configuration', CONFIG_FILE )
else:
	# Load the default file
	print( 'loading config from dashboard.cfg.default')
	# Apply configuration to Flask application
	app.config.from_pyfile( 'dashboard.cfg.default' )
	# Load the configuration in memory
	#    load relative to runapp.py
	import imp
	configuration = imp.load_source( 'configuration', 'app/dashboard.cfg.default' )

# Apply the logger configuration
dictConfig( configuration.logger_config )

# Prise en charge des requêtes
from app import views_demo
from app import views_history
from app import views_special
from app import views
from models import *
