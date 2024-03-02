import rp2
import time
from machine import Pin
import array
import _thread
import random

# R1, G1, B1, R2, G2, B2 pins
DATA_PIN_START = const(0)

# A, B, C, D, E pins
ROW_PIN_START = const(6)

CLOCK_PIN = const(11)

# Latch pin, output enable pin
LATCH_PIN_START = const(12)

# Frequency of the PIO state machines
FREQUENCY = const(40_000_000)

HUB_75_PANEL_WIDTH = const(64)
HUB_75_PANEL_HEIGHT = const(32)

NUM_PANELS = const(2)

# Each block has 24 bits, which is 4 pixels x 2 scanlines
BLOCKS_PER_ROW = const(NUM_PANELS * HUB_75_PANEL_WIDTH // 4)
NUM_ROWS = const(HUB_75_PANEL_HEIGHT // 2)

@rp2.asm_pio(
    out_shiftdir=1,
    autopull=True,
    pull_thresh=24,
    out_init=(
        rp2.PIO.OUT_HIGH,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_HIGH,
        rp2.PIO.OUT_HIGH,
        rp2.PIO.OUT_HIGH,
        rp2.PIO.OUT_HIGH,
    ),
    sideset_init=(rp2.PIO.OUT_LOW),
)
def data_hub75():
    out(pins, 6)
    nop().side(1)
    nop().side(0)
    out(pins, 6)
    nop().side(1)
    nop().side(0)
    out(pins, 6)
    nop().side(1)
    nop().side(0)
    out(pins, 6)
    nop().side(1)
    nop().side(0)


@rp2.asm_pio(
    out_shiftdir=1,
    autopull=False,
    out_init=(
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
        rp2.PIO.OUT_LOW,
    ),
    sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
)
def row_hub75():
    wrap_target()
    pull()

    nop().side(2)
    # note 3 as only three pins needed for 32x32 screen. This might be wrong. Might needs all five still
    out(pins, 5)[2]
    nop().side(3)  # this triggers the latch
    nop().side(2)  # this disables the latch
    nop().side(0)


# Setup state machines.
# ``sm_data`` is used to push pixel data onto a pair (2x) of scanlines
# and ``sm_row`` is used to control which rows (i.e. scanlines) are active.
def create_state_machines():
    sm_data = rp2.StateMachine(
        0,
        data_hub75,
        out_base=Pin(DATA_PIN_START),
        sideset_base=Pin(CLOCK_PIN),
        freq=FREQUENCY,
    )  
    sm_row = rp2.StateMachine(
        1,
        row_hub75,
        out_base=Pin(ROW_PIN_START),
        sideset_base=Pin(LATCH_PIN_START),
        freq=FREQUENCY,
    )
    return sm_data, sm_row

sm_data, sm_row = create_state_machines()

sm_row.active(1)
sm_data.active(1)

# Drawing counter for scanlines. Should stay in range [0, NUM_ROWS[.
counter = 0

# This is essentially a draw lock.
writing = False

# Double buffering: we should draw onto ``drawBuffer`` (with the draw lock active).
# When drawing is done, the two buffers are swapped and ``frameBuffer``
# is shown at least once.
drawBuffer = array.array("I")
frameBuffer = array.array("I")
for i in range(BLOCKS_PER_ROW * NUM_ROWS):
    drawBuffer.append(0)
    frameBuffer.append(0)

# There are HUB_75_PANEL_WIDTH x HUB_75_PANEL_HEIGHT 3-bit values for each panel.
# Pins r1g1b1 control scanlines 0-15 while pins r2g2b2 control scanlines 16-31
# We want to write 24-bits at a time so we can write out 4 pixels per scanline at a time
# 1st pixel 0th scanline would be the lowest bits (0-2)
# 1st pixel 16th scanline would be the next bits (3-5)
# 2nd pixel 0th scanline would be the next lowest bits (6-8)
# 2nd pixel 16th scanline would be the next lowest bits (9-11)
# continue this pattern to fill our 24-bits
# TODO: Validate and improve above explainer.


@micropython.viper
def set_pixel_raw(x: int, y: int, rgb: uint):

    bit_posn = (x % 4) * 6
    if y > 15:
        y = y - 17
        bit_posn += 3
    else:
        y = y - 1

    # a mystery but rows 0/16 need to use y = 15 to be drawn correctly
    if y == -1:
        y = 15

    index = y * BLOCKS_PER_ROW + int(x >> 2)
    val = uint(drawBuffer[index])

    drawBuffer[index] = val | uint(rgb << (bit_posn))


# Sets a pixel. Note that ``r``, ``g`` and ``b`` can only be 0 or 1.
def set_pixel(x: int, y: int, r: int, g: int, b: int):
    rgb = (r << 0) | (g << 1) | (b << 2)
    set_pixel_raw(x, y, rgb)


# p-shape
# should these really be stored as datapoints?
def p_draw(init_x, init_y, r, g, b):
    # line 10 pixels high
    for i in range(10):
        set_pixel(init_x, init_y + i, r, g, b)
    # line 4 pixesl across
    for i in range(4):
        set_pixel(init_x + i, init_y, r, g, b)
    for i in range(4):
        set_pixel(init_x + i, init_y + 4, r, g, b)
    for i in range(3):
        set_pixel(init_x + 4, init_y + i + 1, r, g, b)


def i_draw(init_x, init_y, r, g, b):
    for i in range(4):
        set_pixel(init_x, init_y + i + 2, r, g, b)
    set_pixel(init_x, init_y, r, g, b)


def c_draw(init_x, init_y, r, g, b):
    for i in range(4):
        set_pixel(init_x, init_y + i + 1, r, g, b)
    for i in range(3):
        set_pixel(init_x + 1 + i, init_y, r, g, b)
        set_pixel(init_x + 1 + i, init_y + 5, r, g, b)


def o_draw(init_x, init_y, r, g, b):
    for i in range(4):
        set_pixel(init_x, init_y + i + 1, r, g, b)
        set_pixel(init_x + 4, init_y + i + 1, r, g, b)
    for i in range(3):
        set_pixel(init_x + 1 + i, init_y, r, g, b)
        set_pixel(init_x + 1 + i, init_y + 5, r, g, b)


# Sets all pixels to black.
def clearBuffer():
    for i in range(NUM_ROWS * BLOCKS_PER_ROW):
        drawBuffer[i] = 0


text_y = 14
direction = 1


def draw_text():
    global text_y
    global direction
    global writing

    writing = True
    text_y = text_y + direction
    if text_y > 25:
        direction = -0.1
    if text_y < 5:
        direction = 0.1
    #     text_y = 14

    clearBuffer()

    p_draw(3, int(text_y) - 4, 1, 1, 1)
    i_draw(9, int(text_y), 1, 1, 0)
    c_draw(11, int(text_y), 0, 1, 1)
    o_draw(16, int(text_y), 1, 0, 1)

    writing = False


def draw_performance():
    global writing

    writing = True

    start = time.ticks_us()

    counter = random.randint(1, 7)

    clearBuffer()

    for j in range(32):
        for i in range(32):
            set_pixel_raw(i, j, 1 + counter % 6)
            counter += 1

    end = time.ticks_us()
    usecs = time.ticks_diff(end, start)
    print(usecs / 1000.0)

    writing = False


def draw_test_pattern():
    global writing

    writing = True

    clearBuffer()

    for i in range(0, 32):
        # draw random selection of rows/colums using all colors
        set_pixel(i, 31, 0, 0, 1)
        set_pixel(i, 0, 0, 1, 0)
        set_pixel(i, 16, 0, 1, 1)
        set_pixel(0, i, 1, 0, 0)
        set_pixel(5, i, 1, 0, 1)
        set_pixel(15, i, 1, 1, 0)
        set_pixel(25, i, 1, 1, 1)
        set_pixel(30, i, 1, 0, 0)

    writing = False


frog = [
    ["b", "b", "b", "b", "b", "g", "b", "b", "b", "b", "b", "b", "b"],
    ["b", "g", "b", "b", "g", "g", "g", "b", "b", "b", "b", "b", "b"],
    ["g", "g", "g", "b", "b", "g", "b", "b", "r", "g", "b", "b", "b"],
    ["b", "g", "b", "b", "b", "g", "b", "g", "g", "g", "g", "b", "b"],
    ["b", "g", "g", "g", "b", "g", "g", "g", "g", "g", "r", "b", "b"],
    ["b", "b", "b", "g", "b", "g", "g", "g", "g", "g", "b", "b", "b"],
    ["b", "b", "b", "g", "g", "g", "g", "g", "g", "b", "b", "b", "b"],
    ["b", "b", "b", "g", "g", "g", "g", "g", "g", "b", "b", "g", "b"],
    ["b", "b", "b", "b", "g", "g", "g", "b", "g", "g", "g", "g", "g"],
    ["b", "b", "b", "b", "b", "g", "g", "b", "b", "b", "b", "g", "b"],
    ["b", "b", "g", "g", "g", "g", "g", "g", "b", "b", "b", "b", "b"],
    ["b", "g", "g", "g", "b", "b", "b", "b", "b", "b", "b", "b", "b"],
    ["b", "b", "g", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b"],
]

text_y = 8
direction = 0.4

text_x = 12
direction_x = 0.4


def draw_frog():
    global writing
    global frog
    global text_y
    global direction
    global text_x
    global direction_x

    writing = True

    clearBuffer()

    text_y = text_y + direction
    if text_y > 19:
        direction = -0.4
    if text_y < 0:
        direction = 0.4

    text_x = text_x + direction_x
    if text_x > 115:
        direction_x = -0.4
    if text_x < 0:
        direction_x = 0.4

    for y, f_col in enumerate(frog):
        for x, c in enumerate(f_col):
            xx = int(text_x) + x
            yy = int(text_y) + y

            if c == "g":
                set_pixel(xx, yy, 0, 1, 0)
            if c == "r":
                set_pixel(xx, yy, 1, 0, 1)

    writing = False


# This is a draw loop. For each pair (2x) of scanlines, we put the ``counter`` value in
# the ``sm_row`` state machine's TX FIFO and then put each block of pixels into
# the ``sm_data`` state machine's TX FIFO.
# 
# TODO: We should consider "swapping" the roles of the main thread and the
# child thread here. That is, keep the main logic in the main thread and
# have a child thread take care of drawing pixels.
while True:
    sm_row.put(counter)

    # Write out 8 integers that hold 8 pixels worth of 3-bit RGB (two scanlines x four pixels)
    baseIndex = counter * BLOCKS_PER_ROW
    for i in range(BLOCKS_PER_ROW):
        val = frameBuffer[baseIndex + i]
        sm_data.put(val)

    counter += 1
    if counter > 15:
        counter = 0

        if not writing:
            # perform our double buffering
            frameBuffer, drawBuffer = drawBuffer, frameBuffer
            _thread.start_new_thread(draw_frog, ())
