# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask, Response, url_for, make_response, request

# Initialisze l'application Flask
app = Flask( __name__ )

encoding_form_template =  """<!DOCTYPE html>
<html>
<body>
<h1>Cookie demo</h1>
 <form action="{{ url_for('setcookie') }}" method="post">
  Nom cookie:<br>
  <input type="text" name="nom"><br>
  Valeur cookie:<br>
  <input type="text" name="valeur"><br>
  <input type="submit" value="Envoyer">
</form> 
<button onclick="window.location.href='{{ url_for('viewcookie') }}'">Voir Cookies</button>
</body>
</html>""".decode('utf8') 

confirmation_template = """<!DOCTYPE html>
<html>
<body>
<h1>Cookie initialisé</h1>
Le cookie "{{ nom }}" est fixé à "{{ valeur }}".<br>
<button onclick="window.location.href='{{ url_for('setcookie') }}'">Nouveau Cookie</button>
<button onclick="window.location.href='{{ url_for('viewcookie') }}'">Voir Cookies</button>
</body>
</html>""".decode('utf8')

cookies_template = """<!DOCTYPE html>
<html>
<body>
<ul>
<h1>Cookie list</h1>
  {% for k,v in cooklist.items() %}
  <li>{{ k }} : {{ v }}</li>
  {% endfor %}
</ul>
<button onclick="window.location.href='{{ url_for('setcookie') }}'">Nouveau Cookie</button>
</body>
</html>""".decode('utf8')

@app.route('/', methods=['GET', 'POST'] )
def setcookie():
   if request.method == 'GET':

      resp = app.jinja_env.from_string(encoding_form_template).render()
      return resp 

   if request.method == 'POST':
      donnee = request.form
      nom = donnee['nom']
      valeur = donnee['valeur']
      # effectuer l'envoi
      # ...

      # renvoyer la réponse
      # SET COOKIE
      resp = make_response( app.jinja_env.from_string( confirmation_template ).render( nom=nom, valeur=valeur) )
      resp.set_cookie( nom, valeur )
      return resp

@app.route('/cookies' )
def viewcookie():
  resp = app.jinja_env.from_string(cookies_template).render(cooklist=request.cookies)
  return resp 

# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

