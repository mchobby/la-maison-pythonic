# Dashboard

Le Dashboard est une application Flask (application Web en Python).

![Tableau de bord du projet](../../res/info/dashboard-1.png)

Le Dashboard permet de lire les messages stockés par push-to-db.py dans la DB pythonic.db (SQLite3).

Ce script utilise également la DB dashboard.db (SQLite3) pour stocker la configuration de Dashboard.

## Fichiers 
 * install/setup.sh : initialisation de la db et des différents fichiers nécessaires (log, config, ...). __Doit être lancé en sudo__.
 * install/createdb.sql : commande sql pour créer la base de donnée Sqlite3 dashboard.db
 * install/dashboard.service.sample : exemple de fichier de démarrage pour SystemD.
 * install/demodb/ : exemple de base de données pré-chargée avec un ensemble de donnée.
 * runapp.py : démarre le serveur Flask. Accéder à la page racine avec http://pythonic.local:5000

## Eléments clés
 * /etc/pythonic/dashboard.cfg - fichier Python de configuration du projet (note: sinon charge le fichier dashboard.cfg.default)
 * /var/local/sqlite/pythonic.db - base de donnée Sqlite3 (alimenté par push-to-db.py)
 * /var/local/sqlite/dashboard.db - base de donnée Sqlite3 (configuration du dashboard)

