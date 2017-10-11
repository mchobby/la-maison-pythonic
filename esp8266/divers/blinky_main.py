from machine import Pin
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP ) 
if runapp.value() == 0:
    print( 'Arret application. RunApp=0' )
else:
    import blinky
    