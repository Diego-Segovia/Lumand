import requests
from requests.exceptions import HTTPError

class LightController():
    def __init__(self, token):
        self.headers = {"Authorization": "Bearer %s" % token,}
        self.payload = {}

    # Execute Query
    def do_action(self):
        try:
            response = requests.put('https://api.lifx.com/v1/lights/all/state', data=self.payload, headers=self.headers)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        return response.json().get('results')[0]

    # Enable Fast Mode: Execute the query fast, without initial state checks and wait for no results.
    def fast_mode(self):
        self.payload['fast'] = True
    
    # Turn light on
    def turn_on(self, go_fast=False):
        if go_fast:
            self.fast_mode()

        if self.payload.get('power', False):
            if self.payload['power'] == 'on':
                return -1

        self.payload['power'] = 'on'

        return self.do_action()
        
    # Turn light off
    def turn_off(self, go_fast=False):
        if go_fast:
            self.fast_mode()
        
        if self.payload.get('power', False):
            if self.payload['power'] == 'off':
                return -1

        self.payload['power'] = 'off'

        return self.do_action()

    # Set Brightness Level between 0.0 and 1.0
    def set_brightness(self, val=1.0, go_fast=False):
        if type(val) is not float:
            raise TypeError('Brightness value must be a float.')

        if not 0.0 <= val <= 1.0:
            raise ValueError('Brightness value must be between 0.0 and 1.0.')
        
        if go_fast:
            self.fast_mode()

        self.payload['brightness'] = val

        return self.do_action()
