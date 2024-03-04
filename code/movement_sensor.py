import pimoroni_i2c
import breakout_vl53l5cx
import time
import network

from machine import Pin
from neopixel import NeoPixel
from microdot import Microdot

# The VL53L5CX requires a firmware blob to start up.
# Make sure you upload "vl53l5cx_firmware.bin" via Thonny to the root of your filesystem
# You can find it here: https://github.com/ST-mirror/VL53L5CX_ULD_driver/blob/no-fw/lite/en/vl53l5cx_firmware.bin

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
PINS_PICO_EXPLORER = {"sda": 20, "scl": 21}

# Sensor startup time is proportional to i2c baudrate
# HOWEVER many sensors may not run at > 400KHz (400000)
i2c = pimoroni_i2c.PimoroniI2C(**PINS_BREAKOUT_GARDEN, baudrate=2_000_000)

print("Starting up sensor...")
t_sta = time.ticks_ms()
sensor = breakout_vl53l5cx.VL53L5CX(i2c)
t_end = time.ticks_ms()
print("Done in {}ms...".format(t_end - t_sta))

# Make sure to set resolution and other settings *before* you start ranging
sensor.set_resolution(breakout_vl53l5cx.RESOLUTION_8X8)
sensor.enable_motion_indicator(breakout_vl53l5cx.RESOLUTION_8X8)
sensor.set_motion_distance(400, 1400)
sensor.start_ranging()

def eu_norm(data):
    total = 0
    for i in data:
        total += i * i
    return total ** 0.5

def update_light(speed):
    vmin = 20
    vmax = 120
    step = (vmax - vmin) / 12
    if speed < vmin:
        speed = vmin
    if speed > vmax:
        speed = vmax
    ind = int((speed - vmin) // step)
    print(f"ind: {ind} speed:{speed}")
    return ind

def plot(data, rows, cols):
    head = '<head><script type="text/javascript">setInterval(()=>{window.location.reload()}, 1000)</script></head>'
    output = f"<html>{head}<body><div>"
    for i in range(rows):
        output += '<div style="display: flex">'
        for j in range(cols):
            ind = i*cols + j
            val = data[ind]
            output += f'<div style="background-color: rgb({val}, {val}, {val}); width: 60px; height: 60px"></div>'
        output += "</div>"
    output += "</div></body></html>"
    return output

def access_point(ssid, password = None):
    # start up network in access point mode  
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid)
    if password:
        wlan.config(password=password)
    else:    
        wlan.config(security=0) # disable password
    wlan.active(True)
    
    # mark access point file
    with open(".access-point-mode", "w") as f:
        f.write("True")
        
    return wlan

ring = NeoPixel(Pin(3), 12)
access_point("speed")
app = Microdot()

@app.route('/')
async def index(request):
    data = sensor.get_data()
    print(data.distance)
    return plot(data.distance, 8, 8), 200, {'Content-Type': 'text/html'}

@app.route("/test")
async def hello(request):
    return "hello"

app.run(port=5000, debug=True)

while True:
    if sensor.data_ready():
        # "data" is a namedtuple (attrtuple technically)
        # it includes average readings as "distance_avg" and "reflectance_avg"
        # plus a full 4x4 or 8x8 set of readings (as a 1d tuple) for both values.
        # Motion data is available in "motion_detection.motion"
        data = sensor.get_data()
        motion = data.motion_indicator.motion[0:16]
        speed = eu_norm(motion)
        ind = update_light(speed)
        for i in range(12):
            if i <= ind:
                ring[i]= (0, 40, 0)
            else:
                ring[i]= (0, 0, 0)
        ring.write()
        print(plot(data.distance, 8, 8))
