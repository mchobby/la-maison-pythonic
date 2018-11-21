# Mode Hors-ligne (Offline) 

Le projet La-maison-pythonic utilise quelques ressources téléchargées directement depuis Internet.

C'est entre autre le cas du projet Dashboard qui télécharge la font Matérialize, du code javascript de JQuery et MQTT Paho pour Javascript.

Il arrive parfois que le projet doivent fonctionner en vase clos sans aucune connexion Internet. Ce qui était entre autre le cas  du panneau de démonstration pour la MakerFair de Paris.

Il faut donc télécharger les éléments nécessaires et les stocker avec les ressources avec les données statiques du DashBoard. La raison même de la création du répertoire dashboard/app/static/offline-mode/ avec les différentes données téléchargées depuis Internet.

# Modification à effectuer

Toutes les modifications prennent place dans le template de base du projet (`base.html`). Vive l'héritage JinJa :-)

## Font Materialize

Editer le contenu du fichier `app/templates/base.html`

et remplacer

```
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
```

avec le contenu ci-dessous téléchargé directement depuis  https://fonts.gstatic.com/s/materialicons/v41/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2 contenu produit pour le navigateur FireFox (à voir s'il ne serait pas différent pour Chromium).

``` 
<style>
/* fallback */
@font-face {
  font-family: 'Material Icons';
  font-style: normal;
  font-weight: 400;
  src: url({{ url_for('static' ,filename='offline-mode/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2') }}) format('woff2');
}

.material-icons {
  font-family: 'Material Icons';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -moz-font-feature-settings: 'liga';
  -moz-osx-font-smoothing: grayscale;
}
</style>
```

Le fichier `flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2` doit être présent dans le répertoire `app/static/offline-mode/` 

## Javascript JQuery 

Modifier le contenu du fichier `app/templates/base.html`

Et remplacer

```
<script type="text/javascript" src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
```

avec 

```
<script type="text/javascript" src="{{ url_for('static' ,filename='offline-mode/jquery-3.2.1.min.js') }}"></script>
```

## JavaScript Paho Mqtt

Modifier le contenu du fichier `app/templates/base.html`

Et remplacer 

```
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.js" ></script>
```

avec

```
<script type="text/javascript" src="{{ url_for('static' ,filename='offline-mode/mqttws31.js') }}" ></script>
```

# Ajouter une horloge temps réel

Autre problème inhérent au fait de ne pas avoir une connexion Internet et de ne pas disposer de l'heure sur le Raspberry-Pi. C'est assez gênant quand ont sait que le logiciel stocke des données d'historique, Gloups!!!

Pour résoudre ce problème, il suffit d'ajouter un horloge temps réel comme la PiRTC - PCF8523

* [https://shop.mchobby.be/pi-extensions/1148-pirtc-pcf8523-real-time-clock-for-raspberry-pi-3232100011489-adafruit.html](PiRTC PCF8523)

Qu'il est très facile de configurer en suivant le tutoriel d'Adafruit ou la traduction sur le Wiki de MCHobby.

* [https://wiki.mchobby.be/index.php?title=RASP-PCF8523](Tutoriel traduit chez MC Hobby)
* [https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/overview](Tutoriel original d'Adafruit)

