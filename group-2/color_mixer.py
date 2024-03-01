from machine import ADC, Pin
from time import sleep
from neopixel import NeoPixel

grb_led_1 = NeoPixel(Pin(2), 1)
grb_led_2 = NeoPixel(Pin(5), 1)

slider = ADC(Pin(28))

while True:
    sleep(0.2)
    
    v = slider.read_u16()
    color = (255-int(v/(2**16)*255),0,int(v/(2**16)*255))
    grb_led_1.fill(color)
    grb_led_1.write()
