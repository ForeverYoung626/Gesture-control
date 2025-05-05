import mediapipe as mp
import cv2
import math
import keyboard as kb
import pyautogui
import datetime
import threading
from PIL import Image, ImageTk
from tkinter import messagebox

class Gesture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        self.screen_width, self.screen_height = pyautogui.size()
        # self.prev_time = datetime.datetime.now()
        # self.cur_time = self.prev_time
        self.min_time_diff = 0.3
        self.mouse_acc = False
        self.running = False

        self.cap = cv2.VideoCapture(0)
        self.cam_width = 640  # self.cap.get(3)
        self.cam_height =360 #  self.cap.get(4)
        self.cap.release() 
        self.current_mode = "Selection"
        self.pos = None
        self.prev_time = datetime.datetime.now()
        self.last_pos = None
        self.gesture = '0'
        self.last_gesture = '0'
        self.temp_gesture = None
        self.det_gesture = None
        # self.test = '0'
        self.sensitivity = 0.7
        
        self.draw_landmark = True
        self.show_camera = False
        
        pyautogui.FAILSAFE = False
        
    def show_skeleton(self, b):
        self.draw_landmark = b

    def show_cam(self, b):
        self.show_camera = b

    def start_camera(self, video_label):
        if self.running: 
            print("running")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("unable")

        self.running = True
        threading.Thread(target=self.process_vidoe, args=(video_label, ), daemon=True).start() 

    def stop_camera(self, lbl):
        self.running = False
        if self.cap:
            self.cap.release()
        lbl.configure(image=None)
        lbl.image = None
        
    def process_vidoe(self, video_label):
        self.prev_time = datetime.datetime.now()
        det_pos = None
        temp_pos = None
        while self.running:
            success, frm = self.cap.read()
            if not success:
                print("Faile to get camera")
                messagebox.showerror("Error", "Failed to get camera frame!")
                break
            
            frm = cv2.flip(frm, 1)
            rgb_frm = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frm)

            
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks[0:1]:
                    handedness = results.multi_handedness[results.multi_hand_landmarks.index(landmarks)].classification[0].label
                    if self.draw_landmark:
                        self.mp_drawing.draw_landmarks( frm, landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                    self.temp_gesture = self.det_gesture
                    det_pos = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                    self.det_gesture = self.get_gesture(landmarks.landmark)
                    cur_time = datetime.datetime.now()
                    diff_time = (cur_time - self.prev_time).total_seconds()
                    

                    # 偵測手勢不爲空
                    if self.temp_gesture != "": 
                        if diff_time >= self.min_time_diff:
                            self.gesture = self.temp_gesture
                            self.last_pos = self.pos
                            self.pos = det_pos
                            self.temp_gesture = self.det_gesture
                            self.prev_time = cur_time
                        elif self.det_gesture != self.temp_gesture:            
                            self.temp_gesture = self.det_gesture
                            self.prev_time = cur_time

                    if self.gesture != self.last_gesture:
                        print("gesture: ", self.gesture, "\nlast gesture: ", self.last_gesture, "\ncurrent mode: ", self.current_mode)

                    if self.current_mode == "Mouse" or self.mouse_acc: 
                        if (self.gesture == '5' or self.gesture == 'left click' or self.gesture == 'right click') and temp_pos:
                            if temp_pos:
                                self.mouse_move(temp_pos, det_pos)
                        elif self.gesture == '0' and self.last_gesture == '1':
                            self.set_mode("Selection")
                        elif self.gesture == 'left click':
                            pyautogui.mouseDown(button="left")
                        elif self.gesture == 'right click':
                            pyautogui.mouseDown(button='right')
                        # if self.gesture == '5':
                        #     pyautogui.mouseUp(button="left")
                        #     pyautogui.mouseUp(button="right")
                    if not (self.last_pos and det_pos and self.last_gesture and self.gesture ):
                        continue  
                    if self.current_mode == 'Keyboard' and self.last_gesture != self.gesture:
                        self.input_keyboard(self.last_pos, self.pos, self.last_gesture, self.gesture)
                    elif self.current_mode == 'Selection':
                        if self.gesture == '0':
                            if self.last_gesture == '2':
                                self.set_mode('Keyboard')
                            elif self.last_gesture == '3':
                                self.set_mode("Mouse")
                            elif self.last_gesture == '4':
                                self.set_mode('PPT')
                            elif self.last_gesture == '5':
                                kb.send("win + tab")
                            elif self.last_gesture == '7':
                                kb.send("alt + tab")
                    elif self.current_mode == 'PPT':
                        self.ppt_control(self.last_pos, self.pos, self.last_gesture, self.gesture)
                                
            self.last_gesture = self.gesture
            temp_pos = det_pos

            # Convert to Tkinter-compatible format
            img = cv2.cvtColor(frm, cv2.COLOR_RGBA2BGR)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update video frame
            if video_label != None and self.show_camera and self.running:
                video_label.configure(image=imgtk)
                video_label.image = imgtk
            else:
                video_label.configure(image=None)
                video_label.image = None

    def set_mode(self, selected_mode):
        self.current_mode = selected_mode
        if selected_mode == "Mouse":
            self.mouse_acc = True
        else:
            self.mouse_acc = False

    # function to calculate angle of 2 vectors
    def angle_of_vec(self, v1, v2):
        try:
            angle= math.degrees(math.acos((v1[0]*v2[0] + v1[1]*v2[1]) / (( (v1[0]**2 + v1[1]**2)**0.5) * ( (v2[0]**2 + v2[1]**2)**0.5) )))
        except:
            angle = 180
        return angle
    
    # return closed fingers in a list
    def closed_fingers(self, point): 
        angles = []
        for i in range(1, 18, 4): # 計算第一指節及第三指節之間的夾角
            v1 = [point[0].x - point[i+1].x, point[0].y - point[i+1].y]
            v2 = [point[i+3].x - point[i+2].x, point[i+3].y - point[i+2].y]
            angles.append(self.angle_of_vec(v1, v2))
        # index finger is closed
        closed = []
        for i in range(5):
            if angles[i] < 135:
                closed.append(i)
        
        return closed

    def get_gesture(self, landmarks):
        closed = self.closed_fingers(landmarks)
        gesture = ''
        if closed == [0, 2, 3, 4]: # gesture "1"
            gesture = "1"
        elif closed == [0, 3, 4]: # gesture "2"
            gesture = "2"
        elif closed == [0, 4]: # gesture "3"
            gesture = "3"
        elif closed == [0]: # gesture "4"
            gesture = "4"
        elif closed == []: # gesture "5"
            gesture = "5"
        elif closed == [1, 2, 3]: # gesture "6"
            gesture = "6"
        elif closed == [2, 3, 4]: # gesture "7"
            gesture = "7"
        elif closed == [3, 4]: # gesture "8"
            gesture = "8"
        elif closed == [4]: # gesture "9"
            gesture = "9"
        elif closed == [0, 1, 2, 3, 4]: # gesture "0"
            gesture = "0"
        elif closed == [1]: 
            gesture = "left click"
        elif closed == [2]: 
            gesture = "right click"
            

        return gesture

    # function to decide what to do in keyboard mode
    def input_keyboard(self, p0, p1, g0, g1): 
        x_dif = (p1.x - p0.x) * self.cam_width
        y_dif = (p1.y - p0.y) * self.cam_height

        if g1 == "0":
            if g0 == "1":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("shift")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send(" ")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("capslock")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    self.set_mode("Selection")
                    return
            elif g0 == "2":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("a")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("b")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("c")
             
            elif g0 == "3":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("d")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("e")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("f")
            elif g0 == "4":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("g")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("h")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("i")
            elif g0 == "5":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("j")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("k")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("l")
            elif g0 == "6":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("m")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("n")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("o")
            elif g0 == "7":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("p")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("q")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("r")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    kb.send("s")
            elif g0 == "8":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("t")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("u")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("v")
            elif g0 == "9":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("w")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("x")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("y")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    kb.send("z")
            elif g0 == "0":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
    
    def ppt_control(self, p0, p1, g0, g1): # 
        x_dif = int(p1.x * self.cam_width - p0.x * self.cam_width)
        y_dif = int(p1.y * self.cam_height - p0.y * self.cam_height)
        if g1 == "0" and g0 != '0':
            print(g0, g1, x_dif, y_dif)
            # print(g0, g1, p0, p1)
            if g0 == "1":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("ctrl + L") # start using laser pen
                    self.mouse_acc = False
                    print("laser pen")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("ctrl + L") # start using laser pen
                    self.mouse_acc = True
                    print("laser pen")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    self.set_mode("Selection")
            elif g0 == "2":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("ctrl + H") # hide mouse pointer
                    print("hide mouse")
                    self.mouse_acc = False
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("ctrl + A") # hide mouse pointer
                    print("show mouse")
                    self.mouse_acc = True
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    print()
            elif g0 == "3":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("ctrl + P") # start using pen
                    print("hide pen")
                    self.mouse_acc = False
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("ctrl + P")
                    print("using pen")
                    self.mouse_acc = True
            elif g0 == "4":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("esc") # end PPT
                    print("stop PPT")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print('4 : moving up')
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("shift + f5") # play PPT
                    print("play PPT") 
                elif y_dif > 0 and abs(x_dif) < abs(y_dif):
                    print("4 : moving down")
            elif g0 == "5":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("p") # previos slide
                    print('previos slide')
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    print("5 : moving up")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("n") # next slide
                    print("next slide")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    print("5 : moving down")
    
    def mouse_move(self, p0, p1):
        # print(p0, p1)
        x = int((p1.x - p0.x) * self.screen_width * self.sensitivity)
        y = int((p1.y - p0.y) * self.screen_height * self.sensitivity)
        # print("mouse move function is runing.\n(x, y) = ( ", x, ", ", y, ")")
        pyautogui.moveRel(x, y)
        # pyautogui.moveTo(x=int(p1.x * self.screen_width), y=int(p1.y * self.screen_height))
        