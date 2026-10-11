import cv2

cap = cv2.VideoCapture(0)  # try 1 or 2 if you have an external camera
if not cap.isOpened():
    raise RuntimeError("Camera not found, try a different index")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("Camera test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()