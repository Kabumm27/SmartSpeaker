from time import sleep
from threading import Thread


class Everloop(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.color = bytearray([0, 0, 0, 0] * 18)
        self.image = None
        self.running = True
        self.sleep_time = 0.03

        self._pulsating = False
        self._rotating = False

        self.presets = {
            'idle': bytearray([0, 0, 0, 0]),
            'listening': bytearray([0, 5, 0, 0]),
            'thinking': bytearray([0, 0, 5, 0] + [0, 0, 4, 0] + [0, 0, 3, 0] + [0, 0, 2, 0] + [0, 0, 1, 0] + ([0, 0, 0, 0] * 13)),
            'error': bytearray([5, 0, 0, 0])
        }

        self.start()


    def run(self):
        with open('/dev/matrixio_everloop', 'wb', buffering=0) as f:
            i = 0
            while self.running:
                self.image = self.color[:]

                if self._rotating:
                    self.rotate(i)
                if self._pulsating:
                    self.pulsate(i)

                i += 1
                f.write(self.image)
                sleep(self.sleep_time)


    def terminate(self):
        self.running = False
        self.set_off()
        with open('/dev/matrixio_everloop', 'wb', buffering=0) as f:
            f.write(self.color)

    
    def rotate(self, n):
        n = n % 18
        self.image = self.image[4 * n:] + self.image[:4 * n]


    def pulsate(self, n, pulse_range=10, speed=3):
        pulse_range *= speed
        # intensity = ((pulse_range // 2) - abs(pulse_range - n % (pulse_range * 2))) * 2 # from -pulse_range -> +pulse_range
        intensity = abs(pulse_range - n % (pulse_range * 2)) # from 0 -> pulse_range
        intensity = intensity // speed

        for i in range(len(self.image)):
            if self.image[i] > 0:
                self.image[i] = max(0, min(255, self.image[i] + intensity))


    def modify_color_preset(self, preset, colors):
        if preset in self.presets:
            self.presets[preset] = bytearray(colors)
            return True
        return False


    def modify_color_preset_rgbw(self, preset, r=0, g=0, b=0, w=0):
        return self.modify_color_preset(preset, bytearray([r, g, b, w]))


    def set_circle_color(self, r=0, g=0, b=0, w=0, pulsating=False, rotating=False):
        self._pulsating = pulsating
        self._rotating = rotating

        colors = [r, g, b, w]
        for i in range(len(self.color)):
            self.color[i] = colors[i % 4]


    def set_pixel_color(self, n, r=0, g=0, b=0, w=0):
        n *= 4
        self.color[n + 0] = r
        self.color[n + 1] = g
        self.color[n + 2] = b
        self.color[n + 3] = w


    def set_idle(self):
        self._pulsating = False
        self._rotating = False

        mod = len(self.presets['idle'])
        for i in range(len(self.color)):
            self.color[i] = self.presets['idle'][i % mod]


    def set_listening(self):
        self._pulsating = True
        self._rotating = False

        mod = len(self.presets['listening'])
        for i in range(len(self.color)):
            self.color[i] = self.presets['listening'][i % mod]


    def set_thinking(self):
        self._pulsating = False
        self._rotating = True

        mod = len(self.presets['thinking'])
        for i in range(len(self.color)):
            self.color[i] = self.presets['thinking'][i % mod]

    
    def set_error(self):
        self._pulsating = False
        self._rotating = False

        mod = len(self.presets['error'])
        for i in range(len(self.color)):
            self.color[i] = self.presets['error'][i % mod]


    def set_off(self):
        self._pulsating = False
        self._rotating = False

        for i in range(len(self.color)):
            self.color[i] = 0



if __name__ == '__main__':
    everloop = Everloop()
    # everloop.set_pixel_color(0, 0, 0, 0, 5)
    everloop.set_listening()

    sleep(3)
    everloop.terminate()
