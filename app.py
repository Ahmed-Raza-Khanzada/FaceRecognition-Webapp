from flask import Flask, render_template, Response, request
from camera import Video
import cv2
app = Flask(__name__)

camera_enabled = False  # Variable to track camera state

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    log_message = request.data.decode('utf-8')
    print(f"Log message from client: {log_message}")

    global camera_enabled
    if log_message == "Camera enabled":
        camera_enabled = True
        print("Camera enabled")
    elif log_message == "Camera disabled":
        camera_enabled = False
        print("Camera disabled")

    return "Log received"

def gen(camera):
    while True:

        if camera_enabled:
            frame = camera.get_frame()
        else:
            frame = cv2.imread(r"static\download.jpg")
            ret, jpg = cv2.imencode('.jpg', frame)
            frame =  jpg.tobytes()
         
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame +
                b'\r\n\r\n')
       

@app.route('/video')
def video():
    return Response(gen(Video()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/graphs')
def second_page():
    return render_template('graphs.html')

if __name__ == '__main__':
    app.run(debug=True)
