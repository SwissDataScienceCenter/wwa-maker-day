from machine import Pin, I2C
from time import sleep
from dht_20 import DHT20

# Set up I2C pins
i2c1_sda = Pin(14)
i2c1_scl = Pin(15)

# Set up I2C
i2c1 = I2C(1, sda=i2c1_sda, scl=i2c1_scl)

# Set up DHT20 device with I2C address
dht20 = DHT20(0x38, i2c1)

while True:
    
    # Grab data from the sensor dictionary
    measurements = dht20.measurements
    
    # Print the data
    print(measurements['t'])
    print(measurements['t_adc'])
    print(measurements['rh'])
    print(measurements['rh_adc'])
    print(measurements['crc_ok'])
    
    # Wait 5 seconds
    sleep(5)
