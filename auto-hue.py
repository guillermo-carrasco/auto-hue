import json
import sys
import time

from requests.exceptions import ConnectionError

import RPi.GPIO as GPIO
import requests

# Data pin for the PIR sensor
PIR_IN = 7

# Configure data pin as input
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_IN, GPIO.IN)

# Hue settings/variables
ENTRANCE_ON = False
USER_ID = ''
BRIDGE_IP = requests.get('https://www.meethue.com/api/nupnp').json()[0].get('internalipaddress')
BASE_URL = 'http://{}/api'.format(BRIDGE_IP)
LIGHTS_URL = BASE_URL + '{}/lights'.format(USER_ID)

# Get entrance light id
ENTRANCE = None
for light, properties in requests.get(LIGHTS_URL).json().iteritems():
    if properties.get('name') == 'Entrance':
        ENTRANCE = light

if ENTRANCE is None:
    print "No entrance light found :-("
    sys.exit(0)



def switch_light(turn_on):
    on = {'on': turn_on}
    try:
        requests.put(LIGHTS_URL + '/{}/state'.format(ENTRANCE), json.dumps(on))
        return True
    except ConnectionError:
        print 'WARN: No internet connection'
        return False


# Turn the light off on program start
switch_light(False)


while True:
    i = GPIO.input(PIR_IN)
    if i == GPIO.HIGH and not ENTRANCE_ON and switch_light(True):
        ENTRANCE_ON = True
    elif i == GPIO.LOW and ENTRANCE_ON and switch_light(False):
        ENTRANCE_ON = False
