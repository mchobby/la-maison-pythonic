# coding: utf-8
""" Souscription au topic "demo/#" sur le broker Eclipse Mosquitto.

    Utilise une autenthification login/mot-de-passe sur le broker
"""
import paho.mqtt.client as mqtt_client

# Configuration 
MQTT_BROKER = "pythonic.local"
MQTT_PORT   = 1883
KEEP_ALIVE  = 45 # interval en seconde

def on_log( client, userdata, level, buf ):
    print( "log: ",buf)

def on_connect( client, userdata, flags, rc ):
    print( "Connexion: code retour = %d" % rc )
    print( "Connexion: Statut = %s" % ("OK" if rc==0 else "échec") )


def on_message( client, userdata, message ):
    print( "Reception message MQTT..." )
    print( "Topic : %s" % message.topic )
    print( "Data  : %s" % message.payload )

# Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
client = mqtt_client.Client( client_id="client007" )

# Assignation des fonctions de rappel
client.on_message = on_message
client.on_connect = on_connect
#client.on_log = on_log 

# Connexion broker
client.username_pw_set( username="pusr103", password="21052017" )
client.connect( host=MQTT_BROKER, port=MQTT_PORT, keepalive=KEEP_ALIVE )
client.subscribe( "demo/#" )

# Envoi des messages
client.loop_forever()

