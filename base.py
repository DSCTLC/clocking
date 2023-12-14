import gui
import business_logic

def auto_start_and_back(app):
    # Show message
    app.show_message("Getting Video Ready")
    app.root.update_idletasks()  # Force an update of the GUI

    # Delay the start of the video to ensure the message is displayed
    app.root.after(100, lambda: business_logic.start_video(app))  # 100 ms delay

    # Schedule to hide the message and go back after a delay
    app.root.after(5100, lambda: [app.hide_message(), business_logic.go_back(app)])  # Adjusted delay
    # Set the flag to show the message
    business_logic.show_message_on_video = True
    business_logic.start_video(app)

    # Schedule to hide the message and go back after a delay
    app.root.after(5000, lambda: [hide_message(), business_logic.go_back(app)])

def hide_message():
    business_logic.show_message_on_video = False

if __name__ == "__main__":
    app = gui.Application()
    app.set_video_start_callback(lambda: business_logic.start_video(app))
    app.set_capture_frame_callback(lambda: business_logic.capture_frame(app))
    app.set_go_back_callback(lambda: business_logic.go_back(app))

    # Automatically start video and go back after a delay
    app.root.after(0, lambda: auto_start_and_back(app))

    app.run()
    business_logic.release_resources()
