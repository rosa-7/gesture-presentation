import pyautogui
import cv2 as cv
import mediapipe as mp
import time


# ─────────────────────────────────────────────
#  HUD overlay function
# ─────────────────────────────────────────────
def draw_hud(frame, gesture_name, fps):
    overlay = frame.copy()
    cv.rectangle(overlay, (0, 0), (frame.shape[1], 60), (0, 0, 0), -1)
    cv.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    cv.putText(frame, f"Gesture: {gesture_name}", (10, 35),
               cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 120, 35),
               cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)


# ─────────────────────────────────────────────
#  MediaPipe setup
# ─────────────────────────────────────────────
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils

hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

# ─────────────────────────────────────────────
#  Variables
# ─────────────────────────────────────────────
cam = cv.VideoCapture(0)

prev_x = 0
last_slide_time = 0
gesture_symbol = ""
gesture_time = 0

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────
while True:

    success, frame = cam.read()

    if not success:
        print("Camera not working")
        break

    # Mirror effect
    frame = cv.flip(frame, 1)

    # Convert to RGB
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Hand detection
    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            # Draw hand landmarks
            mpDraw.draw_landmarks(
                frame,
                hand,
                mpHands.HAND_CONNECTIONS
            )

            # Frame dimensions
            h, w, c = frame.shape

            # Index fingertip coordinates
            x = int(hand.landmark[8].x * w)
            y = int(hand.landmark[8].y * h)

            # Draw fingertip point
            cv.circle(frame, (x, y), 10, (0, 255, 0), -1)

            # Swipe detection
            if prev_x != 0:

                diff = x - prev_x

                current_time = time.time()

                # 1 second cooldown
                if current_time - last_slide_time > 1:

                    # Swipe right → previous slide
                    if diff > 120:

                        pyautogui.press("left")

                        cv.circle(frame, (80, 80), 30, (0, 0, 255), -1)

                        cv.putText(
                        frame,
                        "<",
                        (68, 92),
                        cv.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        3
                        )

                        gesture_symbol = "prev"
                        gesture_time = time.time()

                        print("PREVIOUS")

                        last_slide_time = current_time
                        prev_x = 0

                    # Swipe left → next slide
                    elif diff < -120:

                        pyautogui.press("right")

                        cv.circle(frame, (80, 80), 30, (0, 255, 0), -1)

                        cv.putText(
                        frame,
                        ">",
                        (68, 92),
                        cv.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        3
                        )

                        gesture_symbol = "next"
                        gesture_time = time.time()

                        print("NEXT")

                        last_slide_time = current_time
                        prev_x = 0

            # Update previous x
            prev_x = x

    # Show webcam window
    # Show gesture symbol for 0.5 seconds

    if time.time() - gesture_time < 0.5:

        if gesture_symbol == "next":

            cv.circle(frame, (80, 80), 30, (0, 255, 0), -1)

            cv.putText(
                frame,
                ">",
                (68, 92),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                3
                )

        elif gesture_symbol == "prev":

            cv.circle(frame, (80, 80), 30, (0, 0, 255), -1)

            cv.putText(
                frame,
                "<",
                (68, 92),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                3
                )
    cv.imshow("Gesture Controlled Presentation", frame)

    key = cv.waitKey(1)

    # Quit
    if key == ord('q'):
        break

# Cleanup
cam.release()
cv.destroyAllWindows()