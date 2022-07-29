#!/usr/bin/python3
import multiprocessing
import logging

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


# todo refactor this to process
def spawn_camera_process(feed, camera_name, api_pref=None):
        cv2.namedWindow(camera_name)
        logging.warn(f"`{feed}`")
        if api_pref is None:
            cam = cv2.VideoCapture(feed)
        else:
            cam = cv2.VideoCapture(feed, api_pref)
        if cam.isOpened():  # try to get the first frame
            rval, frame = cam.read()
        else:
            rval = False
        while rval:
            cv2.imshow(camera_name, frame)
            rval, frame = cam.read()

            # todo remove this when installed in car
            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break

        cv2.destroyWindow(camera_name)



def show_camera():
    # Pin Setup:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(frontview_camera_pin, GPIO.IN)  # set pin as an input pin

    logging.warning("Starting...")

    frontview_camera_thread = multiprocessing.Process(target=spawn_camera_process, args=(), kwargs={"feed": gstreamer_pipeline(flip_method=2), "api_pref": cv2.CAP_GSTREAMER, "camera_name": "frontview"})
    rearview_camera_thread = multiprocessing.Process(target=spawn_camera_process, args=(), kwargs={"feed": "/dev/video1", "camera_name": "rearview"})
    try:
        old_time = time.time()
        rearview_on = GPIO.input(frontview_camera_pin)
        logging.warning(f"REARVIEW ON `{rearview_on}`")
        while True:
            current_time = time.time()
            if current_time - old_time > .5:
                rearview_on = GPIO.input(frontview_camera_pin)
                logging.warning(f"REARVIEW ON `{rearview_on}`")
                old_time = current_time

            if rearview_on:
                if frontview_camera_thread.is_alive():
                    frontview_camera_thread.terminate()
                if not rearview_camera_thread.is_alive():
                    rearview_camera_thread = multiprocessing.Process(target=spawn_camera_process, args=(), kwargs={"feed": "/dev/video1", "camera_name": "rearview"})
                    rearview_camera_thread.start()
            else:
                if rearview_camera_thread.is_alive():
                    rearview_camera_thread.terminate()
                if not frontview_camera_thread.is_alive():
                    frontview_camera_thread = multiprocessing.Process(target=spawn_camera_process, args=(), kwargs={"feed": gstreamer_pipeline(flip_method=2), "api_pref": cv2.CAP_GSTREAMER, "camera_name": "frontview"})
                    frontview_camera_thread.start()

            # todo remove this when installed in car
            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break
    finally:
        GPIO.cleanup()
        if rearview_camera_thread.is_alive():
            rearview_camera_thread.terminate()
        if frontview_camera_thread.is_alive():
            frontview_camera_thread.terminate()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    show_camera()
