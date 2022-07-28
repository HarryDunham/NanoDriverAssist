#!/usr/bin/python3

import cv2
import RPi.GPIO as GPIO
import time


frontview_camera_pin = 31
left_turn_signal = 24
right_turn_signal = 23


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
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


def show_camera():
    window_title = ""

    # Pin Setup:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(frontview_camera_pin, GPIO.IN)  # set pin as an input pin

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=2))
    front_video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
    back_video_capture = cv2.VideoCapture("/dev/video1")
    if front_video_capture.isOpened() and back_video_capture.isOpened():
        try:
            old_time = time.time()
            rearview_on = GPIO.input(frontview_camera_pin)
            cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            previous_camera = None
            current_camera = None
            while True:
                current_time = time.time()
                if current_time - old_time > .5:
                    rearview_on = GPIO.input(frontview_camera_pin)
                    old_time = current_time

                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0 and rearview_on:
                    if current_camera != "rearview":
                        previous_camera = current_camera
                        current_camera = "rearview"
                        front_video_capture.release()
                    ret_val, frame = back_video_capture.read()
                    cv2.imshow(window_title, frame)
                else:
                    if current_camera != "frontview":
                        previous_camera = current_camera
                        current_camera = "frontview"
                        back_video_capture.release()
                    ret_val, frame = front_video_capture.read()
                    cv2.imshow(window_title, frame)
                keyCode = cv2.waitKey(10) & 0xFF

                # todo remove this when installed in car
                if keyCode == 27 or keyCode == ord('q'):
                    break
        finally:
            GPIO.cleanup()
            front_video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")


if __name__ == "__main__":
    show_camera()
