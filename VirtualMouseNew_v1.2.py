#Added specific miouse area centred by open palm
import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui


wCam, hCam = 640, 480
wScr, hScr = pyautogui.size()
#print(wScr, hScr)
SCwidth_ratio = wScr/wCam #SC for Screen Cam
SCheight_ratio = hScr/hCam

#so no errors
left = 0
right = 0
top = 0
bottom = 0


pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)

# print(wScr, hScr)

last_frame_clicked = False

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #if there is a hand detected
    if len(lmList) != 0:
        # 2. Get the tip of the index and middle fingers
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        #distance tip index to wirst
        dist = detector.findDistance(8, 0, img, draw=False)[0]

        #Check if palm is open
        palm = detector.palmOpen(img)
        if palm == True:
            print('Recalibrating...')
            #center the tracktable area to the tip of my index finger,
            #and make it just the height and width of tip to wrist
                 
            #cannot do int here cause affect accuracy that is multiplied and cause exponential error later on
            left = x1 - dist #leftmost coordinatye
            top = y1 - dist/2 #top most
            right = x1 + dist #rightmost
            bottom = y1 + dist/2 #bottom most

            #set ratio
            width_ratio = wCam/(2*dist) #NEED TIMES 2, I MINUSED TO THE LEFT, THAN PLUSED THE LENGTH TO THE RIGHT
            height_ratio = hCam/(dist) #cause 2* dist/2 is dist
            #print(width_ratio, height_ratio)

            cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), (255, 0, 255), 2)  

        try: #cause first iteration not defined
            cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), (255, 0, 255), 2)
        except:
            pass

        #only run the code if my hand is in the trackzone i just defined above        
        if  (left <= x1 <= right) and (top <= y1 <= bottom):   
            # 3. Check which fingers are up
            fingers = detector.fingersUp()
            # print(fingers)

            # 4. Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:
                #when i finally put down my middle finger,
                last_frame_clicked = False
                pyautogui.mouseUp()
                
                # 5. Convert Coordinates
                #my own way, using ratio

                #relative zero(to the trackpad) is the top left corner of the trackpad
                #x3 and y3 are the coordinates of the mouse pointer to the cam
                #minus to get the actual relative distance from (0,0)
                x3 = (x1 - left) * width_ratio
                y3 = (y1 - top) * height_ratio

                #x4 amd y4 are the actual coordinates on the real screen
                x4 = x3*SCwidth_ratio
                y4 = y3*SCheight_ratio
                
                #print(x4, y4)
                pyautogui.moveTo(x4, y4)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # 8. Both Index and middle fingers are up ONLY: Clicking Mode
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                # 9. Find distance between fingers
                length, img, lineInfo = detector.findDistance(8, 12, img)
                
                # 10. Click mouse if distance short
                if length < 20:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)

                    print('Left Click:',length)

                    #check if we clicked on last frame                
                    if last_frame_clicked == False:
                        pyautogui.mouseDown()
                        last_frame_clicked = True

                    #if we did, and still hpolding this position, means want to drag
                    elif last_frame_clicked == True:
                        # 5. Convert Coordinates
                        #my own way, using ratio

                        #relative zero(to the trackpad) is the top left corner of the trackpad
                        #x3 and y3 are the of the mouse pointer to the cam
                        #minus to get the actual relative distance from (0,0)
                        x3 = (x1 - left) * width_ratio
                        y3 = (y1 - top) * height_ratio

                        #x4 amd y4 are the actual coordinates on the real screen
                        x4 = x3*SCwidth_ratio
                        y4 = y3*SCheight_ratio

                        # 7. Drag Mouse, since mouse still down
                        pyautogui.moveTo(x4, y4)
                        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                        
            #if 3 fingers up: Right click
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                # 9. Find distance between index and ring finger
                length, img, lineInfo = detector.findDistance(8, 16, img)
                
                # 10. Click mouse if distance short
                if length < 30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)

                    print('Right Click:',length)
                    pyautogui.click(button='right')
                    


    
    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    if (cv2.waitKey(1) & 0xFF == ord('|')):
        cap.release()
        cv2.destroyAllWindows()
        break

    #Slight delay, so not so erratic
    #time.sleep(0.01)
