import cv2
from process import process_image
import time
import mediapipe as mp
import os,face_recognition
mp_face_detection = mp.solutions.face_detection.FaceDetection()
 # Encode the known faces
known_face_encodings = []
known_face_names = []
for i in os.listdir("Known-Faces"):
    known_face_names.append(i.split(".")[0])
    known_image = face_recognition.load_image_file(os.path.join("Known-Faces" , i))
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    known_face_encodings.append(known_face_encoding)
class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.start_time = time.time()
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        

        ret, frame = self.video.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_face_detection.process(frame_rgb)

        if results.detections:
            for detection in results.detections:
                x, y, w, h = int(detection.location_data.relative_bounding_box.xmin * frame.shape[1]), \
                             int(detection.location_data.relative_bounding_box.ymin * frame.shape[0]), \
                             int(detection.location_data.relative_bounding_box.width * frame.shape[1]), \
                             int(detection.location_data.relative_bounding_box.height * frame.shape[0])

                x1, y1 = x + w, y + h
                try:
                    frame = process_image((x, y, w, h), frame,known_face_encodings,known_face_names)
                except Exception as e:
                    print(e)
                # cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 1)
                cv2.line(frame, (x, y), (x + 30, y), (0, 0, 255), 6)  # Top Left
                cv2.line(frame, (x, y), (x, y + 30), (0, 0, 255), 6)

                cv2.line(frame, (x1, y), (x1 - 30, y), (0, 0, 255), 6)  # Top Right
                cv2.line(frame, (x1, y), (x1, y + 30), (0, 0, 255), 6)

                cv2.line(frame, (x, y1), (x + 30, y1), (0, 0, 255), 6)  # Bottom Left
                cv2.line(frame, (x, y1), (x, y1 - 30), (0, 0, 255), 6)

                cv2.line(frame, (x1, y1), (x1 - 30, y1), (0, 0, 255), 6)  # Bottom right
                cv2.line(frame, (x1, y1), (x1, y1 - 30), (0, 0, 255), 6)
        
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()
