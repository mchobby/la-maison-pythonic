# Guide d'installation Rapide

## Pré-requis

Installer le système d'exploitation sur le Raspberry-Pi avec les caratéristiques suivantes:
* Hostname: pythonic 
* Adresse IP: fixe sur 192.168.1.210)

## Installation partie 1

### Installer Mosquitto
`sudo apt-get install mosquitto mosquitto-clients`

Créer fichier passwd et  ajouter utilisateur Mosquitto pusr103

`sudo mosquitto_passwd -c /etc/mosquitto/passwd pusr103`

Le mot de passe utilisé durant la configuration du projet est __21052017__

### Modifier la configuration Mosquitto
`sudo nano /etc/mosquitto/mosquitto.conf`

Et y ajouter les lignes

```
allow_anonymous false 
password_file /etc/mosquitto/passwd 
```
Redémarrer Mosquitto
* `sudo systemctl stop mosquitto.service`
* `sudo systemctl start mosquitto.service`

## Récupération des sources

### La copie à l'édition du livre (sur GitHub)
Saisir la commande suivante pour récupérer l'archive
```
cd  ~
wget "https://github.com/mchobby/la-maison-pythonic/raw/master/res/la-maison-pythonic-(master-livre).zip"
```
Une fois l'archive téléchargée, les sources peuvent être extraites à l'aide de la commande

`unzip -e "la-maison-pythonic-(master-livre).zip"`

Une fois le contenu de l'archive extrait, le répertoire utilisateur doit contenir un répertoire __la-maison-pythonic__ avec les sources du projet.

Il sera probablement nécessaire de renommer le répertoire d'extraction afin qu'il dispose du nom correcte.

`mv la-maison-pythonic-master la-maison-pythonic`

### La copie avec block Switch (sur GitHub)
La copie à l'édition du livre ne contient pas le développement du block "Switch" et action `/MqttProxyPublish`. Ceux-ci fut complété en fin de chapitre 7, modification à saisir à la main.

Vous pouvez néamnoins télécharger cette archive intégrant les modifications et base de données de démonstration correspondate en saissisant la commande: 
```
cd  ~
wget "https://github.com/mchobby/la-maison-pythonic/raw/master/res/la-maison-pythonic-(Switch-MqttProxyPublish).zip"
```
Une fois l'archive téléchargée, les sources peuvent être extraites à l'aide de la commande

`unzip -e "la-maison-pythonic-(Switch-MqttProxyPublish).zip"`

Puis poursuivre le point précédent pour finaliser la mise en place.

### Depuis le GitHub du Projet ###

Le projet la-maison-pythonic est également disponible sur le dépôt GitHub. Ce dernier ayant continué ses évolutions depuis la sortie de l'ouvrage.

Le projet peut être dupliqué dans le répertoire utilisateur à l'aide des commandes.

```
cd  ~
git clone https://github.com/mchobby/la-maison-pythonic.git
```

Une fois l'opération terminée, le répertoire utilisateur doit contenir un répertoire __la-maison-pythonic__ avec les sources du projet.

## Installation suite

### Installer push-to-db
```
cd ~/la-maison-pythonic/python/push-to-db/
./setup.sh
sudo pip install paho-mqtt
```

_Il est possible que le script soit dans l'impossibilité de créer la base de donnée (voir message en fin de script). Cela est dût au fait que le script attache l'utilisateur pi à un nouveau groupe mais que cette modification ne soit instantanément effective. Par conséquent, il faut dé-loguer l'utilisateur pi puis re-loguer l'utilisateur pi avant de relancer le script une seconde fois._

### Tester push-to-db
Tester le script avec les commandes suivantes :
```
cd ~/la-maison-pythonic/python/push-to-db/
python push-to-db.py
```

Le script doit afficher différents messages au démarrage et à la réception de messages MQTT. Une fois le bon fonctionnement confirmé, presser CTRL+C pour interrompre le script Python.

### Démarrer push-to-db avec SystemD
Installer le fichier de configuration
```
sudo cp ~/la-maison-pythonic/python/push-to-db/push-to-db.service.sample /lib/systemd/system/push-to-db.service
sudo chmod 644 /lib/systemd/system/push-to-db.service
```

Recharger la configuration SystemD

`sudo systemctl daemon-reload`

Activer le service

```
sudo systemctl enable push-to-db.service
sudo systemctl start push-to-db.service
```

Vérifier que le service est bien démarré correctement.

`sudo systemctl status push-to-db.service`

### Installer le dashboard
```
cd ~/la-maison-pythonic/python/dashboard/install/
./setup.sh
```

### Copier les bases de données de démonstration
_Ce point est optionnel. Il peut être remplacé par la réinstallation des backups à disposition._
 
Arrêter le service push-to-db

`sudo systemctl stop push-to-db.service`

Copier les bases de données

```
cd ~/la-maison-pythonic/python/dashboard/install/
cd demodb
cp *.db /var/local/sqlite
```

Redémarrer le service push-to-db

`sudo systemctl start push-to-db.service`

### Démarrer dashboard avec SystemD
Installer le fichier de configuration
```
sudo cp ~/la-maison-pythonic/python/dashboard/install/dashboard.service.sample /lib/systemd/system/dashboard.service
sudo chmod 644 /lib/systemd/system/dashboard.service
```
Recharger la configuration SystemD

`sudo systemctl daemon-reload`

Activer le service

```
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

Vérifier que le service est bien démarré correctement.

`sudo systemctl status dashboard.service`

### Tester le dashboard
Pour tester le dashboard, il faut démarrer un navigateur internet puis saisir l'URL correspondant au Raspberry-pi.
 
Selon la configuration recommandée, les URLs possibles sont :

* [http://pythonic.local:5000](http://pythonic.local:5000) 
* [http://192.168.1.210:5000](http://192.168.1.210:5000)

