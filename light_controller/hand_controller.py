import requests
import cv2
from cvzone.HandTrackingModule import HandDetector

token = "ce307b957f9d5b7a0a2c384e2bca457f01d13f29a3ae9f2ba49006fa1ff0eb18"

headers = {
    "Authorization": "Bearer %s" % token,
}

payload = {
    "power": "off",
}
payload2 = {
    "power": "on",
}

payloadbright = {
    "fast": True,
    "brightness": 0.5
}

vid = cv2.VideoCapture(0)
vid.set(3, 1920)
vid.set(4, 1080)
detector = HandDetector(detectionCon=0.8, maxHands=2)

while True:
    success, img = vid.read()
    img = cv2.flip(img, 1)
    if success == True:
        hands, img = detector.findHands(img, flipType=False)
        if hands:
            # Hand 1
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmark points
            bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
            centerPoint1 = hand1['center']  # center of the hand cx,cy
            #print(centerPoint1)
            handType1 = hand1["type"]  # Handtype Left or Right

            fingers1 = detector.fingersUp(hand1)

            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                lmList2 = hand2["lmList"]  # List of 21 Landmark points
                bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
                centerPoint2 = hand2['center']  # center of the hand cx,cy
                handType2 = hand2["type"]  # Hand Type "Left" or "Right"

                fingers2 = detector.fingersUp(hand2)

            if fingers1[1] == 1 and fingers1[2] == 1 and fingers1.count(1) == 2:
                response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)

            if fingers1[0] == 1 and fingers1.count(1) == 1:
                response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload2, headers=headers)


        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    else:
        break
    
vid.release()
cv2.destroyAllWindows()
