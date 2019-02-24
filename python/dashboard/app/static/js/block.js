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

// List of Mqtt Notifiable component.
// Component must expose a onmqttmessage( event ) see mqtt.js::dispatch_message_to_blocks() for 
// more information.
const MqttNotifiable = {
    _list : [],
    append : function( aTarget, aBlockConfigId ){
          this._list.push( {target:aTarget, id: aBlockConfigId} ); 
       },
    
    get_item : function( aBlockConfigId ){       
         for( let idx in this._list ){
             if( this._list[idx].id == aBlockConfigId ){
                return this._list[idx];
             }
         }
         return undefined;
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

function block_config_id_from_id( id ){
    // Extract the block_config index identification (string, eg: '11') 
    // from the DOM component id (eg: checkbox_switch_11) 
    var idx = id.lastIndexOf('_');
    if( idx < 0 ){
        return undefined;
    } 
    var _r = id.substring( idx+1 )
    // result must also been a valid integer (parseInt may strip incorrect char)
    if( parseInt( _r ) == NaN ) {
        return undefined;
    }
    // return the result as a string
    return String(parseInt(_r));
}

// --------------------------------------------------------------------------
//                  BLOCK MANAGEMENT FUNCTIONS
// --------------------------------------------------------------------------

function on_switch_mqtt_message( event ){
   console.debug( 'on_switch_mqtt_message '+event );
   // Find the <p id="11_footer"> and update it
   $('[id^="'+event.block_config_id+'_footer"]')[0].innerText = event.payload;
   $('[id^="'+event.block_config_id+'_rectime_footer"]')[0].innerText = '---'; 
   
   // Find the checkbox and states definition 
   var _checkbox = $('[id^="checkbox_switch_'+event.block_config_id+'"]')[0]
   var _blockconfig = block_configs[event.block_config_id]
   var _checked_value = undefined
   var _unchecked_value = undefined
   if( _blockconfig.switch && _blockconfig.switch.check ){
       _checked_value =  _blockconfig.switch.check;
   }
   if( _blockconfig.switch && _blockconfig.switch.uncheck ){
       _unchecked_value =  _blockconfig.switch.uncheck;
   }

   // IF the value does not fit the state of the checkbox THEN fix it!
   if( (event.payload == _checked_value) && !(_checkbox.checked) ){
      // check the input
      _checkbox.checked = true;
   }
   if( (event.payload == _unchecked_value) && (_checkbox.checked) ){
      // uncheck the input
      _checkbox.checked = false;
   }
} 

function on_switch_change( event ){
 	var checkbox = event.target

 	console.debug( 'on_switch_change for '+checkbox.id+' getting '+ (checkbox.checked ? " CHECKED " : " unchecked ") );
  // Extract the block ID from "checkbox_switch_14"
  //var _arr = checkbox.id.split('_');
  var block_id = block_config_id_from_id( checkbox.id ) //_arr[ _arr.length-1 ];
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
    
  var _client = mqtt_sources[ _source ].client
  var message = new Paho.MQTT.Message( _msg );
  message.destinationName = _topic;
  try {
      _client.send(message);
      M.toast( {html: _msg+' sent!', classes:'green'} ) ;     
  }
  catch( err ){
      M.toast( {html: 'MQTT Send error! '+err.message, classes:'red'} ) ;
  }
}

//
// Former version using Ajax call to /MqttProxyPublish 
//
/*  
function on_switch_change_xhr( event ){
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
*/ 
