# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask, abort

# Initialisze l'application Flask
app = Flask( __name__ )

@app.route('/')
def racine():
   return 'Appeler /mon-erreur avec id<100 ou id>=100'.decode('utf8')

@app.route('/mon-erreur/<int:id>')
def demo( id ):
	if id > 100:
		# Retourner une page d'erreur 400 
		abort(404) 
	else:
		return 'C est tout bon'

# Demarrer l'application sur le port 8085
app.run( debug=True, port=5000, host='0.0.0.0')

