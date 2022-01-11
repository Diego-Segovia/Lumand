import os
import cv2
import mediapipe as mp
import numpy as np
from dotenv import load_dotenv
from light_ctrl import LightController

load_dotenv()

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

TOKEN = os.getenv('TOKEN')

light = LightController(TOKEN)

def is_fist(results):
    # Minimum distance fingers need to be from wrist
    MIN_DIST = 0.17

    # Finger and wrsit (x,y) coordinates
    middle_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y])

    ring_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y])

    pinky_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].y])

    wrist = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].x, 
                    results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].y])

    # Calcuating Euclidean distance between wrist and fingers
    dist_middle = np.linalg.norm(middle_finger-wrist)
    dist_ring = np.linalg.norm(ring_finger-wrist)
    dist_pinky = np.linalg.norm(pinky_finger-wrist)

    # Check if all fingers are the minimum distance from wrist
    if dist_middle < MIN_DIST and dist_ring < MIN_DIST and dist_pinky < MIN_DIST:
        return True

    return False

def is_three_finger_pinch(results):
    # Minimum distance between thumb, ring, and middle finger
    MIN_DIST = 0.1

    middle_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y])

    ring_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y])

    thumb = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.THUMB_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.THUMB_TIP].y])

    dist_middle = np.linalg.norm(middle_finger-thumb)
    dist_ring = np.linalg.norm(ring_finger-thumb)

    if dist_middle < MIN_DIST and dist_ring < MIN_DIST:
        return True

    return False

def is_two_finger(results):
    # Minimum distance between index and middle finger
    MIN_DIST_FINGERS_UP = 0.1
    # Minimum distance between ring and pink finger and wrist
    MIN_DIST_FINGERS_DOWN = 0.3

    middle_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y])

    index_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y])

    ring_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y])

    pinky_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].y])

    wrist = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].x, 
                    results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].y])

    dist_middle_index = np.linalg.norm(middle_finger-index_finger)
    dist_pinky_wrist = np.linalg.norm(pinky_finger-wrist)
    dist_ring_wrist = np.linalg.norm(ring_finger-wrist)

    if dist_middle_index < MIN_DIST_FINGERS_UP and dist_pinky_wrist < MIN_DIST_FINGERS_DOWN and dist_ring_wrist < MIN_DIST_FINGERS_DOWN:
        return True

    return False

# For webcam input:
cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()

        # Ignoring empty camera frame.
        if not success:
            continue

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True

        # Index finger x coordinate used for brightness change
        index_finger_x = None

        # Flags for light state changes
        was_turned_off = False
        was_turned_on = False
        had_brightness_changed = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw finger and joint marks on image
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            # Turn light off if fist is detected
            if is_fist(results):
                light.turn_off(go_fast=True)
                was_turned_off = True

            if is_three_finger_pinch(results):
                light.turn_on(go_fast=True)
                was_turned_on = True

            # Enter brightness mode if index and middle finger raised is detected
            if is_two_finger(results):
                # Get index finger x coordinate minus 1 to account for image flip
                index_finger_x = round(1 - results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x, 1)
                light.set_brightness(index_finger_x, go_fast=True)
                had_brightness_changed = True

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)

        # Add text to image based on light state changes
        if had_brightness_changed:
            cv2.putText(image, 'Brightness: ' + str(int(index_finger_x * 100)) + '%', (50, 50), cv2.FONT_HERSHEY_DUPLEX, 
                    1, (255, 195, 0), 2, cv2.LINE_AA)
        
        if was_turned_on:
            cv2.putText(image, 'Light On', (50, 50), cv2.FONT_HERSHEY_DUPLEX, 
                   1, (247, 255, 71), 2, cv2.LINE_AA)

        if was_turned_off:
            cv2.putText(image, 'Light Off', (50, 50), cv2.FONT_HERSHEY_DUPLEX, 
                   1, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('Lumand', image)

        #press ESC key to exit
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()