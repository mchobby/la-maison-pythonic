# Activer Mosquitto WebSocket  

Il est nécessaire d'activer le service WebSocket sur le broket MQTT Mosquitto 
pour pouvoir établir une connexion MQTT depuis du code Javascript à l'aide 
de [Eclipse Paho JavaScript Client](https://www.eclipse.org/paho/clients/js/) .

Suivre les indictions ci-dessous pour activer le WebSocket.

Enfin, après avoir chargé un Dashboard, il est possible de tester le broker MQTT
 depuis une Ardoise Javascript à l'aide du fichier d'exemple [JavascriptClientMqtt-WebSocket.js](/mchobby/la-maison-pythonic/blob/master/python/divers/JavascriptClientMqtt-WebSocket.js).

# Modification à effectuer

## Configuration Mosquitto

Editer le contenu du fichier `/etc/mosquitto/mosquitto.conf`

et ajouter le contenu suivant en fin de fichier:

```
port 1883
listener 9001
protocol websockets
```

## redémarrer les services

Redémarrer le service mosquitto pour actualiser la configuration.

```
sudo systemctl restart dashboard.service
```

Ensuite, redémarrer le service push-to-db car celui-ci à perdu toutes ses 
souscriptions MQTT durant le redémarrage du broker MQTT. 

```
sudo systemctl restart push-to-db.service
```

