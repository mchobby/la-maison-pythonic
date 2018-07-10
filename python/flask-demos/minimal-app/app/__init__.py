# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask
from app import config

# Initialisze l'application Flask
app = Flask( __name__ )

# Conigurer Flask depuis config.py
# Ex: SECRET_KEY, LOGGER_NAME, DEBUG, TESTING, ... 
# et ajouter les autres définitions
app.config.from_object(config)

# Creation d'autre ressources
# - connexion DB via SqlAlchemy
# db = SQLAlchemy( app )
# - traduction avec Babel
# babel = Babel( app )

# Prise en charge des requêtes
from app import views

# Prise en charge des accès DB
from app import models



