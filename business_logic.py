import cv2
import tkinter as tk

cap = None
show_message_on_video = False  # Flag to control message display

def start_video(gui):
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        gui.capture_button.config(state=tk.NORMAL)
        gui.back_button.config(state=tk.NORMAL)
        show_frame(gui)

def capture_frame(gui):
    # Implement the capture functionality
    pass

def go_back(gui):
    global cap
    if cap is not None:
        cap.release()
        cap = None

    # Reset the GUI elements
    reset_gui(gui)

def show_frame(gui):
    global cap, show_message_on_video
    if cap:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            # If the flag is set, draw the message on the frame
            if show_message_on_video:
                text = "Getting Video Ready"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_color = (0, 0, 255)  # Red color
                thickness = 2
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

                # Get the text position so it's centered
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2

                cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, thickness)

            gui.update_frame(frame)
        gui.root.after(10, lambda: show_frame(gui))

def reset_gui(gui):
    # Reset the GUI to its initial state
    gui.start_button.config(state=tk.NORMAL)
    gui.capture_button.config(state=tk.DISABLED)
    gui.back_button.config(state=tk.DISABLED)
    gui.video_label.imgtk = None
    gui.video_label.configure(image='')  # Remove the current image

def release_resources():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
