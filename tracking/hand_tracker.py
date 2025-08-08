# Hand tracking module using MediaPipe for detecting and tracking hand landmarks
# Provides real-time hand detection and landmark extraction for gesture recognition

import cv2
import mediapipe as mp
from typing import List, Optional

class HandDetector:
    def __init__(self, static_image_mode=False, max_hands=2, model_complexity=1, detection_confidence=0.7, track_confidence=0.5):

        self.static_image_mode = static_image_mode     
        self.max_hands = max_hands                      
        self.model_complexity = model_complexity       
        self.detection_confidence = detection_confidence 
        self.track_confidence = track_confidence       


        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.track_confidence
        )

        self.mp_draw = mp.solutions.drawing_utils

        self.results = None
        

        self.cached_rgb_image = None
        self.cached_bgr_image = None

    def find_hands(self, image, draw=True):

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False 
        

        self.results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True   


        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        image, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                        connection_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )
        return image

    def find_position(self, image, hand_no=0, draw=True):

        landmark_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                for id, landmark in enumerate(my_hand.landmark):
       
                    h, w, c = image.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmark_list.append([id, cx, cy])

                    if draw:
                        cv2.circle(image, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return landmark_list

    def get_hand_type(self, hand_index, handedness_list):

        if handedness_list and hand_index < len(handedness_list):
            return handedness_list[hand_index].classification[0].label
        return None

class HandTracker:

    
    def __init__(self, detection_confidence=0.8, max_hands=2):

        self.hand_detector = HandDetector(detection_confidence=detection_confidence, max_hands=max_hands)
        

        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks: Optional[List[List[int]]] = None
        self.right_hand_landmarks: Optional[List[List[int]]] = None

    def process_hands(self, image: cv2.typing.MatLike):

        image = self.hand_detector.find_hands(image)
        self.reset_hand_states()

    
        if self.hand_detector.results and self.hand_detector.results.multi_hand_landmarks:
            num_hands = len(self.hand_detector.results.multi_hand_landmarks)
            handedness_list = self.hand_detector.results.multi_handedness

            for hand_index in range(num_hands):

                landmarks = self.hand_detector.find_position(image, hand_no=hand_index, draw=False)

                hand_type = self.hand_detector.get_hand_type(hand_index, handedness_list)


                if hand_type == "Right":
                    self.right_hand_landmarks = landmarks
                    self.right_hand_present = True
                elif hand_type == "Left":
                    self.left_hand_landmarks = landmarks
                    self.left_hand_present = True
        return image

    def reset_hand_states(self):

        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None

    def cleanup(self):

        cv2.destroyAllWindows()
