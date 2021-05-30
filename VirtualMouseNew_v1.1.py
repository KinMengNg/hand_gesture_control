#Added drag and right click
import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui


##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 2
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()
# print(wScr, hScr)

last_frame_clicked = False

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            #when i finally put down my middle finger,
            last_frame_clicked = False
            pyautogui.mouseUp()
            
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            #autopy.mouse.move(wScr - clocX, clocY)
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Both Index and middle fingers are up ONLY: Clicking Mode
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print('Left Click:',length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)

                #check if we clicked on last frame                
                if last_frame_clicked == False:
                    #autopy.mouse.click()
                    pyautogui.mouseDown()
                    last_frame_clicked = True

                #if we did, and still hpolding this position, means want to drag
                elif last_frame_clicked == True:
                    # 5. Convert Coordinates
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                    # 6. Smoothen Values
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening

                    # 7. Drag Mouse, since mouse still down
                    pyautogui.moveTo(wScr-clocX, clocY)
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY

        #if 3 fingers up: Right click
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            # 9. Find distance between index and ring finger
            length, img, lineInfo = detector.findDistance(8, 16, img)
            print('Right Click:',length)
            # 10. Click mouse if distance short
            if length < 70:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                
                #autopy.mouse.click()
                pyautogui.click(button='right')
                

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. Display
    img = cv2.flip(img, 1)
    cv2.imshow("Image", img)
    if (cv2.waitKey(1) & 0xFF == ord('|')):
        cap.release()
        cv2.destroyAllWindows()
        break

    #Slight delay, so not so erratic
    time.sleep(0.01)
