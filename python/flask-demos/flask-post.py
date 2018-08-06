# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask, Response, url_for, request

# Initialisze l'application Flask
app = Flask( __name__ )

# Definir une route pour capturer la requete 
# /message et produire la réponse avec la fonction 
# message()
@app.route('/message', methods=['GET', 'POST'] )
def message():
   if request.method == 'GET':
      return Response( """<!DOCTYPE html>
<html>
<body>
<h1>Saisir un message</h1>
 <form action="%s" method="post">
  Destinataire:<br>
  <input type="text" name="dest"><br>
  Message:<br>
  <input type="text" name="msg"><br>
  <input type="submit" value="Envoyer">
</form> 

</body>
</html>""".decode('utf8') % url_for('message') )

   if request.method == 'POST':
      donnee = request.form
      le_message = donnee['msg']
      le_destinataire = donnee['dest']
      # effectuer l'envoi
      # ...

      # renvoyer la réponse
      return Response( """<!DOCTYPE html>
<html>
<body>
<h1>Message envoyé</h1>
Le message "%s" à été envoyé à %s.
</body>
</html>""".decode('utf8') % (le_message, le_destinataire) )

# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

