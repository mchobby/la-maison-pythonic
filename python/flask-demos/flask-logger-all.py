# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask
from logging.config import dictConfig
from logging import getLogger
import sys

# Lorsque qu'exécuté depuis la console avec Werzeug, les handlers
# stdout et wsgi affichent l'information sur la console
dictConfig({
    'version': 1,
    'formatters': {
		'default': {
        	'format': '[%(asctime)s] x %(levelname)s in %(module)s: %(message)s',
        },
		'appformatter' : {
        	'format': '[%(asctime)s] -(APP)- %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
		'wsgi': {
			'class': 'logging.StreamHandler',
			'stream': sys.stdout, 
            # sur version plus recente de Flask
            #
            # 'stream': 'ext://flask.logging.wsgi_errors_stream',
			'formatter': 'default'
		},
		'stdout': {
			'class': 'logging.StreamHandler',
			'stream': sys.stdout,
			'formatter': 'appformatter'
		}
	},
	'loggers' : {
	    'root': {
    		'level': 'DEBUG',
        	'handlers': ['wsgi']
    	},
    	'app': {
        	'level': 'DEBUG',
        	'handlers': ['stdout']
    	}
    }
})

# Initialise l'application Flask
app = Flask( __name__ )
app.logger.info( 'Log on root logger!' )
getLogger('app').info( 'Log on APP logger!' ) 

index_template =  """<!DOCTYPE html>
<html>
<body>
<h1>Logger demo</h1>
Un message d'erreur vient d'être envoyé vers le logger.
</body>
</html>""".decode('utf8') 

@app.route('/' )
def index():
   getLogger('app').error( 'Appel de /' )
   resp = app.jinja_env.from_string(index_template).render()
   return resp 
      
# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

