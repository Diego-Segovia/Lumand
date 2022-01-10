import requests
from requests.exceptions import HTTPError

class LightController():
    def __init__(self, token):
        self.headers = {"Authorization": "Bearer %s" % token,}
        self.payload = {}
    
    def do_action(self):
        try:
            response = requests.put('https://api.lifx.com/v1/lights/all/state', data=self.payload, headers=self.headers)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        return response.json().get('results')[0]
    
    def turn_on(self):
        if self.payload.get('power', False):
            if self.payload['power'] != 'on':
                self.payload['power'] = 'on'
        else:
            self.payload['power'] = 'on'

        return self.do_action()
        

    def turn_off(self):
        if self.payload.get('power', False):
            if self.payload['power'] != 'off':
                self.payload['power'] = 'off'
        else:
            self.payload['power'] = 'off'

        return self.do_action()

    def set_brightness(self, val=1.0):
        if type(val) is not float:
            raise TypeError('Brightness value must be a float.')

        if not 0.0 <= val <= 1.0:
            raise ValueError('Brightness value must be between 0.0 and 1.0.')

        self.payload['brightness'] = val

        return self.do_action()
