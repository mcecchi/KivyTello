import sys
import traceback
import av
import cv2
import numpy
import time
from kivy.app import App
from kivy.core.window import Window
from joystick import Joystick
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import CoverBehavior
from kivy.uix.video import Video
from tellopy import Tello
from threading import Thread
from flask import Response
from perfume import route, Perfume


class FlaskApp(Perfume):
    def __init__(self, drone=None, **kwargs):
        super(FlaskApp, self).__init__(**kwargs)
        self.drone = drone
        self.face_detect = False

    def __getattr__(self, name):
        pass

    @property
    def face_detect(self):
        return self.__face_detect

    @face_detect.setter
    def face_detect(self, val):
        self.__face_detect = val

    @route('/video_feed')
    def video_feed(self):
        def generate():
            try:
                container = av.open(self.drone.get_video_stream())
                if self.face_detect:
                    faceCascade = cv2.CascadeClassifier(
                        "haarcascade_frontalface_default.xml")
                frame_skip = 300
                while True:
                    for frame in container.decode(video=0):
                        if 0 < frame_skip:
                            frame_skip = frame_skip - 1
                            continue
                        start_time = time.time()
                        image = numpy.array(frame.to_image())
                        color = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        if self.face_detect:
                            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                            faces = faceCascade.detectMultiScale(
                                gray,
                                scaleFactor=1.1,
                                minNeighbors=5,
                                minSize=(30, 30),
                                flags=cv2.CASCADE_SCALE_IMAGE
                            )
                            for (x, y, w, h) in faces:
                                cv2.rectangle(
                                    color, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        ret, jpeg = cv2.imencode('.jpg', color)
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' +
                               jpeg.tobytes() +
                               b'\r\n\r\n')
                        frame_skip = int((time.time() -
                                         start_time)/frame.time_base)
            except Exception as ex:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                print(ex)
            finally:
                self.drone.quit()
                # cv2.destroyAllWindows()
                pass

        return Response(generate(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


def start_flask_app(flask_app=None):
    print("Starting Flask app...")
    flask_app.run(port=5000, debug=True,
                  use_reloader=False, threaded=True)


IDX_ROLL = 0
IDX_PITCH = 1
IDX_THR = 2
IDX_YAW = 3


class CoverVideo(CoverBehavior, Video):
    def _on_video_frame(self, *largs):
        video = self._video
        if not video:
            return
        texture = video.texture
        self.reference_size = texture.size
        self.calculate_cover()
        self.duration = video.duration
        self.position = video.position
        self.texture = texture
        self.canvas.ask_update()


class DragableJoystick(Joystick):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pos = touch.x-self.width/2, touch.y-self.height/2
            return super(DragableJoystick, self).on_touch_down(touch)


class KivyTelloRoot(FloatLayout):

    def __init__(self, drone=None, flask_app=None, **kwargs):
        super(KivyTelloRoot, self).__init__(**kwargs)
        self.stick_data = [0.0] * 4
        Window.allow_vkeyboard = False
        self.ids.pad_left.ids.stick.bind(pad=self.on_pad_left)
        self.ids.pad_right.ids.stick.bind(pad=self.on_pad_right)
        self.ids.takeoff.bind(state=self.on_state_takeoff)
        self.ids.rotcw.bind(state=self.on_state_rotcw)
        self.ids.rotccw.bind(state=self.on_state_rotccw)
        self.ids.facedetect.bind(state=self.on_state_facedetect)
        self.ids.quit.bind(on_press=lambda x: self.stop())
        self.drone = drone
        self.flask_app = flask_app
        # self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, self.handler)
        # self.drone.start_video()
        # self.drone.subscribe(self.drone.EVENT_VIDEO_FRAME, self.handler)

    # def handler(self, event, sender, data, **args):
        # drone = sender
        # if event is self.drone.EVENT_FLIGHT_DATA:
        #     print(data)
        # # elif event is self.drone.EVENT_VIDEO_FRAME:
        # #     pass
        # # else:
        # #     rint(('event="%s" data=%s' % (event.getname(), str(data))))

    def on_state_takeoff(self, instance, value):
        if value == 'down':
            print('take off')
            self.drone.takeoff()
        else:
            print('land')
            self.drone.land()

    def on_state_rotcw(self, instance, value):
        if value == 'down':
            print('start cw')
            self.drone.clockwise(50)
        else:
            print('stop cw')
            self.drone.clockwise(0)

    def on_state_rotccw(self, instance, value):
        if value == 'down':
            print('start ccw')
            self.drone.counter_clockwise(50)
        else:
            print('stop ccw')
            self.drone.counter_clockwise(0)

    def on_state_facedetect(self, instance, value):
        if value == 'down':
            print('start fd')
            self.flask_app.face_detect = True
        else:
            print('stop fd')
            self.flask_app.face_detect = False

    def on_pad_left(self, instance, value):
        x, y = value
        self.stick_data[IDX_YAW] = x
        self.stick_data[IDX_THR] = y
        # self.ids.pad_left.ids.label.text = \
        #     'THR: {0:f}\n' \
        #     'YAW: {1:f}'.format(self.stick_data[IDX_THR],
        #                         self.stick_data[IDX_YAW])
        self.drone.set_throttle(self.stick_data[IDX_THR])
        self.drone.set_yaw(self.stick_data[IDX_YAW])

    def on_pad_right(self, instance, value):
        x, y = value
        self.stick_data[IDX_ROLL] = x
        self.stick_data[IDX_PITCH] = y
        # self.ids.pad_right.ids.label.text = \
        #     'ROLL: {0:f}\n' \
        #     'PITCH: {1:f}'.format(self.stick_data[IDX_ROLL],
        #                           self.stick_data[IDX_PITCH])
        self.drone.set_roll(self.stick_data[IDX_ROLL])
        self.drone.set_pitch(self.stick_data[IDX_PITCH])

    def stop(self):
        self.drone.quit()
        App.get_running_app().stop()


class KivyTelloApp(App):
    def __init__(self, drone=None, flask_app=None, **kwargs):
        super(KivyTelloApp, self).__init__(**kwargs)
        self.drone = drone
        self.flask_app = flask_app

    def build(self):
        return KivyTelloRoot(drone=self.drone, flask_app=self.flask_app)

    def on_pause(self):
        return True

    def on_stop(self):
        Window.close()


if __name__ in ('__main__', '__android__'):
    drone = Tello()
    try:
        drone.connect()
        drone.wait_for_connection(60.0)
        flask_app = FlaskApp(drone=drone)
        t = Thread(target=start_flask_app, args=(flask_app,))
        t.setDaemon(True)
        t.start()
        KivyTelloApp(drone=drone, flask_app=flask_app).run()
    except Exception as ex:
        print(ex)
        drone.quit()
        Window.close()
        # exit(1)
