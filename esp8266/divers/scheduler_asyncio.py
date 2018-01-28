# coding: utf8
""" Utilisation de asyncio pour planifier des taches.

  Voir également asyncio et exemples
  https://github.com/peterhinch/micropython-async """

import uasyncio as asyncio

async def print_this( s, time_ms ):
    while True:
        await asyncio.sleep_ms( time_ms )
        print( s )

loop = asyncio.get_event_loop()
loop.create_task( print_this( "every sec", 1000 ) )
loop.create_task( print_this( "every 1.2sec", 1200 ) )

loop.run_forever()

#async def killer( sec ):
#    await asyncio.sleep( sec )
#
#loop.run_until_complete( killer( sec=25 ) )
#print( "Execution terminee")

loop.close()
