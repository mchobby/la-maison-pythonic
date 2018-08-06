# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask


# Initialise l'application Flask
app = Flask( __name__ )

# La config par défaut ne log que les erreurs
app.logger.info( 'Objet app créé!' )

index_template =  """<!DOCTYPE html>
<html>
<body>
<h1>Logger demo</h1>
Un message d'erreur vient d'être envoyé vers le logger.
</body>
</html>""".decode('utf8') 

@app.route('/' )
def index():
   app.logger.error( 'Appel de /' )
   resp = app.jinja_env.from_string(index_template).render()
   return resp 
      
# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

