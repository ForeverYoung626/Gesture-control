import mediapipe as mp
import cv2
import numpy as np
import math
import keyboard as kb
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

# function to calculate angle of 2 vectors
def angle_of_vec(v1, v2):
    try:
        angle= math.degrees(math.acos((v1[0]*v2[0] + v1[1]*v2[1]) / (( (v1[0]**2 + v1[1]**2)**0.5) * ( (v2[0]**2 + v2[1]**2)**0.5) )))
    except:
        angle = 180
    return angle

def closed_fingers(point):
    angles = []
    for i in range(1, 18, 4):
        v1 = [point[0].x - point[i+1].x, point[0].y - point[i+1].y]
        v2 = [point[i+3].x - point[i+2].x, point[i+3].y - point[i+2].y]
        angles.append(angle_of_vec(v1, v2))
    # index finger is closed
    closed = []
    for i in range(5):
        if angles[i] < 135:
            closed.append(i)
    
    return closed
        
def input_keyboard(p0, p1, g0, g1):
    x_dif = p1.x - p0.x
    y_dif = p1.y - p0.y

    if g1 == "0":
        if g0 == "1":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("!")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send(" ")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("?")
            elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                return "selection"
        elif g0 == "2":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("a")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("b")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("c")
        elif g0 == "3":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("d")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("e")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("f")
        elif g0 == "4":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("g")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("h")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("i")
        elif g0 == "5":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("j")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("k")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("l")
        elif g0 == "6":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("m")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("n")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("o")
        elif g0 == "7":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("p")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("q")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("r")
            elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                kb.send("s")
        elif g0 == "8":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("t")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("u")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("v")
        elif g0 == "9":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                kb.send("w")
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                kb.send("x")
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                kb.send("y")
            elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                kb.send("z")
        elif g0 == "0":
            if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                print()
            elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                print()
            elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                print()

    return "keyboard & mouse"

def get_gesture(landmarks):
    closed = closed_fingers(landmarks)
    gesture = ''
    if closed == [0, 2, 3, 4]: # gesture "1"
        cv2.putText(frame, text='1', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "1"
    elif closed == [0, 3, 4]: # gesture "2"
        cv2.putText(frame, text='2', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "2"
    elif closed == [0, 4]: # gesture "3"
        cv2.putText(frame, text='3', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "3"
    elif closed == [0]: # gesture "4"
        cv2.putText(frame, text='4', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "4"
    elif closed == []: # gesture "5"
        cv2.putText(frame, text='5', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "5"
    elif closed == [1, 2, 3]: # gesture "6"
        cv2.putText(frame, text='6', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "6"
    elif closed == [2, 3, 4]: # gesture "7"
        cv2.putText(frame, text='7', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "7"
    elif closed == [3, 4]: # gesture "8"
        cv2.putText(frame, text='8', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "8"
    elif closed == [4]: # gesture "9"
        cv2.putText(frame, text='9', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "9"
    elif closed == [0, 1, 2, 3, 4]: # gesture "0"
        cv2.putText(frame, text='0', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "0"
    elif closed == [1]: # gesture "Okay"
        cv2.putText(frame, text='Okay', org=(300, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 0, 0), fontScale=2, lineType=cv2.LINE_AA)
        gesture = "okay"

    return gesture
        
cap = cv2.VideoCapture(0)
last_pos = None # record position of hand in last run
last_gesture = None
cam_width = cap.get(3) # width
cam_height = cap.get(4) # height
mode = 'selection'

while cap.isOpened():
    success, frame = cap.read()

    # miror the frame 
    frame = cv2.flip(frame, 1)
    results = hands.process(frame)
    
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            handedness = results.multi_handedness[results.multi_hand_landmarks.index(landmarks)].classification[0].label
            mp_drawing.draw_landmarks( frame, landmarks, mp_hands.HAND_CONNECTIONS)
        
            hand_pos = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            gesture = get_gesture(landmarks.landmark)
            
            if mode == 'keyboard & mouse':
                if handedness == "Right":
                    if last_pos and hand_pos and last_gesture and gesture and last_gesture != gesture:
                        mode = input_keyboard(last_pos, hand_pos, last_gesture, gesture)
                        
                    last_gesture = gesture
                    last_pos = hand_pos
                
                elif handedness == "Left": 
                    cursor_x = int(hand_pos.x * screen_width)
                    cursor_y = int(hand_pos.y * screen_height)

                    pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)

                    # current_dist = index_tip.y - index_mid.y
                    closed = closed_fingers(landmarks.landmark)
                    if 1 in closed:
                        pyautogui.click()
            
            elif mode == 'selection':
                if gesture == '0':
                    if last_gesture == '2':
                        mode = 'keyboard & mouse'
                    elif last_gesture == '3':
                        mode = 'PPT'
                last_gesture = gesture
                print(mode, gesture)
                
    
    cv2.imshow('Gesture Recognition', frame)
    
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()

