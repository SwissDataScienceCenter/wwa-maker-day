# Imports
from machine import Pin
from neopixel import NeoPixel
import time

tickTime = 0.09

stripLedCount = 15
strand = NeoPixel(Pin(2), stripLedCount)

ringLedCount = 12
ring = NeoPixel(Pin(3), ringLedCount)

# Turn off all LEDs before program start
ring.fill((0, 0, 0))
ring.write()
strand.fill((0, 0, 0))
strand.write()

strandColor = 255, 0, 0
ringColor = 0, 255, 0

time.sleep(1)


def clear_strand():
    strand.fill((0, 0, 0))
    strand.write()


def clear_ring():
    ring.fill((0, 0, 0))
    ring.write()


def clear_all():
    clear_strand()
    clear_ring()


while True:

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
