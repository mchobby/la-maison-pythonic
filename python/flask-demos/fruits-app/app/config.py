# coding: utf8
import sys

# Modifier la config pour 
# Capturer tous les logs
configuration = {
    'version': 1,
    'formatters': {
		'default': {
        	'format': '[%(asctime)s] x %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
		'wsgi': {
			'class': 'logging.StreamHandler',
			'stream': sys.stdout, #'ext://flask.logging.wsgi_errors_stream',
			'formatter': 'default'
		}
	},
	'loggers' : {
	    'root': {
    		'level': 'DEBUG',
        	'handlers': ['wsgi']
    	}
    }
}