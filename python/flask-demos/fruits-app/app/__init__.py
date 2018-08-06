# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask
from app.config import configuration
from logging.config import dictConfig

# Nouvelle config pour capturer 
# tous les niveaux de log
dictConfig( configuration )

# Initialisze l'application Flask
app = Flask( __name__ )

# Prise en charge des requêtes
from app import views
from app import models
