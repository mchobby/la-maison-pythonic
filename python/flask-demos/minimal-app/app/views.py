# coding: utf8
from app import app

# importer les autres éléments déclarés 
# dans /app/__init__py selon les besoins
#
# from app import db, babel

# importer les modèles pour accéder 
# aux données
#
from app.models import *

@app.route('/')
def dit_bonjour():
   # Récupération de PARAMS (config.py)
   p = app.config['PARAMS']
   return """<!doctype html>
<html>
<head>
  <title>Titre de la page</title>
</head>
<body>
  <h1>Dis bonjour!</h1><br />
  Bonjour tout le monde, je suis %s et j'ai %s ans!
</body>
</html>""" % (p['nom'],p['age'])

