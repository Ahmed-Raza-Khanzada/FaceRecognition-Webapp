import face_recognition
import os
import cv2
def recognize_faces(faces,image,known_face_encodings,known_face_names):

   

    # Convert the image from BGR to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    
    # Identify faces in the image
    

    x,y,w,h = faces

    # Crop the face from the image
    face_image = rgb_image[y:y+h, x:x+w]

    # Resize the face image for better recognition performance (optional)
    face_image = cv2.resize(face_image, (300, 300), fx=0.5, fy=0.5)

    # Perform face recognition
    face_encodings = face_recognition.face_encodings(face_image)
    if len(face_encodings) > 0:
    
        matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0])
        name = "Unknown"

        # Check if there is a match
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Return the face names
        return name
   
    return False
# Process an image file
def process_image(face,image,known_face_encodings,known_face_names):
    # Load the image
    

    # Recognize faces in the image
    face_names = recognize_faces(face,image,known_face_encodings,known_face_names)

    # Draw bounding boxes and names on the image
    if face_names:
        cv2.putText(image, face_names, (max(2,face[0]), max(9,face[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return image,face_names