# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask

# Initialisze l'application Flask
app = Flask( __name__ )

# Definir une route pour capturer la requete /
# et produire la réponse avec la fonction 
# dit_bonjour()
@app.route('/')
def dit_bonjour():
   return 'Salut tout le monde!'

# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

