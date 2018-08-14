# Dashboard

Le script python run.py est un élément du projet "La Maison Pythonic".

Le Dashboard est une application Flask (application Web en Python).

Ce script permet de lire les messages stockés par push-to-db.py dans la DB pythonic.db (SQLite3).

Ce script utilise également la DB dashboard.db (SQLite3) pour stocker la configuration du dashboard.

## Fichiers 
 * install/setup.sh : initialisation de la db et des différents fichiers nécessaires (log, config, ...). __Doit être lancé en sudo__.
 * install/inifile.sample : exemple de fichier dashboard.ini (sera copié par setup.sh)
 * install/createdb.sql : commande sql pour créer la base de donnée Sqlite3 dashboard.db
 * run.py : capture les message MQTT et les sauve dans la DB (cfr fichier ini)

## Eléments clés
 * /etc/pythonic/dashboard.ini - fichier de configuration du projet
 * /var/local/sqlite/pythonic.db - base de donnée Sqlite3 (alimenté par push-to-db.py)
 * /var/local/sqlite/dashboard.db - base de donnée Sqlite3 (configuration du dashboard)

