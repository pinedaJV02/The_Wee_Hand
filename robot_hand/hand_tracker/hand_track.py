import time
import cv2
import mediapipe as mp # import the mediapipe library, which is used for building multimodal applied machine learning pipelines.
                       # It provides pre-trained models and tools for tasks like hand tracking, face detection, and pose estimation.
from mediapipe.tasks import python # import the python module from mediapipe.tasks, 
                                   # which provides access to various machine learning tasks and models that can be used in Python applications.
from mediapipe.tasks.python import vision # import the vision module from mediapipe.tasks.python, 
                                          # which provides tools and models for computer vision tasks such as image classification, object detection, and hand tracking.

# ---------- Setup that runs once, before the loop ----------

model_path = "mediapipe_Model/hand_landmarker.task"
BaseOptions = mp.tasks.BaseOptions # default options
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Pairs of landmark indices that form the bones of the hand, used to draw the lines
# this telss us where a line needs to start and end
# mediapipe only tell us the position of the 21 landmarks but not how they are connected
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),         # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),         # index finger
    (5, 9), (9, 10), (10, 11), (11, 12),    # middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),  # ring finger
    (13, 17), (17, 18), (18, 19), (19, 20), # pinky
    (0, 17),                                # edge of the palm
]

# The callback runs on a separate thread, so it only saves the newest result here.
# The main loop reads this variable and does the drawing.
# intially, there is no result, so we set it to None
latest_result = None

# ---------- Callback function that runs when the landmarker has a new result ----------
# Create a hand landmarker instance with the live stream mode:
def store_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_result # use the global variable latest_result to store the result from the callback function, do not create a new locaal variable
    latest_result = result # update the latest_result variable with the new result from the callback function

# ---------- Setup that runs once, before the loop ----------
# open the camera and check if it is available. If not, raise an error.
cap = cv2.VideoCapture(0)  # try 1 or 2 if you have an external camera
if not cap.isOpened():
    raise RuntimeError("Camera not found, try a different index")

# save the options for the hand landmarker
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=2,
    result_callback=store_result)

# time.monotonic() returns the value (in fractional seconds) of a clock which never goes backwards.
# It is used here to get a reference point for timestamps, ensuring that every frame processed by the hand landmarker has a rising timestamp.
# This is important for synchronizing the processing of frames in real-time applications.
start_time = time.monotonic()  # reference point so every frame gets a rising timestamp

# ---------- Main loop, inside the landmarker block ----------
# create a hand landmarker instance using the options defined above. 
# The "with" statement ensures that resources are properly managed and released when the block is exited.
with HandLandmarker.create_from_options(options) as landmarker:
    # The landmarker is initialized. Use it here.
    while True:
        ok, frame = cap.read() # read a frame from the camera. The read() function returns two values:
                               # "ok" is a boolean indicating whether the frame was successfully captured, and "frame" is the actual image data captured from the camera.
        if not ok:
            break

        # Send the frame to the landmarker (it expects RGB, OpenCV gives BGR)
        # Convert the frame from BGR to RGB color space using cv2.cvtColor.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Create a MediaPipe Image object from the RGB frame, specifying the image format as SRGB and providing the pixel data.
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        # update the timestamp for the current frame by calculating the elapsed time since start_time, converting it to milliseconds
        timestamp_ms = int((time.monotonic() - start_time) * 1000)
        # send the MediaPipe Image and the timestamp to the landmarker for processing. 
        # The detect_async method processes the image asynchronously, allowing the program to continue running while waiting for the results.
        landmarker.detect_async(mp_image, timestamp_ms)

        ######### VERIFY FROM HERE #########

        # Draw the most recent result on top of the current frame
        # latest result is updated by the callback function store_result whenever a new result is available from the landmarker.
        if latest_result is not None:
            # create a variable to hold the height and width of the frame, which are used to scale the normalized landmark coordinates to pixel coordinates.
            height, width = frame.shape[:2] # [:2] means we only want the first two values of the shape tuple, which are height and width.
            for hand in latest_result.hand_landmarks:
                # landmarks are between 0 and 1, so scale them to pixel positions
                # recover the pixel coordinates of the hand landmarks by multiplying the normalized coordinates (between 0 and 1).
                points = [(int(lm.x * width), int(lm.y * height)) for lm in hand]
                # create a line between the start and end points of each connection in HAND_CONNECTIONS, using the corresponding pixel coordinates from points.
                # The line is drawn in green with a thickness of 2 pixels.
                # for start, end in HAND_CONNECTIONS [0:12]: # Use this line if you want to draw only the first 12 connections (the thumb and index finger)
                for start, end in HAND_CONNECTIONS:
                    # in FRAME, itrate through the HAND_CONNECTIONS list, use the [0] and [1] to get the start and end points of each connection.
                    cv2.line(frame, points[start], points[end], (0, 255, 0), 2)
                for point in points:
                    cv2.circle(frame, point, 4, (0, 0, 255), -1)

        cv2.imshow("Camera test", frame) # here "Camera test" is the name of the window that will display the camera feed,
                                         # "frame" is the variable that holds the current frame captured from the camera.
                                         # The imshow function displays the frame in a window.
        if cv2.waitKey(1) & 0xFF == ord("q"): # this line waits for a key press for 1 millisecond, and checks if the pressed key is "q". If "q" is pressed, it will exit the loop and stop displaying the camera feed.
            break # stop the loop if "q" is pressed

# ---------- Cleanup, after the landmarker block has closed ----------

cap.release() # stop the camera capture and release the camera resource
cv2.destroyAllWindows() # close all OpenCV windows that were opened during the program execution