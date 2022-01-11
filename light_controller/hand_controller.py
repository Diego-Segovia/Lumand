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
    MIN_DIST = 0.15

    # Finger and wrsit (x,y) coordinates
    index_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y])

    middle_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y])

    ring_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y])

    pinky_finger = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].x, 
                            results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.PINKY_TIP].y])

    wrist = np.array([results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].x, 
                    results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].y])

    # Calcuating Euclidean distance between wrist and fingers
    dist_index = np.linalg.norm(index_finger-wrist)
    dist_middle = np.linalg.norm(middle_finger-wrist)
    dist_ring = np.linalg.norm(ring_finger-wrist)
    dist_pinky = np.linalg.norm(pinky_finger-wrist)

    # Check if all fingers are the minimum distance from wrist
    if dist_index < MIN_DIST and dist_middle < MIN_DIST and dist_ring < MIN_DIST and dist_pinky < MIN_DIST:
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

        if results.multi_hand_landmarks:
            #print(results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].y)
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw finger and joint marks on image
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            if is_fist(results):
                light.turn_off()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imshow('Lumand', cv2.flip(image, 1))

        #press ESC key to exit
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()