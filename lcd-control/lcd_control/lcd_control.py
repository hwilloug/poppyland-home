#!/usr/bin/python3

from rpi_lcd import LCD
from signal import signal, SIGTERM, SIGHUP, pause
from datetime import datetime
import time
import RPi.GPIO as GPIO

raincloud_channel = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(raincloud_channel, GPIO.OUT)

lcd = LCD()

def safe_exit(signum, frame):
    exit(1)
    
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

try:
    while True:
        lcd.text(datetime.now().strftime("%a, %m-%d-%Y"), 1)
        lcd.text(datetime.now().strftime("%-I:%M:%S %p"), 2)
        lcd.text(f"Raincloud: {'open' if GPIO.input(raincloud_channel) else 'closed'}", 4)
        
    pause()
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()