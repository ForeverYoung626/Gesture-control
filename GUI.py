import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import threading
from recognition import Gesture

class ModernGestureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Recognition")
        self.root.resizable(False, False)
        
        self.root.overrideredirect(True)
        self.transparent_color = '#000001'
        self.root.attributes('-transparentcolor', self.transparent_color)
        self.root.configure(bg=self.transparent_color)
        self.root.attributes('-topmost', True)

        screen_width = root.winfo_screenwidth()
        self.window_width = 820
        self.window_height = 800
        x_pos = (screen_width - self.window_width) // 2
        y_pos = (root.winfo_screenheight() - self.window_height) // 2
        root.geometry(f'{self.window_width}x{self.window_height}+{x_pos}+{y_pos}')
        
        self.shadow = tk.Canvas(self.root, width=self.window_width + 20, height=self.window_height + 20)
        self.shadow.place(x=-10, y=-10)
        self.create_blur_background()
        self.create_rounded_background()
        
        self.ges = Gesture()

        self.idle_alpha = 0.6
        self.hover_alpha = 0.9
        self.shrinked = False
        self.animating = False
        self.expanded = True
        self.shrink_timer = None
        self.fade_job = None
        self.floating_camera_window = None

        self.show_camera_var = tk.BooleanVar(value=True)
        self.show_skeleton_var = tk.BooleanVar(value=False)
        self.show_on_top_var = tk.BooleanVar(value=False)
        self.show_img_var = tk.BooleanVar(value=False)

        self.create_widgets()
        # self.bind_hover_detection()
        
        self.offset_x = 0
        self.offset_y = 0
        root.bind("<ButtonPress-1>", self.start_move)
        root.bind("<B1-Motion>", self.do_move)
        
    def create_blur_background(self):
        base = Image.new('RGBA', (self.window_width, self.window_height), (240, 240, 240, 180))
        blurred = base.filter(ImageFilter.GaussianBlur(radius=8))
        self.blur_image = ImageTk.PhotoImage(blurred)

        self.blur_canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height, bg='white', highlightthickness=0)
        self.blur_canvas.place(x=0, y=0)
        self.blur_canvas.create_image(0, 0, anchor='nw', image=self.blur_image)

    def create_rounded_background(self):
        self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height, bg=self.transparent_color, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        radius = 30
        w, h = self.window_width, self.window_height
        self.canvas.create_arc((0, 0, radius*2, radius*2), start=90, extent=90, fill="#f0f0f0", outline="#f0f0f0")
        self.canvas.create_arc((w-radius*2, 0, w, radius*2), start=0, extent=90, fill="#f0f0f0", outline="#f0f0f0")
        self.canvas.create_arc((0, h-radius*2, radius*2, h), start=180, extent=90, fill="#f0f0f0", outline="#f0f0f0")
        self.canvas.create_arc((w-radius*2, h-radius*2, w, h), start=270, extent=90, fill="#f0f0f0", outline="#f0f0f0")
        self.canvas.create_rectangle((radius, 0, w-radius, h), fill="#f0f0f0", outline="#f0f0f0")
        self.canvas.create_rectangle((0, radius, w, h-radius), fill="#f0f0f0", outline="#f0f0f0")

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        #攝影機畫面區
        self.video_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.video_frame.pack(pady=20)

        self.video_canvas = tk.Canvas(self.video_frame, width=640, height=360, bg="#dee2e6", highlightthickness=0)
        self.video_canvas.pack()
        self.video_label = tk.Label(self.video_canvas, bg="black")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center", width=620, height=340)

        #模式按鈕列
        self.mode_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.mode_frame.pack(pady=20)

        self.modes = ["Selection", "Keyboard", "Mouse", "PPT"]
        self.mode_var = tk.StringVar(value=self.modes[0])
        self.mode_buttons = {}

        for mode in self.modes:
            btn = tk.Button(self.mode_frame, text=mode, width=12, height=2,
                            bg="#dee2e6", fg="#343a40",
                            font=("Segoe UI", 11, "bold"),
                            relief="flat",
                            command=lambda m=mode: self.update_mode(m))
            btn.pack(side="left", padx=10)
            self.add_hover_effect(btn)
            self.mode_buttons[mode] = btn

        #當前模式標籤
        self.mode_label = tk.Label(self.root, text=f"Current Mode: {self.ges.current_mode}",
                                   bg="#f8f9fa", fg="#495057",
                                   font=("Segoe UI", 12))
        self.mode_label.pack(pady=10)

        #控制按鈕列
        self.control_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.control_frame.pack(pady=20)

        self.start_button = tk.Button(self.control_frame, text="Start Camera", width=15,
                                      bg="#51cf66", fg="white", font=("Segoe UI", 11, "bold"),
                                      activebackground="#40c057", relief="flat",
                                      command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=10)
        self.add_hover_effect(self.start_button, darken=True)

        self.stop_button = tk.Button(self.control_frame, text="Stop Camera", width=15,
                                     bg="#fab005", fg="white", font=("Segoe UI", 11, "bold"),
                                     activebackground="#f59f00", relief="flat",
                                     command=self.stop_camera)
        self.stop_button.grid(row=0, column=1, padx=10)
        self.add_hover_effect(self.stop_button, darken=True)

        self.exit_button = tk.Button(self.control_frame, text="Exit", width=15,
                                     bg="#fa5252", fg="white", font=("Segoe UI", 11, "bold"),
                                     activebackground="#f03e3e", relief="flat",
                                     command=self.on_close)
        self.exit_button.grid(row=0, column=2, padx=10)
        self.add_hover_effect(self.exit_button, darken=True)

        #顯示控制開關列
        self.toggle_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.toggle_frame.pack(pady=10)

        self.show_camera_check = tk.Checkbutton(self.toggle_frame, text="Show Camera",
                                                variable=self.show_camera_var,
                                                bg="#f8f9fa", fg="#343a40",
                                                font=("Segoe UI", 10),
                                                activebackground="#f8f9fa", activeforeground="#343a40",
                                                command=self.toggle_show_camera)
        self.show_camera_check.grid(row=0, column=0, padx=20)

        self.show_skeleton_check = tk.Checkbutton(self.toggle_frame, text="Show Skeleton",
                                                  variable=self.show_skeleton_var,
                                                  bg="#f8f9fa", fg="#343a40",
                                                  font=("Segoe UI", 10),
                                                  activebackground="#f8f9fa", activeforeground="#343a40",
                                                  command=self.toggle_show_skeleton)
        self.show_skeleton_check.grid(row=0, column=1, padx=20)

        self.show_on_top_check = tk.Checkbutton(self.toggle_frame, text="Always On Top",
                                                  variable=self.show_on_top_var,
                                                  bg="#f8f9fa", fg="#343a40",
                                                  font=("Segoe UI", 10),
                                                  activebackground="#f8f9fa", activeforeground="#343a40",
                                                  command=self.toggle_show_on_top)
        self.show_on_top_check.grid(row=0, column=2, padx=20)

        self.show_img_check = tk.Checkbutton(self.toggle_frame, text="Show Keyboard",
                                                  variable=self.show_img_var,
                                                  bg="#f8f9fa", fg="#343a40",
                                                  font=("Segoe UI", 10),
                                                  activebackground="#f8f9fa", activeforeground="#343a40",
                                                  command=self.toggle_show_img)
        self.show_img_check.grid(row=0, column=3, padx=20)
        
        self.floating_img = None
        self.create_floating_img()
        
    def start_camera(self):
        self.ges.show_cam(self.show_camera_var.get())
        self.ges.show_skeleton(self.show_skeleton_var.get())
        self.ges.start_camera(self.video_label)
        # self.create_floating_img()
        self.show_floating(self.show_img_var.get())
        
    def stop_camera(self):
        self.ges.stop_camera(self.video_label)
        # self.close_floating_img()

    def update_mode(self, selected_mode):
        self.ges.set_mode(selected_mode)
        self.mode_var.set(selected_mode)
        self.mode_label.config(text=f"Current Mode: {selected_mode}")
        # self.auto_shrink()
        self.start_camera()

    def on_close(self):
        self.ges.stop_camera(self.video_label)
        self.root.destroy()

    def toggle_show_camera(self):
        self.ges.show_cam(self.show_camera_var.get())

    def toggle_show_skeleton(self):
        self.ges.show_skeleton(self.show_skeleton_var.get())

    def toggle_show_on_top(self):
        self.root.attributes('-topmost', self.show_on_top_var.get())

    def toggle_show_img(self):
        self.show_floating(self.show_img_var.get())

    def add_hover_effect(self, widget, darken=False):
        normal_bg = widget['bg']
        original_x = 0

        def on_enter(e):
            nonlocal original_x
            if darken:
                widget.config(bg=self.darken_color(normal_bg, amount=30))
            else:
                widget.config(bg="#ced4da")
            widget.config(cursor="hand2")
            # if shake:
            #     original_x = widget.winfo_x()
            #     self.shake(widget)

        def on_leave(e):
            widget.config(bg=normal_bg)
            # if shake:
            #     widget.place_configure(x=original_x)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def shake(self, widget, count=0):
        if count > 6:
            return
        offset = (-2 if count % 2 == 0 else 2)
        widget.place_configure(x=widget.winfo_x() + offset)
        widget.after(50, lambda: self.shake(widget, count + 1))

    def darken_color(self, color, amount=20):
        color = color.lstrip("#")
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, c - amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def create_floating_img(self):
        self.floating_img = tk.Toplevel(self.root)
        self.floating_img.overrideredirect(True)
        self.floating_img.geometry("300x300+10+10")
        self.floating_img.configure(bg="black")

        img = Image.open("image/keyboard.jpg")
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_label = tk.Label(self.floating_img, image=self.tk_img)
        self.img_label.pack(fill="both", expand=True)

        # 加入拖曳功能
        # self.floating_img.bind("<Button-1>", self.start_move)
        # self.floating_img.bind("<B1-Motion>", self.do_move)
        
        self.show_floating(self.show_img_var)
        
    def show_floating(self, b):
        if b:
            self.floating_img.deiconify()
        else:
            self.floating_img.withdraw()
    
    def close_floating_img(self):
        if self.floating_img:
            self.floating_img.destroy()
            self.floating_img = None

    # def bind_hover_detection(self):
    #     self.root.bind("<Enter>", self.on_mouse_enter)
    #     self.root.bind("<Leave>", self.on_mouse_leave)

    # def on_mouse_enter(self, event):
    #     if self.shrinked and not self.animating and not self.expanded:
    #         if self.shrink_timer:
    #             self.root.after_cancel(self.shrink_timer)
    #             self.shrink_timer = None
    #         if self.fade_job:
    #             self.root.after_cancel(self.fade_job)
    #         self.fade_alpha(target_alpha=self.hover_alpha, step=0.02)
    #         self.animate_slide(opening=True)

    # def on_mouse_leave(self, event):
    #     if self.shrinked and not self.animating:
    #         if not self.expanded:
    #             return
    #         mouse_x = self.root.winfo_pointerx()
    #         mouse_y = self.root.winfo_pointery()
    #         win_x = self.root.winfo_rootx()
    #         win_y = self.root.winfo_rooty()
    #         win_width = self.root.winfo_width()
    #         win_height = self.root.winfo_height()

    #         if (win_x - 30 <= mouse_x <= win_x + win_width) and (win_y <= mouse_y <= win_y + win_height):
    #             return

    #         if self.fade_job:
    #             self.root.after_cancel(self.fade_job)
    #         self.fade_alpha(target_alpha=self.idle_alpha, step=-0.02)

    #         if not self.shrink_timer:
    #             self.shrink_timer = self.root.after(3000, self.delayed_shrink)

    # def delayed_shrink(self):
    #     if self.shrinked and not self.animating:
    #         self.animate_slide(opening=False)
    #     self.shrink_timer = None

    # def fade_alpha(self, target_alpha, step=0.02):
    #     current_alpha = self.root.attributes('-alpha')
    #     current_alpha = float(current_alpha)

    #     def fading():
    #         nonlocal current_alpha
    #         if (step > 0 and current_alpha < target_alpha) or (step < 0 and current_alpha > target_alpha):
    #             current_alpha += step
    #             current_alpha = max(min(current_alpha, 1.0), 0.0)
    #             self.root.attributes('-alpha', current_alpha)
    #             self.fade_job = self.root.after(30, fading)
    #         else:
    #             self.root.attributes('-alpha', target_alpha)
    #             self.fade_job = None

    #     fading()

    # def animate_slide(self, opening):
    #     self.animating = True
    #     screen_width = self.root.winfo_screenwidth()

    #     full_width = 180
    #     collapsed_width = 20
    #     target_width = full_width if opening else collapsed_width
    #     steps = 20
    #     current_step = 0

    #     if opening:
    #         self.close_floating_camera()
    #     else:
    #         self.show_floating_camera()
            
    #     def slide():
    #         nonlocal current_step
    #         progress = current_step / steps
    #         if opening:
    #             width = int(collapsed_width + (full_width - collapsed_width) * progress)
    #         else:
    #             width = int(full_width - (full_width - collapsed_width) * progress)

    #         height = 40 * len(self.modes) + 220
    #         new_x = screen_width - width - 10

    #         self.root.geometry(f"{width}x{height}+{new_x}+{self.root.winfo_y()}")

    #         if current_step < steps:
    #             current_step += 1
    #             self.root.after(10, slide)
    #         else:
    #             final_width = full_width if opening else collapsed_width
    #             final_x = screen_width - final_width - 10
    #             self.root.geometry(f"{final_width}x{height}+{final_x}+{self.root.winfo_y()}")
    #             self.expanded = opening
    #             self.animating = False
        
    #     slide()

    # def auto_shrink(self):
    #     if not self.shrinked:
    #         self.animate_slide(opening=False)
    #         self.shrinked = True


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGestureApp(root)
    root.mainloop()