#!/usr/bin/python3
import threading

import cv2
import RPi.GPIO as GPIO
import time


frontview_camera_pin = 31
left_turn_signal = 24
right_turn_signal = 23
WIDTH = 1920
HEIGHT = 1080


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=WIDTH,
    capture_height=HEIGHT,
    display_width=800,
    display_height=400,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


class CameraThread(threading.Thread):
    def __init__(self, *args, camera_name, **kwargs):
        threading.Thread.__init__(self)
        self.camera_name = camera_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        cv2.namedWindow(self.camera_name)
        cam = cv2.VideoCapture(*self.args, **self.kwargs)
        if cam.isOpened():  # try to get the first frame
            rval, frame = cam.read()
        else:
            rval = False
        while rval:
            cv2.imshow(self.camera_name, frame)
            rval, frame = cam.read()

            # todo remove this when installed in car
            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break

        cv2.destroyWindow(self.camera_name)


def show_camera():
    window_title = ""

    # Pin Setup:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(frontview_camera_pin, GPIO.IN)  # set pin as an input pin

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=2))
    frontview_camera_thread = CameraThread(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER, camera_name="frontview")
    rearview_camera_thread = CameraThread("/dev/video1", camera_name="rearview")
    frontview_camera_thread.run()
    try:
        old_time = time.time()
        rearview_on = GPIO.input(frontview_camera_pin)
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
        cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while True:
            current_time = time.time()
            if current_time - old_time > .5:
                rearview_on = GPIO.input(frontview_camera_pin)
                old_time = current_time

            if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0 and rearview_on:
                frontview_camera_thread.join()
                rearview_camera_thread.start()
            else:
                if rearview_camera_thread.is_alive():
                    rearview_camera_thread.join()
                if not frontview_camera_thread.is_alive():
                    frontview_camera_thread.start()

            # todo remove this when installed in car
            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break
    finally:
        GPIO.cleanup()
        if rearview_camera_thread.is_alive():
            rearview_camera_thread.join()
        if frontview_camera_thread.is_alive():
            frontview_camera_thread.join()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    show_camera()
