from machine import Pin
from time import sleep

# Led rouge sur la carte
led = Pin( 0, Pin.OUT )
# Eteindre LED (logique inversée)
led.value( 1 )

def blink( count = 3 ):
    # clignoter = changer 2x d état
    for i in range( count * 2 ):
        # changer etat de l entrée 
        led.value( 0 if led.value()==1 else 1 )
        sleep( 1 )
    # Eteindre la LED 
    led.value( 1 )

# exécution (pour un temps limité)
print( 'Blink x 10' )
blink( 10 )
print( 'C est fait' )
