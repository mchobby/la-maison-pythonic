# coding: utf8
# Importer la bibliothèque Flask
from flask import Flask

# Initialisze l'application Flask
app = Flask( __name__ )

# Prise en charge des requêtes
from app import views
