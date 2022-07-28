import cv2

cap = cv2.VideoCapture("/dev/video1")

if cap.isOpened():
    try:
        while True:
            ret_val, frame = cap.read()
            cv2.imshow("", frame)
            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
