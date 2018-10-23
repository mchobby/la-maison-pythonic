# La Maison Pythonic

![La Maison Pythonic](res/logo/la-maison-pythonic.png)

La Maison Pythonic, c'est un projet didactique accompagnant __le livre "(TODO)"__ et dont le but est 
* d'aborder la capture de données avec des objets Internet (ESP8266 sous MicroPython),  
* la transmission télémétrique avec Mosquitto MQTT, 
* le stockage en base de données (SQLite3 et Python), 
* le rendu sous forme de pages HTMLs avec Flask (Python). 

Le tout en utilisant un Raspberry-Pi comme élément central tout en respectant les limites de ses ressources.

# A propos du Livre 

Capturez des données télémétriques et réaliser des tableaux de bord WEB
* __Rasperry-Pi__ avec __MQTT__, __Flask__, __SQLite__, __Python__
* __ESP8266__ avec __MicroPython__, __montages__
* Pour les Makers, les développeurs, les curieux en électronique

![Python, Raspberry Pi et Flask - Capturez des données témétriques et réalisez des tableaux de board Web](res/logo/livre.png)

Ce livre s'adresse à toute personne qui souhaite découvrir comment __capturer des données télémétriques__ d'une maison (température, humidité, pression atmosphérique, luminosité) et les présenter dans une interface web sous forme de __tableaux de bord__. L'auteur s'appuie pour cela sur les possibilités offertes par le langage __Python__, le nano-ordinateur __Raspberry Pi__ et le framework __Flask__. Bien qu'appliqué au Raspberry Pi, le contenu du livre est suffisamment universel pour être exploité sur d'autres plateformes telles que des ordinateurs.

Pour tirer le meilleur profit de la lecture de ce livre, des notions de __programmation orientée objet__ et  quelques rudiments sur le langage Python et en __électronique__ sont nécessaires. Une première expérience avec le Raspberry Pi et est également souhaitée.

Les points technologiques du livre sont isolés et vulgarisés avant d'être intégrés dans un projet global qui sert de fil conducteur à la prise en main et l'exploitation des différentes technologies étudiées. L'auteur commence par présenter la __collecte de données__ à l'aide de composants basés sur un __microcontrôleur ESP8266__ programmé avec __MicroPython__. Il détaille ensuite la centralisation de ces données à l'aide d'un __broker MQTT__ fonctionnant sur un __Raspberry Pi__. Dans la suite du livre, le lecteur découvre comment une __base de données SQLite 3__ permet d'offrir un __stockage persistant__ des données et comment elle peut être exploitée par une __application Flask__ pour produire des __tableaux de bord sur mesure__.

À l'issue de ce livre, le lecteur disposera de bases solides pour créer sereinement une grande variété de solutions, plus ou moins sophistiquées, en fonction de ses besoins.

__Plus d'information sur le livre__ sur [le site de l'éditeur (Editions ENI)](https://www.editions-eni.fr/livre/python-raspberry-pi-et-flask-capturez-des-donnees-telemetriques-et-realisez-des-tableaux-de-bord-web-9782409016318)

__Le code source de ce GitHub correspondant au livre__ est disponible dans l'archive [la-maison-pythonic-(master-livre).zip](https://github.com/mchobby/la-maison-pythonic/raw/master/res/la-maison-pythonic-(master-livre).zip) . 

# Installation 

Voir [les notes d'installation rapide](res/install-rapide.md)

# Matériel 
Vous trouverez facilement nécessaire chez les distributeurs Adafruit. Voici une proposition de lien:
* {{pl|846|Feather ESP8266 Huzzah}} - plateforme certifiée distribuée dans le monde entier! 
* LED et Bouton, résistance pull-up et déparasitage logiciel
* {{pl|33|Potentiomètre}} sur l'entrée analogique
* {{pl|218|MCP23017}} pour ajouter des entrées sorties
* {{pl|362|ADS1115}} pour ajouter des entrées analogiques
* {{pl|59|TMP36}} pour mesurer la température (en analogique)
* {{pl|259|DS18B20}} (et {{pl|151|DS18B20 water-proof}}) mesure de température (numérique, OneWire)
* {{pl|61|Senseur PIR}} pour détecter les mouvements à proximité
* {{pl|911|Contact magnétique}} pour détecter l'ouverture d'une porte
* {{pl|708|DHT11}} (ou {{pl|219|DHT22}})pour la mesure d'humidité
* {{pl|932|AM2315}} senseur d'humidité et T° weather-proof.
* {{pl|86|Senseur à Effet Hall}} pour la détection de présence de champs magnétique.
* {{pl|238|TSL2561}} pour la mesure de luminosité
* {{pl|684|BME280}} pour la mesure de pression Atmosphérique, Température, Humidité
* {{pl|1118|BMP280}} pour la mesure de pression Atmosphérique et T°
* RELAIS {{pl|107|module Relais}} ou {{pl|507|Bi-Relais}} pour commander des appareils.
* {{pl|58|PHOTO-RESISTANCE}}

# Le projet en quelques images

Les deux images suivantes présentent les éléments principaux du projet. Tous les détails sont disponibles dans Livre.

![Eléments du projet](res/info/project-howto-0.png)

![Eléments du projet](res/info/project-howto-1.png)

Les tableaux de bords (projet "Dashboard", Python + Flask + Materialize)

![Tableaux de bords](res/info/dashboard-1.png)
![Tableaux de bords](res/info/dashboard-2.png)
![Tableaux de bords](res/info/dashboard-3.png)
![Tableaux de bords](res/info/dashboard-4.png)
![Tableaux de bords](res/info/dashboard-5.png)
