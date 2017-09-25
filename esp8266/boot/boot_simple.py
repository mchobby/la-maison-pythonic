WIFI_SSID = "MY_WIFI_SSID"
WIFI_PASSWORD = "MY_PASSWORD"

def sta_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        # connecting to network...
        wlan.connect( WIFI_SSID, WIFI_PASSWORD )
        
        while not wlan.isconnected():
            pass

sta_connect()

import gc
#import webrepl
#webrepl.start()
gc.collect()
