# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask, request

# Initialisze l'application Flask
app = Flask( __name__ )

# Definir une route pour capturer la requete /param
@app.route('/param/<version_id>')
def montrer_parametre( version_id = -1):
   # retourne du contenu sous format texte
   return 'Le paramètre est %s'.decode('utf8') % version_id 

@app.route('/prendre-id/<element_id>')
@app.route('/prendre/<element_nom>')
def prend_element( element_id = None, element_nom = None):
   # traiter les cas d erreur
   if not( element_id or element_nom ):
       return 'bad request!', 400 
   
   # retourne du contenu sous format texte
   if element_id:
      return 'Le paramètre est numérique avec %s'.decode('utf8') % element_id
   else:
      return 'Le paramètre est textuel avec %s'.decode('utf8') % element_nom

# Utilisation structure plusieurs?nom=Mhoa&prenom=Champion
@app.route('/plusieurs')
def plusieurs():
   param_nom = request.args.get('nom')
   param_prenom = request.args.get('prenom')

   return "Test de plusieurs parametres." + \
          " Nom=%s et Prénom=%s".decode('utf8') % (param_nom, param_prenom)

# Plusieurs paramètres dans la route
@app.route('/plusieurs2/<nom>/<prenom>')
def plusieurs2(nom,prenom):
   return "2ième test parametres.".decode('utf8') + \
          " Nom=%s et Prénom=%s".decode('utf8') % (nom, prenom)

@app.route('/demo/<int:id>')
def montrer_demo( id ):
   # retourne du contenu sous format texte
   return 'Le paramètre entier demo est %s'.decode('utf8') % id 

@app.route('/demo/<string:id>')
def montrer_demo2( id ):
   # retourne du contenu sous format texte
   return 'Le paramètre string demo est %s'.decode('utf8') % id 


# Demarrer l'application sur le port 5000
app.run( debug=True, port=5000, host='0.0.0.0')

