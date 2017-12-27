# coding: utf-8
""" Publication de donnée sur le topic "demo/#" du broker Eclipse Mosquitto.
 
    Utilise une autenthification login/mot-de-passe sur le broker
"""
import paho.mqtt.client as mqtt_client
from time import sleep

# Configuration 
MQTT_BROKER = "pythonic.local"
MQTT_PORT   = 1883
KEEP_ALIVE  = 45 # interval en seconde

def on_log( client, userdata, level, buf ):
    print( "log: ",buf)

client = mqtt_client.Client( client_id="client007" )

# Assignation des fonctions de rappel
#client.on_log = on_log 

# Connexion broker
client.username_pw_set( username="pusr103", password="21052017" )
client.connect( host=MQTT_BROKER, port=MQTT_PORT, keepalive=KEEP_ALIVE )

# traitement des message
for i in range(4):
    print( "Publication iteration %s" % i )
    r = client.publish( "demo/machin-chose", "message %s"%i )
    print( "  envoyé" if r[0] == 0 else "  echec" ) 
    sleep( 1 )
