from time import sleep


class Color:
    def __init__(self, r, g, b, w):
        self.r = r
        self.g = g
        self.b = b
        self.w = w


class Everloop:
    def __init__(self):
        self.image = bytearray([0, 0, 0, 0] * 18)
        self.mode = "idle"
        # self.running = False

        self.idle_color = bytearray([1, 0, 1, 0])
        self.active_color = bytearray([0, 5, 0, 0])
        self.busy_color = bytearray([0, 0, 5, 0])
        self.error_color = bytearray([5, 0, 0, 0])

    
    def render(self):
        with open('/dev/matrixio_everloop', 'wb', buffering=0) as f:
            f.write(self.image)


    def modify_color_preset(self, preset, color):
        if preset == "idle":
            self.idle_color = color
            if self.mode == "idle":
                self.set_idle_color()
            return True
        elif preset == "active":
            self.active_color = color
            if self.mode == "active":
                self.set_active_color()
            return True
        elif preset == "busy":
            self.busy_color = color
            if self.mode == "busy":
                self.set_busy_color()
            return True
        elif preset == "error":
            self.error_color = color
            if self.mode == "error":
                self.set_error_color()
            return True
        else:
            return False


    def modify_color_preset_rgbw(self, preset, r, g, b, w):
        return self.modify_color_preset(preset, bytearray([r, g, b, w]))


    def set_color_rgbw(self, r, g, b, w):
        self.image = bytearray([r, g, b, w] * 18)

        self.render()
        self.mode = "custom"


    def set_color(self, color):
        self.set_color_rgbw(color[0], color[1], color[2], color[3])


    def set_idle_color(self):
        self.set_color(self.idle_color)
        self.mode = "idle"


    def set_active_color(self):
        self.set_color(self.active_color)
        self.mode = "active"
        

    def set_busy_color(self):
        self.set_color(self.busy_color)
        self.mode = "busy"
        

    def set_error_color(self):
        self.set_color(self.error_color)
        self.mode = "error"


    def set_off(self):
        self.set_color_rgbw(0, 0, 0, 0)
        self.mode = "off"


    # def everloop_rotating_animation(self, counter):
    #     index = counter % 17

    #     for led in self.image.leds:
    #         rotated_led = (led + index) % 17

    #         led.blue = 0
    #         led.red = 0
    #         led.green = max(0, 255 - (rotated_led * 20))
    #         led.white = 0

    #     self.image.render()


    # def everloop_pulsating_animation(self, counter):
    #     pulse_range = 30
    #     intensity = ((pulse_range // 2) - abs(pulse_range - counter % (pulse_range * 2))) * 8

    #     for led in self.image.leds:
    #         led.blue = 0
    #         led.red = 0
    #         led.green = 128 + intensity
    #         led.white = 0

    #     self.image.render()


    def everloop_blue(self, counter):
        self.image = bytearray([5, 5, 0, 0] * 18)
        self.render()

    
    def everloop_green(self):
        self.image = bytearray([0, 0, 5, 0] * 18)
        self.render()


    def everloop_max_bright(self):
        self.image = bytearray([255, 255, 255, 255] * 18)
        self.render()


    # def animation(self):
    #     counter = 0

    #     # Start loop of no return!
    #     while self.running.value:
    #         if self.mode == 0:
    #             self.everloop_blue(counter)
    #         elif self.mode == 1:
    #             self.everloop_green(counter)
    #         elif self.mode == 2:
    #             self.everloop_rotating_animation(counter)
    #         elif self.mode == 3:
    #             self.everloop_max_bright(counter)
    #         else:
    #             self.everloop_set_off(counter)

    #         counter += 1
    #         time.sleep(0.3)

    #     self.everloop_set_off(counter)

