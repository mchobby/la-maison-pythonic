// Inclusion du script
// <script type="text/javascript" 
//     src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.js" >
// </script>

// Créer un client MQTT
client = new Paho.MQTT.Client( "pythonic.local", 
                               9001, 
                               "Dashboard");

// Définir les fonctions de rappel
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// Connecter le client
client.connect({onSuccess:onConnect,
                userName:"pusr103", 
                password:"21052017" });

// Appelé quand le client se connecte
function onConnect() {
  console.log("onConnect");

  // Réaliser une souscription
  client.subscribe("maison/cave/chaufferie/etat");

  // Envoi d'un message
  message = new Paho.MQTT.Message("MARCHE");
  message.destinationName = "maison/cave/chaufferie/cmd";
  client.send(message);
}

// Appelé lors d'une perte de connexion
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
}

// Appelé lors de la réception d'un messahe
function onMessageArrived(message) {
  console.log("onMessageArrived:"+message.payloadString);
}
