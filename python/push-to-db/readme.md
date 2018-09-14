# push-to-db

Le script python push-to-db.py est un élément du projet "La Maison Pythonic".

Ce script permet de stocker les messages du broker MQTT (Eclipse Mosquitto) directement dans une db SQLite3.

## Fichiers 
 * setup.sh : initialisation de la db et des différents fichiers nécessaires (log, config, ...). __Doit être lancé en sudo__.
 * inifile.sample : exemple de fichier push-to-db.ini (sera copié par setup.sh)
 * push-to-db.service.sample : exemple de fichier pour installation sous systemD.
 * createdb.sql : commande sql pour créer la base de donnée Sqlite3
 * push-to-db.py : capture les message MQTT et les sauve dans la DB (cfr fichier ini)

## Eléments clés
 * /etc/pythonic/push-to-db.ini - fichier de configuration du script
 * /var/local/sqlite/pythonic.db - base de donnée Sqlite3 (voir createdb.sql pour plus d'informations)

