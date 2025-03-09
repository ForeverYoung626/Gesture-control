import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import cv2
import mediapipe as mp
from PIL import Image, ImageTk

import math
import keyboard as kb
import pyautogui
import datetime

class HandGestureGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Recognition GUI")

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.screen_width, self.screen_height = pyautogui.size()
        # self.prev_time = datetime.datetime.now()
        # self.cur_time = self.prev_time
        self.min_time_diff = 0.3
        self.mouse_acc = False

        self.cap = None
        self.running = False
        self.current_mode = "Selection"
        self.cam_width = 640 # width
        self.cam_height = 480 # height
        self.cur_pos = None
        self.last_pos = None
        # self.last_gesture = None
        # self.temp_gesture = None
        self.cur_gesture = None        

        # Video frame label
        self.video_label = tk.Label(self.root, background='#000')
        self.video_label.pack()

        # Mode selection dropdown
        self.modes = ["Selection", "Keyboard & Mouse", "PPT"]
        self.mode_var = tk.StringVar(value=self.modes[0])
        self.mode_dropdown = ttk.Combobox(self.root, textvariable=self.mode_var, values=self.modes, state="readonly")
        self.mode_dropdown.pack(pady=10)
        self.mode_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_mode(self.mode_var.get()))

        # Mode label
        self.mode_label = tk.Label(self.root, text=f"Current Mode: {self.current_mode}")
        self.mode_label.pack(pady=10)

        # Control buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop Camera", command=self.stop_camera)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Close button
        self.close_button = tk.Button(self.root, text="Exit", command=self.on_close)
        self.close_button.pack(pady=10)

        # Handle application close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_camera(self):
        if self.running:
            messagebox.showinfo("Info", "Camera is already running!")
            return
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to access the camera!")
            return
        self.running = True
        threading.Thread(target=self.process_video, daemon=True).start()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def process_video(self):
        hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        while self.running:
            success, frame = self.cap.read()
            if not success:
                messagebox.showerror("Error", "Failed to get camera frame!")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            prev_time = datetime.datetime.now()
            temp_gesture = ''
            gesture = ''
            last_gesture = ''
            last_pos = None

            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    handedness = results.multi_handedness[results.multi_hand_landmarks.index(landmarks)].classification[0].label
                    self.mp_drawing.draw_landmarks( frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                    hand_pos = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                    cur_gesture = self.get_gesture(landmarks.landmark)
                    cur_time = datetime.datetime.now()
                    diff_time = cur_time - prev_time

                    if diff_time.total_seconds() >= self.min_time_diff and cur_gesture == temp_gesture:
                        gesture = cur_gesture
                        prev_time = cur_time
                    elif temp_gesture != cur_gesture:
                        prev_time = cur_time
                        last_pos = hand_pos
                    temp_gesture = cur_gesture
                                        
                    if self.current_mode == 'Keyboard & mouse':
                        if handedness == "Right":
                            if last_pos and hand_pos and last_gesture and gesture and last_gesture != gesture:
                                self.current_mode = self.keyboard_action(last_pos, hand_pos, last_gesture, gesture)
                        elif handedness == "Left" and mouse_acc: 
                            if gesture == '5':
                                self.mouse_move(last_pos, hand_pos)

                            # current_dist = index_tip.y - index_mid.y
                            closed = self.closed_fingers(landmarks.landmark)
                            if 1 in closed:
                                pyautogui.click()
                    elif self.current_mode == 'Selection':
                        if gesture == '0':
                            if last_gesture == '2':
                                self.update_mode('Keyboard & mouse')
                            elif last_gesture == '3':
                                self.update_mode('PPT')
                            elif last_gesture == '5':
                                kb.send("win + tab")
                            elif last_gesture == '7':
                                kb.send("alt + tab")
                    elif self.current_mode == 'PPT':
                        if handedness == "Right":
                            if last_pos and hand_pos and last_gesture and gesture and last_gesture != gesture:
                                self.current_mode = self.ppt_action(last_pos, hand_pos, last_gesture, gesture)
                        elif handedness == "Left" and mouse_acc: 
                            self.mouse_move(last_pos, hand_pos)

                    if last_gesture != gesture:
                        print(self.current_mode, last_gesture, gesture, hand_pos.x - last_pos.x, hand_pos.y - last_pos.y)    
                    last_gesture = gesture
                    
                print(gesture, hand_pos)
            
            # Convert to Tkinter-compatible format
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update video frame
            self.video_label.configure(image=imgtk)

        hands.close()

    def update_mode(self, selected_mode):
        self.current_mode = selected_mode
        self.mode_dropdown.set(selected_mode)
        self.mode_label.config(text=f"Current Mode: {self.current_mode}")

    def on_close(self):
        self.stop_camera()
        self.root.destroy()
    
    def angle_of_vec(self, v1, v2):
        try:
            angle = math.degrees(math.acos((v1[0] * v2[0] + v1[1] * v2[1]) / (( (v1[0]**2 + v1[1]**2)**0.5) * ( (v2[0]**2 + v2[1]**2)**0.5) )))
        except:
            angle = 180
        return angle
    
    def closed_fingers(self, point):
        angles = []
        for i in range(1, 18, 4):
            v1 = [point[0].x - point[i+1].x, point[0].y - point[1].y]
            v2 = [point[i+3].x - point[i+2].x, point[i+3].y - point[i+2].y]
            angles.append(self.angle_of_vec(v1, v2))
        
        closed = [] # index of closed fingers
        for i in range(5):
            if angles[i] < 135:
                closed.append(i)
        
        return closed

    def get_gesture(self, landmarks): # function which defines gesture
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
        elif closed == [1]: # gesture "Okay"
            gesture = "okay"

        return gesture

    def mouse_move(self, p0, p1):
        x = int(p1.x - p0.x) * self.cam_width 
        y = int(p1.y - p0.y) * self.cam_width 
        pyautogui.moveRel(x, y) 
        
    def keyboard_action(self, p0, p1, g0, g1):
        x_dif = (p1.x - p0.x) * self.cam_width
        y_dif = (p1.y - p0.y) * self.cam_height
        
        if g1 == "0":
            if g0 == "1":
                if x_dif < 0 and abs(x_dif) < abs(y_dif):
                    kb.send("shift")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send(" ")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("capslock")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    self.update_mode("Selection")
            elif g0 == "2":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("a")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("b")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("c")
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    global mouse_acc
                    mouse_acc = not mouse_acc               
            elif g0 == "3":
                if x_dif > 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("d")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("e")
                elif x_dif < 0 and abs(x_dif) > abs(y_dif): # moving right
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

    def ppt_action(self, p0, p1, g0, g1):
        x_dif = (p1.x - p0.x) * self.cam_width
        y_dif = (p1.y - p0.y) * self.cam_height
        
        if g1 == "0":
            if g0 == "1":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    return "selection"
            elif g0 == "2":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("ctrl + L") # start using laser pen
                    print("laser pen")
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    kb.send("ctrl + H") # hide mouse pointer
                    print("hide mouse")
            elif g0 == "3":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("ctrl + P") # start using pen
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("ctrl + E")
                    print("using eraser")
            elif g0 == "4":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
            elif g0 == "5":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    kb.send("P") # previos slide
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving up
                    kb.send("esc") # end PPT
                    print("stop PPT")
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    kb.send("N") # next slide
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving down
                    kb.send("shift + f5") # play PPT
                    print("play PPT")
            elif g0 == "6":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
            elif g0 == "7":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    print()
            elif g0 == "8":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
            elif g0 == "9":
                if x_dif < 0 and abs(x_dif) > abs(y_dif): # moving left
                    print()
                elif y_dif > 0 and abs(x_dif) < abs(y_dif): # moving up
                    print()
                elif x_dif > 0 and abs(x_dif) > abs(y_dif): # moving right
                    print()
                elif y_dif < 0 and abs(x_dif) < abs(y_dif): # moving down
                    print()
        


root = tk.Tk()
app = HandGestureGUI(root)
root.mainloop()
