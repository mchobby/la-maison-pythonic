# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask, session, url_for, make_response, request, redirect

# Initialisze l'application Flask
app = Flask( __name__ )

app.config['SECRET_KEY'] = 'Ehu6|C|#Ei~IkdN~0@Dq=}((]^ddez#_Uozv0<D&N7=z}P^%c=XqI2&V2ic2c^L'

encoding_form_template =  """<!DOCTYPE html>
<html>
<body>
<h1>Session demo</h1>
 <form action="{{ url_for('setsession') }}" method="post">
  Nom variable de session:<br>
  <input type="text" name="nom"><br>
  Valeur variable:<br>
  <input type="text" name="valeur"><br>
  <input type="submit" value="Envoyer">
</form> 
<button onclick="window.location.href='{{ url_for('viewsession') }}'">Voir session Vars</button>
</body>
</html>""".decode('utf8') 

confirmation_template = """<!DOCTYPE html>
<html>
<body>
<h1>Variable session initialisée</h1>
Le cookie "{{ nom }}" est fixé à "{{ valeur }}".<br>
<button onclick="window.location.href='{{ url_for('setsession') }}'">Nouvelle Var.</button>
<button onclick="window.location.href='{{ url_for('viewsession') }}'">Voir session Vars</button>
</body>
</html>""".decode('utf8')

sessionvars_template = """<!DOCTYPE html>
<html>
<body>
<ul>
<h1>Liste des variables session</h1>
  {% for k,v in sessionlist.items() %}
  <li>{{ k }} : {{ v }} <a href="{{ url_for('removesession', name=k) }}"> enlever</a></li>
  {% endfor %}
</ul>
<button onclick="window.location.href='{{ url_for('setsession') }}'">Nouvelle Var.</button>
</body>
</html>""".decode('utf8')

@app.route('/', methods=['GET', 'POST'] )
def setsession():
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
      # SET session var
      session[nom]=valeur
      return app.jinja_env.from_string( confirmation_template ).render( nom=nom, valeur=valeur) 
      
@app.route('/sessionvars' )
def viewsession():
  resp = app.jinja_env.from_string(sessionvars_template).render(sessionlist=session)
  return resp 

@app.route('/sessionremove/<name>')
def removesession( name ):
  session.pop( name )
  return redirect( url_for('viewsession') )

# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

