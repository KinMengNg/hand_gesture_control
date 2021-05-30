import cv2
import mediapipe as mp
import time
import math
import numpy as np

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),(0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        #1 means finger is up, 0 means its not
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):

            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def palmOpen(self, img):
        #if palm is open, distance ratio of tip of fingers to wrist to bottom of fingers to wrist should be about 2
        #ie, tip to wirst divided by bottom of finger to wrist should be around 2(besides thumb and pinky)

        #length of palm
        palm_len = self.findDistance(5, 0, img, draw=False)[0]

        #length of each tip of finger to palm
        palm_thumb = self.findDistance(4, 0, img, draw=False)[0]
        palm_index = self.findDistance(8, 0, img, draw=False)[0]
        palm_middle = self.findDistance(12, 0, img, draw=False)[0]
        palm_ring = self.findDistance(16, 0, img, draw=False)[0]
        palm_pinky = self.findDistance(20, 0, img, draw=False)[0]

        #get which fingers are up
        fingers = self.fingersUp()

##        print(palm_thumb/palm_len)
##        print(palm_index/palm_len)
##        print(palm_middle/palm_len)
##        print(palm_ring/palm_len)
##        print(palm_pinky/palm_len)
        
                                                                                                                                                                #index, middle and ring is up
        if palm_thumb/palm_len > 1.3 and palm_index/palm_len > 1.7 and palm_middle/palm_len > 1.8 and palm_ring/palm_len > 1.7 and palm_pinky/palm_len > 1.4 and (fingers[1], fingers[2], fingers[3]) == (1,1,1):
            return True
        else:
            return False

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if len(lmList) != 0:
            #print(lmList[4])
            print(detector.palmOpen(img))  
            #print(lmList)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 255), 3)

        cv2.imshow('Image', img)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            cap.release()
            cv2.destroyAllWindows()
            break
if __name__ == '__main__':
    main()
