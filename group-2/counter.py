from machine import Pin
from time import sleep

onboardLED = Pin(25, Pin.OUT)
# bigLED = Pin(14, Pin.OUT)

red_button = Pin(2, Pin.IN, Pin.PULL_DOWN)
green_button = Pin(3, Pin.IN, Pin.PULL_DOWN)

segments = [Pin(13-x, Pin.OUT) for x in range(0, 5)]

counter = 0

while True:
    sleep(0.2)
    
    if green_button.value() == 1:
        counter += 1
        
    if red_button.value() == 1:
        counter -= 1
        
    if counter < 0:
        counter = 0
    if counter > 5:
        counter = 5
        
    for seg in segments[:counter]:
        seg.value(1)
    for seg in segments[counter:]:
        seg.value(0)
        
    print(counter)
