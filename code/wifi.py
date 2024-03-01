#
# Convenience functions to connect to WiFi with the PicoW
#

import network
import json
import os
from time import sleep


def credentials(path="wlan-credentials.json"):
    try:
        with open(path, "r") as f:
            creds = json.load(f)
    except OSError:        
        creds = {"ssid": "", "password": ""}
    return creds

def connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 5
    while max_wait > 0:
        if wlan.status() == network.STAT_GOT_IP:
            break
        max_wait -= 1
        print('waiting for connection...')
        sleep(1)
    
    if wlan.status() != network.STAT_GOT_IP:
        raise RuntimeError("Unable to connect to network")

    print(wlan.ifconfig())

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

def get_ip():
    if is_access_point():
        mode = network.AP_IF
    else:
        mode = network.STA_IF
    return network.WLAN(mode).ifconfig()[0]

def is_access_point():
    try:
        os.stat(".access-point-mode")
        return True
    except:
        return False

    