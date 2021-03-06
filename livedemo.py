import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
import numpy as np
import cv2
import platform
import tensorflow as tf
import argparse
import imutils

# For static images:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


if __name__ == "__main__":
    model_path = r'output\DD2CNN_model.h5'
    model = tf.keras.models.load_model(model_path)

    print("python version:", platform.python_version())
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=False, type=str,
                    help="set path of video for testing video path")

    args = vars(ap.parse_args())
    path = args['path']
    cap = None
    if path is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(path)


    cap.set(3,2000)
    cap.set(4,2000)

    ret, frame = cap.read()
    cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    with mp_face_mesh.FaceMesh() as face_mesh:
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            frame = imutils.resize(frame, width=450)
            image = frame
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            status = None
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACE_CONNECTIONS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec)
                    landmark_arr = []
                    for point in face_landmarks.landmark:
                        landmark_arr.append([point.x, point.y, point.z])
                    # print(landmark_arr)
                    status = model.predict([landmark_arr])
            print(status)
            if status is not None:
                index = np.argmax(status[0])
                percentage = status[0][index]
                frame = image
                label = ['alert','drowsy','semi alert']
                msg = label[index]+' '+'{:.2f}'.format(percentage)
                cv2.putText(frame,msg,(200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)

            # Process the keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("quit")
                break
            # show the images
            cv2.imshow('frame',image)

    cap.release()
    cv2.destroyAllWindows()