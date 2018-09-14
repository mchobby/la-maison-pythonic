/*!
 * La-Maison_Pythonic (https://github.com/mchobby/la-maison-pythonic)
 * Javascript Code for Blocks
 */

 block_config_templates = 
    { "switch:block_config_required" : true,
      "switch:template" :

		 {  "switch:info" : "switch contains the MQTT values corresponding to check / uncheck state of the checkbox. Used to initialize the checkbox",
		 	"switch:required": { 
		 		"check:required":"MARCHE" ,
		      	"uncheck:required":"ARRET"
		    },
		   
		    "action:info" : "describe the MQTT publication to perform when the checkbox is checked / unchecked by the user.",
		    "action:required": { 

                "checked:info" : "MQTT publication to perform when checkbox is checked by the user",
		    	"checked:required":  { 
		       	       "source:info"    : "Identification of MQTT Server (in the config file)",
		       	       "source:required": "mqtt_pythonic",
		       	        
		       	       "topic:info"    : "topic on wich the value must be published.",
		       	       "topic:required": "maison/cave/chaufferie/cmd",
		       	       
		       	       "message:info"     : "value to publish on the topic",
		       	       "message:required" : "MARCHE" 
		       	},
		       	 

		        "unchecked:required": {
		         	   "source:required": "mqtt_pythonic", 
		         	   "topic:required": "maison/cave/chaufferie/cmd", 
		         	   "message:required": "ARRET" }
		        },
		   
		    "watch:info" : "Indicates which MQTT topic to subscribe to be informed of changes",
		    "watch:optional" : 
		        { "source:required": "mqtt_pythonic", "topic:required": "maison/cave/chaufferie/etat" }
		 }
    };

 function check_block_config( block_type, block_config ){
 	// check the content of the block_config if configured as suited. 
 	//
 	// block_type in ['switch']
 	//
 	// Returns: Error message in case of problem -OR- undefined when it is all right
 	//
 	// TODO: use the "block_config_templates" here upper to check the structure 
 	//
 	if( block_config == undefined ){
 		return "Configuration block vide!"
 	}
 	if( block_config[block_type] == undefined ){
 		return block_type+" manquant!"
 	}

 	return undefined;
 }

 function get_mqtt( mqtt_source ){
 	// retreive the mqtt definition object
 	_dic = mqtt_sources[mqtt_source]
 	if( _dic == undefined ){
 		throw mqtt_source + ' is not defined into mqtt_sources.';
 		return
 	}

 	// Is the MQTT instance already created ?
 	_mqtt = _dic['_mqtt']
 	if ( _mqtt == undefined ){
 		// create the instance
 		_mqtt = new Paho.MQTT.Client( _dic['server'], Number(_dic['port']), "dashboard" );
 		console.log("connect MQTT for source "+mqtt_source );
 		console.debug( 'MQTT connexion details...' )
 		console.debug( _dic );
 		_mqtt.connect( {onSuccess:on_mqtt_connect, onFailure:on_mqtt_connect_fail, userName:_dic['username'], password:_dic['passwd'] } );
 		_dic['_mqtt'] = _mqtt;
 	}
 	// return the instance
    return _mqtt;
 }

 function on_mqtt_connect(){
   // Once a connection has been made, make a subscription and send a message.
   console.log("MQTT connected. on_mqtt_connect()");	
 }

 function on_mqtt_connect_fail( x,y ){
   console.error( "Fail to connect MQTT. on_mqtt_connect_fail()" );
   M.toast( {html:'Fail to connect MQTT',classes:'red', displayLength:8000 } );
 }
 
 function on_switch_change( event ){
 	var checkbox = event.target

 	console.debug( 'on_switch_change for '+checkbox.id+' getting '+ (checkbox.checked ? " CHECKED " : " unchecked ") );
    // Extract the block ID from "checkbox_switch_14"
    var _arr = checkbox.id.split('_');
    var block_id = _arr[ _arr.length-1 ];
    // retreive the corresponding block_config
    var block_config = block_configs[ block_id ];
    var err = check_block_config ( 'switch', block_config );
    if( err ){
    	M.toast( {html:'Erreur configuration block: '+err, classes:'red' } )
    	return
    }
    if( checkbox.checked ){
    	var _source = block_config.action.checked.source;
    	var _topic  = block_config.action.checked.topic;
    	var _msg    = block_config.action.checked.message;
    }
    else {
    	var _source = block_config.action.unchecked.source;
    	var _topic  = block_config.action.unchecked.topic;
    	var _msg    = block_config.action.unchecked.message;    	
    }
    
    // On 06/09/2017, Javascript Paho Mqtt Client rely on WebSocket 
    //    Mosquitto does support it by adding the following
    //    configuration to the /etc/mosquitto/mosquitto.conf
    //       port 1883
    //       listener 9001
    //       protocol websockets 
    //    Unfortunately, on this days, the libwebsockets 2.1.0 as
    //       uncompatibility with mosquitto 1.4 causing error message 
    //       " Error: AMQJS0011E Invalid state not connected. "
    //       Downgrading to libwebsockets 2.0.2 seems to solve the issue
    //       but that's not an easy work on a Raspberry Pi.
    //    The best would certainly to wait for libwebsockets 2.1.1 
    //       that fix the issue.
    //
    //    More information: https://github.com/eclipse/mosquitto/issues/336
    //
    //    Workaround: rely on the Flask APP to rely the MQTT Publish
    //    
    //var _client = get_mqtt( _source )
    //var message = new Paho.MQTT.Message( _msg );
    //message.destinationName = _topic;
    //_client.send(message);
    console.log( JSON.stringify( {source:_source,topic:_topic,_msg:_msg} ) );
    var jqxhr = $.ajax({url: '/MqttProxyPublish',
                        type: 'POST',
                        data: JSON.stringify( {source:_source,topic:_topic,msg:_msg} ),
                        contentType: 'application/json; charset=utf-8' })
	  .done(function(response, status, xhr) {
	    M.toast( {html: response, classes: 'green' } );
	  })
	  .fail(function(response, status, xhr) {
	    M.toast( {html: response.responseText, classes: 'red' } );
	    M.toast( {html:'Erreur ajax!', classes:'red'} ) ;
	  })
	  .always(function() {
	    console.debug( '' );
	  });
     
 }