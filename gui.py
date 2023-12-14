import tkinter as tk
from PIL import Image, ImageTk
import cv2  # Make sure to import cv2

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('640x580')
        self.video_label = tk.Label(self.root, bg='grey')
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Initialize the methods as None
        self.start_video = None
        self.capture_frame = None
        self.go_back = None

        self.setup_buttons()
        #text overlay
        self.message_label = tk.Label(self.video_label, text="", bg='grey', fg='white', font=("Helvetica", 16))
        self.message_label.place(relx=0.5, rely=0.5, anchor='center')

    def setup_buttons(self):
        button_container = tk.Frame(self.root)
        button_container.pack()

        self.start_button = tk.Button(button_container, text="Start Video", command=lambda: self.start_video())
        self.start_button.pack(side=tk.LEFT)

        self.capture_button = tk.Button(button_container, text="Capture Frame", state=tk.DISABLED, command=lambda: self.capture_frame())
        self.capture_button.pack(side=tk.LEFT)

        self.back_button = tk.Button(button_container, text="Go Back", state=tk.DISABLED, command=lambda: self.go_back())
        self.back_button.pack(side=tk.LEFT)

    def set_video_start_callback(self, callback):
        self.start_video = callback

    def show_message(self, message):
        self.message_label.config(text=message)
        self.message_label.place(relx=0.5, rely=0.5, anchor='center')

    def hide_message(self):
        self.message_label.place_forget()
    def set_capture_frame_callback(self, callback):
        self.capture_frame = callback

    def set_go_back_callback(self, callback):
        self.go_back = callback

    def update_frame(self, frame):
        # Convert the frame to a format suitable for Tkinter and display it
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def reset_gui(self):
        self.start_button.config(state=tk.NORMAL)
        self.capture_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)
        self.video_label.imgtk = None
        self.video_label.configure(image='')  # Remove the current image

    def run(self):
        self.root.mainloop()
