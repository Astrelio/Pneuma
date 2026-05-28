import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        # Para Python 3.12 y MediaPipe > 0.10, usamos la nueva Tasks API.
        base_options = python.BaseOptions(model_asset_path='detector/hand_landmarker.task')
        
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=vision.RunningMode.VIDEO)
            
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.start_time_ms = int(time.time() * 1000)

    def process_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Calcular el timestamp en milisegundos desde que inició el tracker
        current_time_ms = int(time.time() * 1000) - self.start_time_ms
        
        results = self.detector.detect_for_video(mp_image, current_time_ms)
        return results

    def get_landmarks(self, frame, results):
        landmarks_list = []
        if results and results.hand_landmarks:
            for hand_lms in results.hand_landmarks:
                lm_list = []
                h, w, c = frame.shape
                for id, lm in enumerate(hand_lms):
                    # Multiplicamos la coordenada Z por 'w' para que tenga una escala proporcional a los píxeles X e Y
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    lm_list.append([id, cx, cy, cz])
                landmarks_list.append(lm_list)
        return landmarks_list
