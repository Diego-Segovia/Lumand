import requests
from requests.exceptions import HTTPError

class LightController():
    def __init__(self, token):
        self._headers = {"Authorization": "Bearer %s" % token,}
        self._payload = {}

    # Execute Query
    def do_action(self):
        try:
            requests.put('https://api.lifx.com/v1/lights/all/state', data=self._payload, headers=self._headers)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')


    # Enable Fast Mode: Execute the query fast, without initial state checks and wait for no results.
    def fast_mode(self):
        self._payload['fast'] = True
    
    # Turn light on
    def turn_on(self, go_fast=False):
        if go_fast:
            self.fast_mode()

        if self._payload.get('power', False):
            if self._payload['power'] == 'on':
                return -1

        self._payload['power'] = 'on'

        self.do_action()
        
    # Turn light off
    def turn_off(self, go_fast=False):
        if go_fast:
            self.fast_mode()
        
        if self._payload.get('power', False):
            if self._payload['power'] == 'off':
                return -1

        self._payload['power'] = 'off'

        self.do_action()

    # Set Brightness Level between 0.0 and 1.0
    def set_brightness(self, val=1.0, go_fast=False):
        if type(val) is not float:
            raise TypeError('Brightness value must be a float.')

        if not 0.0 <= val <= 1.0:
            raise ValueError('Brightness value must be between 0.0 and 1.0.')
        
        if go_fast:
            self.fast_mode()

        self._payload['brightness'] = val

        self.do_action()
