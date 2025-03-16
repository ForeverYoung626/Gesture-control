import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from recognition import Gesture

class HandGestureGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Recognition GUI")
        
        self.ges = Gesture()

        # Video frame label
        self.video_frm = tk.Frame(self.root, width=self.ges.cam_width, height=self.ges.cam_height, bg="black")
        self.video_frm.pack_propagate(0)
        self.video_label = tk.Label(self.video_frm, background='black')
        self.video_label.pack()
        self.video_frm.pack()

        # Mode selection dropdown
        self.modes = ["Selection", "Keyboard", "Mouse", "PPT"]
        self.mode_var = tk.StringVar(value=self.modes[0])
        self.mode_dropdown = ttk.Combobox(self.root, textvariable=self.mode_var, values=self.modes, state="readonly")
        self.mode_dropdown.pack(pady=10)
        self.mode_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_mode(self.mode_var.get()))

        # Mode label
        self.mode_label = tk.Label(self.root, text=f"Current Mode: {self.ges.current_mode}")
        self.mode_label.pack(pady=10)

        # Control buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Camera", command=lambda: self.ges.start_camera(self.video_label))
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop Camera", command=lambda: self.ges.stop_camera())
        self.stop_button.grid(row=0, column=1, padx=5)

        # Close button
        self.close_button = tk.Button(self.root, text="Exit", command=self.on_close)
        self.close_button.pack(pady=10)

        # Handle application close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_mode(self, selected_mode):
        self.ges.set_mode(selected_mode)
        self.mode_dropdown.set(selected_mode)
        self.mode_label.config(text=f"Current Mode: {selected_mode}")

    def on_close(self):
        self.ges.stop_camera()
        self.root.destroy()
        
root = tk.Tk()
app = HandGestureGUI(root)
root.mainloop()
