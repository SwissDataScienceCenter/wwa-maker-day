from machine import Pin
from neopixel import NeoPixel
from time import sleep

ring = NeoPixel(Pin(2), 15)

# ring[0] = (10,0,0)

colors = [
    (255,0,0),
    (255,128,0),
    (255,255,0),
    (128,255,0),
    (0,255,0),
    (0,255,128),
    (0,255,255),
    (0,128,255),
    (0,0,255),
    (128,0,255),
    (255,0,255),
    (255,0,64)
]

for i, c in enumerate(colors):
    ring[i] = c
    
ring.write()

time = 0

while True:
    sleep(0.1)
    
    for i, c in enumerate(colors):
        ring[(i+time)%12] = (c[0]//4,c[1]//4,c[2]//4)
        
    ring.write()
    
    time += 1
