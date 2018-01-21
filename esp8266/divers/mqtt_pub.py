""" La Maison Pythonic - publication sur broker MQTT depuis MicroPython """ 
import time
from network import WLAN
from umqtt.simple import MQTTClient
from ubinascii import hexlify
import sys

CLIENT_ID = "demo-pub"

MQTT_SERVER = "192.168.1.210"

# Mettre a None si pas utile
MQTT_USER = 'pusr103'
MQTT_PSWD = '21052017'

print( "Creation MQTTClient")
q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )

if q.connect() != 0:
	print( "erreur connexion" )
	sys.exit()
print( "Connecté" )

# annonce connexion objet
sMac = hexlify( WLAN().config( 'mac' ) ).decode()
q.publish( "connect/%s" % CLIENT_ID , sMac )

# publication d'un compteur
for i in range( 10 ):
	print( "pub %s" % i )
	q.publish( "demo/compteur", str(i) )
	time.sleep( 1 ) 

q.disconnect()
print( "Fin de traitement" )
