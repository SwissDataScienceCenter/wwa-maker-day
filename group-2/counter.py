from machine import Pin
from time import sleep

onboardLED = Pin(25, Pin.OUT)
# bigLED = Pin(14, Pin.OUT)

red_button = Pin(2, Pin.IN, Pin.PULL_DOWN)
green_button = Pin(3, Pin.IN, Pin.PULL_DOWN)

segments = [Pin(13-x, Pin.OUT) for x in range(5)]
dips = [Pin(6-x, Pin.IN, Pin.PULL_DOWN) for x in range(5)]

counter = 0

while True:
    sleep(1)
    
    print("---")
    
    for i, dip in enumerate(dips):
        print(f"dip {i+1}: {dip.value()}")
