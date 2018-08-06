# coding: utf8
from flask import Flask

app = Flask( __name__ )

template =  """<!DOCTYPE html>
<html>
<body>
<h1>demo</h1>
 {{ name }}
</body>
</html>""".decode('utf8') 

@app.route('/' )
def test():
   nom='demo'
   lst=[1,3,8,12]
   return app.jinja_env.from_string( template ).render( nom=nom, valeur=lst) 
  
# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

