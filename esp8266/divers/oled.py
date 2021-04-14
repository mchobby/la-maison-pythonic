from machine import Pin, I2C
import time
import ssd1306

i2c = I2C( sda=Pin(23), scl=Pin(22) ) # ESP32
# i2c = I2C( sda=Pin(4), scl=Pin(5) ) # ESP8266

lcd = ssd1306.SSD1306_I2C( 128, 32, i2c )
lcd.fill(1) # Rempli l'écran en blanc
lcd.show()  # Afficher!
time.sleep( 2 )

# Remplis un rectangle en noir
# fill_rect( x, y, w, h, c ) 
lcd.fill_rect( 10,10, 20, 4, 0 )
lcd.show()  # Afficher!
time.sleep( 2 )

lcd.fill(0) # Rempli l'écran en noir
# Dessine un pixel en noir
# pixel( x, y, c ) 
lcd.pixel( 3, 4, 1 ) 
lcd.show()  # Afficher!
time.sleep( 2 )

lcd.fill(0) # Rempli l'écran en noir
# Dessine du texte en blanc.
#   text( str, x,y, c )
lcd.text("Bonjour!", 0,0, 1 )
lcd.show()  # Afficher!

