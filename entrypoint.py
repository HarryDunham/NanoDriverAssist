#!/usr/bin/python3
import logging
from systemd.journal import JournalHandler
import cv2

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    logger.info("Starting the webcam stream")
    show_webcam()


if __name__ == '__main__':
    main()
