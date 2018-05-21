from kivy.app import App
from kivy.core.window import Window
from joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from tellopy import Tello

IDX_ROLL = 0
IDX_PITCH = 1
IDX_THR = 2
IDX_YAW = 3


class DragableJoystick(Joystick):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pos = touch.x-self.width/2, touch.y-self.height/2
            return super(DragableJoystick, self).on_touch_down(touch)


class KivyTelloRoot(BoxLayout):

    def __init__(self, drone=None, **kwargs):
        super(KivyTelloRoot, self).__init__(**kwargs)
        self.stick_data = [0.0] * 4
        Window.allow_vkeyboard = False
        self._keyboard = Window.request_keyboard(self.keyboard_closed,
                                                 self,
                                                 'text')
        self._keyboard.bind(on_key_down=self.on_key_down)
        self.ids.pad_left.ids.stick.bind(pad=self.on_pad_left)
        self.ids.pad_right.ids.stick.bind(pad=self.on_pad_right)
        self.ids.takeoff.bind(state=self.on_state_takeoff)
        self.ids.rotcw.bind(state=self.on_state_rotcw)
        self.ids.rotccw.bind(state=self.on_state_rotccw)
        self.ids.quit.bind(on_press=lambda x: self.stop())
        self.drone = drone
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, self.handler)

    def handler(self, event, sender, data, **args):
        drone = sender
        if event is self.drone.EVENT_FLIGHT_DATA:
            print(data)

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        print(keycode[1])
        if keycode[1] == 'escape':
            self.stop()
            return True
        elif keycode[1] == 'spacebar':
            if self.ids.takeoff.state == 'normal':
                self.ids.takeoff.state = 'down'
            else:
                self.ids.takeoff.state = 'normal'
            return True
        elif keycode[1] == '1':
            if self.ids.rotcw.state == 'normal':
                self.ids.rotcw.state = 'down'
            else:
                self.ids.rotcw.state = 'normal'
            return True
        elif keycode[1] == '2':
            if self.ids.rotccw.state == 'normal':
                self.ids.rotccw.state = 'down'
            else:
                self.ids.rotccw.state = 'normal'
            return True
        else:
            return False

    def on_state_takeoff(self, instance, value):
        if value == 'down':
            print 'take off'
            self.drone.takeoff()
        else:
            print 'land'
            self.drone.land()

    def on_state_rotcw(self, instance, value):
        if value == 'down':
            print 'start cw'
            self.drone.clockwise(50)
        else:
            print 'stop cw'
            self.drone.clockwise(0)

    def on_state_rotccw(self, instance, value):
        if value == 'down':
            print 'start ccw'
            self.drone.counter_clockwise(50)
        else:
            print 'stop ccw'
            self.drone.counter_clockwise(0)

    def on_pad_left(self, instance, value):
        x, y = value
        self.stick_data[IDX_YAW] = x
        self.stick_data[IDX_THR] = y
        self.ids.pad_left.ids.label.text = \
            'THR: {0:f}\n' \
            'YAW: {1:f}'.format(self.stick_data[IDX_THR],
                                self.stick_data[IDX_YAW])
        self.drone.set_throttle(self.stick_data[IDX_THR])
        self.drone.set_yaw(self.stick_data[IDX_YAW])

    def on_pad_right(self, instance, value):
        x, y = value
        self.stick_data[IDX_ROLL] = x
        self.stick_data[IDX_PITCH] = y
        self.ids.pad_right.ids.label.text = \
            'ROLL: {0:f}\n' \
            'PITCH: {1:f}'.format(self.stick_data[IDX_ROLL],
                                  self.stick_data[IDX_PITCH])
        self.drone.set_roll(self.stick_data[IDX_ROLL])
        self.drone.set_pitch(self.stick_data[IDX_PITCH])

    def stop(self):
        self.drone.quit()
        App.get_running_app().stop()


class KivyTelloApp(App):
    def __init__(self, drone=None, **kwargs):
        super(KivyTelloApp, self).__init__(**kwargs)
        self.drone = drone

    def build(self):
        return KivyTelloRoot(drone=self.drone)
        pass


if __name__ == '__main__':
    drone = Tello()
    try:
        drone.connect()
        drone.wait_for_connection(60.0)
        KivyTelloApp(drone=drone).run()
    except Exception as ex:
        print(ex)
        drone.quit()
        exit(1)
