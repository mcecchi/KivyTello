# KivyTello

![Screenshot](KiviTello.png?raw=true "Screenshot")

Kivy app to control your Ryze Tello.

Very simple python app to drive your Ryze Tello from desktop or smartphone.
It uses [Kivy](https://kivy.org) to create a basic platform independent GUI.

KivyTello in master branch works well on Android, both in Kivy Launcher
and .apk created with Buildozer.

I still haven't compiled KivyTello from videofeed branch for Android
due to lack of time, all volunteers are welcome!

# July 23, 2018 - Major update on branch [videofeed](https://github.com/mcecchi/KivyTello/tree/videofeed)

- Added video (using Kivy Video widget and Flask internal streaming server)
- Added simple face detection
- Using video in cover mode (background)
- Semi-transparent widgets

Very early stages,
**suggestions and pull requests are welcome!**

Note: this version of KiviTello requires opencv and av.
This can be tricky on some platforms.
On Windows, you can install prerequisites with

    pip install opencv-python
    pip install opencv-contrib-python
    pip install av

Then install FFmpeg from [shared and dev packages](https://ffmpeg.zeranoe.com/builds/)
and unpack them somewhere (like `C:\ffmpeg`), then use `set_env.cmd` in repo
to set environment variables according.
Now you can run KivyTello from branch videofeed on your desktop.

Sample screenshots:

![Screenshot](shot01.png?raw=true "Screenshot")

![Screenshot](shot02.png?raw=true "Screenshot")

**Note: please be patient. KiviTello drops first 300 frames, so
you must wait about 30 seconds before something appears on the screen.**

## Important update

**KiviTello finally works on Android!**

I used [Kivy Launcher](https://play.google.com/store/apps/details?id=org.kivy.pygame&hl=en).

Once the Kivy launcher is installed, you can put your KivyTello
folder in the Kivy directory in your external storage directory
(often available at `/sdcard` even in devices where this memory
is internal), e.g. :

    /sdcard/kivy/KivyTello

**KivyTello waits 60 seconds before exiting if you don't connect Tello in the meantime.**

KiviTello can also be packaged for Android (see [Create a package for Android](https://kivy.org/docs/guide/packaging-android.html#)) and I'll do it as soon as possible.

## Contributing

You're welcome!

## Credits

Many thanks to [TelloPy](https://github.com/hanyazou/TelloPy) for his great Tello library!
