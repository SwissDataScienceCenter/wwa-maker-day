# Imports
from machine import Pin
from neopixel import NeoPixel
import time

tickTime = 0.12

stripLedCount = 15
strand = NeoPixel(Pin(2), stripLedCount)

ringLedCount = 12
ring = NeoPixel(Pin(3), ringLedCount)


def clear_strand():
    strand.fill((0, 0, 0))
    strand.write()


def clear_ring():
    ring.fill((0, 0, 0))
    ring.write()


def clear_all():
    clear_strand()
    clear_ring()


# Turn off all LEDs before program start
clear_all()

time.sleep(1)

big_i = 0
while True:
    strandColor = [20, 20, 20]
    ringColor = [50, 50, 50]
    strandColor[big_i % 3] = 255
    ringColor[(big_i + 1) % 3] = 255

    for i in range(stripLedCount):
        strand[i] = strandColor
        strand.write()
        ring[i % ringLedCount] = ringColor
        ring.write()

        # Show the light for this long
        time.sleep(tickTime)
        clear_all()

    for i in reversed(range(stripLedCount)):
        strand[i] = strandColor
        strand.write()
        ring[i % ringLedCount] = ringColor
        ring.write()

        # Show the light for this long
        time.sleep(tickTime)

        # Clear the strand at the end of each loop
        clear_all()

    big_i += 1
