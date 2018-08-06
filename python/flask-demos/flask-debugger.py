# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask

# Initialisze l'application Flask
app = Flask( __name__ )

@app.route('/')
def racine():
   return 'Appeler /kaboum pour créer une erreur!'.decode('utf8')

@app.route('/kaboum')
def kaboum():
	val1 = 10
	val2 = 0
	# Créer une erreur "division par 0" 
	return 'Résultat = %s'.decode('utf8') % (val1/val2)

# Demarrer l'application sur le port 8085
app.run( debug=True, port=5000, host='0.0.0.0')

