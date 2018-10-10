import soco


class Sonos():
    def __init__(self):
        self._get_available_rooms()

    def _get_available_rooms(self):
        self.rooms = []
        for d in soco.discover():
            self.rooms.append(d.player_name)

    def _get_room_device(self, room):
        if not room in self.rooms: return None
        return soco.discovery.by_name(room)

    def play(self, room):
        device = self._get_room_device(room)
        device.play()

    def pause(self, room):
        device = self._get_room_device(room)
        device.pause()

    def change_volume(self, room, to=None, by=None):
        if to == None and by == None: return False

        device = self._get_room_device(room)

        if to:
            volume = to
        else:
            volume = device.volume + by

        device.volume = volume
        print(device.volume)

    def next_track(self, room):
        device = self._get_room_device(room)
        device.next()

    def previous_track(self, room):
        device = self._get_room_device(room)
        device.previous()

    def select_stream(self, room, uri, meta='', title=''):
        device = sonos._get_room_device('Wohnzimmer')
        device.play_uri(uri=uri, meta=meta, title=title)

if __name__ == '__main__':
    sonos = Sonos()
    device = sonos._get_room_device('Wohnzimmer')
    # sonos.play('Wohnzimmer')
    # sonos.change_volume('Wohnzimmer', to=20)
    # sonos.previous_track('Wohnzimmer')
    # sonos.pause('Wohnzimmer')

    radio_stations = device.get_favorite_radio_stations()['favorites']
    station = radio_stations[1]
    
    # sonos.select_stream('Wohnzimmer', station['uri'], title=station['title'])
    sonos.pause('Wohnzimmer')
