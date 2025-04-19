import tkinter as tk
from recognition import Gesture

class PresentationSupportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Presentation Support")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 400
        window_height = 300
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        root.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')
        
        self.ges = Gesture()
        
        self.modes = ["Selection", "Keyboard", "Mouse", "PPT"]
        self.active_mode = None

        # Frame for buttons (to organize layout better)
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Create mode buttons
        self.buttons = {}
        for mode in self.modes:
            btn = tk.Button(self.button_frame, text=mode, width=20, command=lambda m=mode: self.switch_mode(m))
            btn.pack(pady=5)
            self.buttons[mode] = btn

        # Home & Quit buttons (always visible)
        self.home_btn = tk.Button(root, text="Home", command=self.reset_window, bg="blue", fg="white")
        self.home_btn.pack(pady=5)
        self.quit_btn = tk.Button(root, text="Quit", command=self.on_close, bg="red", fg="white")
        self.quit_btn.pack(pady=5)

    def switch_mode(self, mode):
        if self.active_mode == mode:
            self.reset_window()  # Reset if clicking the active mode again
            return
        
        self.active_mode = mode
        self.ges.set_mode(mode)
        self.update_ui()

        # Resize and move to the right side
        screen_width = self.root.winfo_screenwidth()
        new_width, new_height = 150, 40 * len(self.modes) + 120  # Increased height so Home button fits
        x_pos = screen_width - new_width - 10
        y_pos = 100
        self.root.geometry(f"{new_width}x{new_height}+{x_pos}+{y_pos}")

        # Hide title bar
        self.root.overrideredirect(True)
        

    def reset_window(self):
        self.active_mode = None
        self.update_ui()

        # Reset to default size and position
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 400
        window_height = 300
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        root.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')
        self.root.overrideredirect(False)  # Show title bar again

    def update_ui(self):
        for mode, btn in self.buttons.items():
            if mode == self.active_mode:
                btn.config(bg="green", fg="white")  # Active mode highlighted
            else:
                btn.config(bg="gray", fg="black")  # Inactive mode darkened

    def on_close(self):
        self.root.destroy()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PresentationSupportApp(root)
    root.mainloop()