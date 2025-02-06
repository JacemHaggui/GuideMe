from picamera2 import Picamera2

# Initialize the camera
def setup_camera():
    piCam = Picamera2()
    dispW = 720
    dispH = 360
    piCam.preview_configuration.main.size = (dispW, dispH)
    piCam.preview_configuration.main.format = "RGB888"
    piCam.preview_configuration.align()
    piCam.set_controls({"AfMode": 2})
    piCam.preview_configuration.controls.FrameRate = 30
    piCam.configure("preview")
    piCam.start()
    return piCam, dispW, dispH