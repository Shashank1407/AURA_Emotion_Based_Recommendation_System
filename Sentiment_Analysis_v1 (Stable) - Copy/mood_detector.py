import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from collections import deque
import datetime
import csv
import os
import time

# --- Create a directory to save snapshots ---
SNAPSHOT_DIR = 'snapshots'
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

# --- Configuration for the snapshot feature ---
SNAPSHOT_TRIGGER_EMOTION = 'Happy' 
SNAPSHOT_CONFIDENCE_THRESHOLD = 0.90
SNAPSHOT_COOLDOWN_SECONDS = 5
last_snapshot_time = 0

# --- Load Models and Setup ---
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # --- This loads your final ROBUST model ---
    emotion_model = load_model('emotion_model_robust.h5', compile=False) # compile=False is needed for custom loss
except Exception as e:
    print(f"Error loading model files: {e}")
    print("Please ensure 'haarcascade_frontalface_default.xml' and 'emotion_model_robust.h5' are in the directory.")
    exit()

EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
PREDICTION_HISTORY = deque(maxlen=15)
LOG_FILE_NAME = 'emotion_log.csv'

with open(LOG_FILE_NAME, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Emotion'])
last_logged_emotion = None

# --- Initialize Webcam ---
print("Starting webcam...")
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open webcam.")
    exit()

# --- Main Application Loop ---
while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame from camera.")
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    (frame_height, frame_width) = frame.shape[:2]
    dashboard = np.zeros((frame_height, 300, 3), dtype="uint8")

    if len(faces) > 0:
        faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (x, y, w, h) = faces

        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            
            prediction = emotion_model.predict(roi, verbose=0)[0]
            top_emotion_index = np.argmax(prediction)
            top_emotion_name = EMOTIONS[top_emotion_index]
            top_emotion_confidence = prediction[top_emotion_index]

            PREDICTION_HISTORY.append(top_emotion_name)
            smoothed_emotion = max(set(PREDICTION_HISTORY), key=PREDICTION_HISTORY.count)
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, smoothed_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            current_time = time.time()
            if (smoothed_emotion == SNAPSHOT_TRIGGER_EMOTION and
                top_emotion_confidence > SNAPSHOT_CONFIDENCE_THRESHOLD and
                (current_time - last_snapshot_time) > SNAPSHOT_COOLDOWN_SECONDS):
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SNAPSHOT_DIR, f"{timestamp}_{smoothed_emotion}.jpg")
                cv2.imwrite(filename, frame)
                print(f"📸 Snapshot saved: {filename}")
                last_snapshot_time = current_time

            if smoothed_emotion != last_logged_emotion:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE_NAME, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, smoothed_emotion])
                last_logged_emotion = smoothed_emotion

            for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, prediction)):
                text = f"{emotion}: {prob * 100:.2f}%"
                bar_width = int(prob * 250)
                bar_y_position = (i * 40) + 45
                cv2.rectangle(dashboard, (20, bar_y_position - 10), (270, bar_y_position + 10), (50, 50, 50), -1)
                cv2.rectangle(dashboard, (20, bar_y_position - 10), (20 + bar_width, bar_y_position + 10), (0, 255, 0), -1)
                cv2.putText(dashboard, text, (25, bar_y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    else:
        PREDICTION_HISTORY.clear()
        last_logged_emotion = None

    final_output = np.hstack((frame, dashboard))
    cv2.imshow('Enhanced Mood Detector', final_output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Closing application...")
camera.release()
cv2.destroyAllWindows()