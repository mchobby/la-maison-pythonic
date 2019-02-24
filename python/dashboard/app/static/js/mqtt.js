/*!
 * La-Maison_Pythonic (https://github.com/mchobby/la-maison-pythonic)
 * Javascript Code for MQTT request
 */

// MQTT Connexion : make needed subscription 
function onMqttConnect( object ) {
  console.debug("onMqttConnect for " + object.invocationContext.mqttsource );
  subscribe_for_blocks( object.invocationContext.mqttsource, object.invocationContext.mqttclient );

  // Réaliser une souscription
  //client.subscribe("maison/cave/chaufferie/etat");

  // Envoi d'un message
  //message = new Paho.MQTT.Message("MARCHE");
  //message.destinationName = "maison/cave/chaufferie/cmd";
  //client.send(message);
}

function onMqttConnectFailure( x, y ){
   console.error( "Fail to connect MQTT. on_mqtt_connect_fail()" );
   M.toast( {html:'Fail to connect MQTT',classes:'red', displayLength:8000 } );
}

// MQTT Connexion Lost :
function onMqttConnectionLost(responseObject) {
  console.log( 'onMqttConnectionLost' );
  //console.log( responseObject );
  if (responseObject.errorCode !== 0) {
     console.debug("onMqttConnectionLost:"+responseObject.errorMessage);
     M.toast( {html:'MQTT Conn. lost: '+responseObject.errorMessage, classes:'red' } )
  }
}

// MQTT Message Arrived : Dispatch to block
function onMqttMessageArrived(message) {
  console.log("onMqttMessageArrived:"+message.payloadString+ ' for '+message.destinationName );
  //console.log(message);
  dispatch_message_to_blocks( message.destinationName, message.payloadString );
}

// ----------------------------------------------------------------------
//        UTILITIES
// ----------------------------------------------------------------------

//function get_mqtt( mqtt_source ){
 	 // retreive the mqtt client object
//}

// Connect all the mqtt_source (and register a 'client' in the objet
function connect_mqtt_sources( mqtt_sources ){
   for( let mqtt_source in mqtt_sources ){
         var client = new Paho.MQTT.Client( mqtt_sources[mqtt_source]['server'], 
                               9001,         // websocket is on this port, not the 1883 mentionned in the source
                               "Dashboard"); // The identification of MQTT client
         mqtt_sources[mqtt_source]['client'] = client;
         client.onConnectionLost = onMqttConnectionLost;
         client.onMessageArrived = onMqttMessageArrived;
         client.connect({onSuccess:onMqttConnect,
                onFailure:onMqttConnectFailure,
                userName:mqtt_sources[mqtt_source]['username'], 
                password: mqtt_sources[mqtt_source]['passwd'] ,
                invocationContext: {mqttsource:mqtt_source , mqttclient:client }
                });
   }
}

// Make all the subscription on MQTT client for a given MQTT source
function subscribe_for_blocks( mqtt_source, client ){
   console.debug( 'subscribing for MQTT client '+mqtt_source );
   // perform the subscription of all blocks having MQTT Clients
   for( let id in mqtt_required ){

      var config = block_configs[ id ]
      if( !config ) {
         // No configuration
      } else 
      if( config['watch'] && config['watch']['source'] && config['watch']['source'] == mqtt_source ){
         // watch for a Block ?
         console.log( 'register '+ config['watch']['topic'] +' for '+mqtt_source )
         client.subscribe( config['watch']['topic'] );
      }
   } 
}

// Dispatch the given message to the target block
function dispatch_message_to_blocks( topic, payload ){
   console.debug( 'dispatch_message_to_blocks' );
   // perform the subscription of all blocks having MQTT Clients
   for( let id in mqtt_required ){
      var config = block_configs[ id ]
      if( !config ) {
         // No configuration
      } else 
      if( config['watch'] && config['watch']['topic']  && config['watch']['topic'] == topic ){
         console.debug( 'dispatch to item id='+id );
         // OK: match a Block watch!
         // Now find wich component to notify
         var _item = _mqtt_notifiable.get_item( id );
         // Make the onmqttmessage() call
         try {
             if(!_item ){
                 throw new Error( 'Unable to find mqtt_notifiable item for id '+id );
             }
             if( _item.target.onmqttmessage == undefined ){
                 throw new Error( "no onmqttmessage() event defined on target "+id );
             }
             // Call the onmqttmessage() event on the target will expose
             // .target, .payload, .topic, .block_config_id
             _item.target.onmqttmessage( {target:_item.target, payload:payload, topic:topic, block_config_id:id } );
         }
         catch(err) {
               console.error( 'Exception on item '+id+' while calling onmqttmessage(): ' + err.message );
               M.toast( {html:'MQTT dispatch message error!', classes:'red'} ) ;
         }
       
                   
      }
   }  // end for
}
