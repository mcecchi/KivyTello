import sys
import traceback
import time
from threading import Thread
from flask import Response
from perfume import route, Perfume


class FlaskApp(Perfume):
    def __init__(self, drone=None, **kwargs):
        super(FlaskApp, self).__init__(**kwargs)
        self.face_detect = True

    def __getattr__(self, name):
        pass

    @property
    def face_detect(self):
        return self._face_detect

    @face_detect.setter
    def face_detect(self, val):
        self._face_detect = val

    @route('/')
    def root(self):
        return 'self.face_detect = {}'.format(self.face_detect)


def start_flask_app(flask_app=None):
    print("Starting Flask app...")
    flask_app.run(port=5000, debug=True,
                              use_reloader=False, threaded=True)


if __name__ in ('__main__', '__android__'):
    try:
        flask_app = FlaskApp()
        t = Thread(target=start_flask_app, args=(flask_app,))
        t.setDaemon(True)
        t.start()
        while True:
            time.sleep(5)
            flask_app.face_detect = not flask_app.face_detect
    except Exception as ex:
        print(ex)
        # exit(1)
