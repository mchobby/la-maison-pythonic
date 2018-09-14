# Guide d'installation Rapide

## Pré-requis


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

