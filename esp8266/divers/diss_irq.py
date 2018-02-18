# Exemple désactivation des interruptions
# durant le traitement d'une section critique.
#
# Dans cet exemple, la section critique se 
# réduit a une instruction d'addition.
#
# Durant la section critique, il n'y a plus de
# déclenchement d'interruption sur la broche 13
#
from machine import Pin
import machine
import time

def irq_handler():
	print( 'Pin 13 a la masse.')

p = machine.Pin( 13,  Pin.IN, Pin.PULL_UP )
p.irq( trigger=Pin.IRQ_RISING, handler=irq_handler )

i = 0

def test():
	global i
	# Debut de section critique
	state = machine.disable_irq()
	i = i +1
	machine.enable_irq( state )
	# Fin de section critique
	return i

for j in range( 100 ):
	print( test() )
	time.sleep( 0.200 )

print( "C est fini!")
