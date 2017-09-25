WIFI_SSID = "MY_WIFI_SSID"
WIFI_PASSWORD = "MY_PASSWORD"

def sta_connect( timeout = None, disable_ap = False ):
    import network, time
    from machine import Pin
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        # connecting to network...
        wlan.connect( WIFI_SSID, WIFI_PASSWORD )
        
        # Skip connexion wait when RunApp=False to avoids REPL timeout
        # testing machine.reset_cause() is not reliable on Huzza ESP8266
        runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
        if runapp.value() == 0:
            print( "WLAN: no wait!")
        else:
            ctime = time.time()
            while not wlan.isconnected():
                if timeout and ((time.time()-ctime)>timeout):
                    print( "WLAN: timeout!" )
                    break
                else:
                    # print(".")
                    time.sleep( 0.500 )

    # Decommenter pour obtenir des infos
    # print('network config:', wlan.ifconfig())
    if wlan.isconnected() and disable_ap:
        ap = network.WLAN(network.AP_IF)
        if ap.active():
            ap.active(False)
            print( "AP disabled!" )

    return wlan.isconnected()

# Disable Access Point if connected as STATION
# Connexion timeout of 40 sec
if sta_connect( disable_ap=True, timeout=20 ):
    print( "WLAN: connected!" )

import gc
#import webrepl
#webrepl.start()
gc.collect()

