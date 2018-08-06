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
<h1>Affichage des variables spéciales</h1>
<h2>Variable g</h2>
{{ g }}
<ul>
{% for item in g %}
   <li>{{ item }}</li>
{% endfor %}
</ul>
test
<h2>Variable request</h2>
{{ request }}
<h2>variable session</h2>
{{ session }}
</body>
</html>""".decode('utf8') 

@app.route('/' )
def index():
   resp = app.jinja_env.from_string(index_template).render()
   return resp 
      
# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

