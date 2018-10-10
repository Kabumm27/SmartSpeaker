import json
from urllib.request import Request, urlopen


class HueLights():
    COLOR_RED = {'hue': 0, 'sat': 255}
    COLOR_GREEN = {'hue': 25500, 'sat': 255}
    COLOR_BLUE = {'hue': 46920, 'sat': 255}
    COLOR_PURPLE = {'hue': 56100, 'sat': 255}

    COLOR_WARM = {'hue': 5800, 'sat': 205}
    COLOR_NEUTRAL = {'hue': 54346, 'sat': 25}
    COLOR_COLD = {'hue': 42495, 'sat': 124}

    COLOR_DEFAULT = {'hue': 7208, 'sat': 224}


    def __init__(self, ip, key):
        self.ip = ip
        self.key = key
        self.base_url = 'http://{}/api/{}/'.format(self.ip, self.key)

        self.load_rooms()


    def load_rooms(self):
        req = Request(self.base_url, method='GET')
        response = urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        self.rooms = {}
        for _, group in data['groups'].items():
            if group['type'] == 'Room':
                name = group['name'].lower()
                if not name in self.rooms:
                    self.rooms[name] = []
                for light in group['lights']:
                    self.rooms[name].append(light)

    def switch_on(self, room):
        self.switch(room, True)
    
    def switch_off(self, room):
        self.switch(room, False)

    def switch(self, room, on):
        lights = self._get_lights(room)
        data = str.encode(json.dumps({'on': on}))
        self._put_light_request(lights, data)

    def dim(self, room, by=None, to=None):
        if not by and not to:
            return False

        if by:
            bri = self._get_brightness(room) + by
        else:
            bri = to
        
        lights = self._get_lights(room)
        data = str.encode(json.dumps({'on': True, 'bri': bri}))
        self._put_light_request(lights, data)

    def change_color(self, room, color):
        if type(color) == str:
            color = self._string_to_color(color)

        hue = color['hue']
        sat = color['sat']

        lights = self._get_lights(room)
        data = str.encode(json.dumps({'on': True, 'hue': hue, 'sat': sat}))
        self._put_light_request(lights, data)


    def _get_brightness(self, room):
        lights = self._get_lights(room)
        data = self._get_light_state(lights)

        bri = 0
        for _, state in data.items():
            bri += state['bri']

        return bri // len(lights)

    def _get_lights(self, room):
        room = room.lower()
        if not room in self.rooms:
            return []
        return self.rooms[room]

    def _put_light_request(self, lights, data):
        for light in lights:
            url = self.base_url + 'lights/' + light + '/state'
            req = Request(url, data=data, method='PUT')
            response = urlopen(req)

    def _get_light_state(self, lights):
        state = {}
        for light in lights:
            url = self.base_url + 'lights/' + light
            req = Request(url, method='GET')
            response = urlopen(req)
            state[light] = json.loads(response.read().decode('utf-8'))['state']
        return state

    def _string_to_color(self, color_string):
        color_string = color_string.lower()
        if color_string in ['red', 'rot']:
            return self.COLOR_RED
        if color_string in ['blue', 'blau']:
            return self.COLOR_BLUE
        if color_string in ['green', 'grün']:
            return self.COLOR_GREEN
        if color_string in ['purple', 'violett', 'lila']:
            return self.COLOR_PURPLE
        if color_string in ['warm']:
            return self.COLOR_WARM
        if color_string in ['neutral']:
            return self.COLOR_NEUTRAL
        if color_string in ['cold', 'kalt']:
            return self.COLOR_COLD
        if color_string in ['default']:
            return self.COLOR_DEFAULT


if __name__ == '__main__':
    # hue = HueLights('192.168.178.49', 'ktAfubPaW2rrROs3113VIQcYpfLGXIQNbvpGS6Ji')
    # hue.dim('Büro', to=30)
    # hue.switch_on('Büro')
    # hue.change_color('Büro', 'default')
    print('main')
