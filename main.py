import pyautogui
import cv2 as cv
import mediapipe as mp
import time

last_slide_time = 0


mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils

hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

cam = cv.VideoCapture(0)
prev_x = 0
while True:
    success, frame = cam.read()

    if not success:
        break

    frame = cv.flip(frame, 1)

    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mpDraw.draw_landmarks(
                frame,
                hand,
                mpHands.HAND_CONNECTIONS
            )

            h, w, c = frame.shape

            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)

            cv.circle(frame, (x, y), 10, (0,255,0), -1)

            if prev_x != 0:

                diff = x - prev_x

                current_time = time.time()
                if current_time - last_slide_time > 1:

                    if diff > 120:
                        pyautogui.press("left")
                        cv.putText(frame, "PREVIOUS SLIDE",
                        (50,50),
                        cv.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,0,255),
                        3)
                        print("PREVIOUS")

                        last_slide_time = current_time
                        prev_x = 0

                    elif diff < -120:
                        pyautogui.press("right")
                        cv.putText(frame, "NEXT SLIDE",
                        (50,50),
                        cv.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,255,0),
                        3)
                        print("NEXT")

                        last_slide_time = current_time
                        prev_x = 0

            prev_x = x

    cv.imshow("Gesture Presentation", frame)

    key = cv.waitKey(1)

    if key == ord('q'):
        break

cam.release()
cv.destroyAllWindows()