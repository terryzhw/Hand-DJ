

import cv2
import time
import os
import pygame
import threading
import numpy as np
from typing import Optional
from tracking.hand_tracker import HandTracker
from audio.audio_controller import AudioController
from tracking.visualizer import Visualizer
from modules.constants import *

class DJController:
    def __init__(self, audio_file: str = "audio.wav"):

        self.camera_width, self.camera_height = DEFAULT_CAMERA_WIDTH, DEFAULT_CAMERA_HEIGHT
        

        self.visualizer = Visualizer(camera_width=self.camera_width, camera_height=self.camera_height)

        self.audio_controller = AudioController(sample_rate=DEFAULT_SAMPLE_RATE)
        
        self.hand_tracker: Optional[HandTracker] = None
        self.camera: Optional[cv2.VideoCapture] = None
        self.initialization_complete = False
        self.initialization_thread: Optional[threading.Thread] = None

        self.previous_time = 0
        self.frame_skip_count = 0
        self.process_every_n_frames = 1
        
  
        self.previous_landmarks = {
            'left': None,
            'right': None
        }
        

        if audio_file and os.path.exists(audio_file):
            self.pending_audio_file = audio_file
        else:
            self.pending_audio_file = None
        

        self.start_async_initialization()

    def start_async_initialization(self):

        self.initialization_thread = threading.Thread(
            target=self.initialize_heavy_components,
            daemon=True
        )
        self.initialization_thread.start()

    def initialize_heavy_components(self):

        try:

            self.hand_tracker = HandTracker(
                detection_confidence=DEFAULT_DETECTION_CONFIDENCE, 
                max_hands=DEFAULT_MAX_HANDS
            )
            

            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
 
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
            

            if self.pending_audio_file:
                self.audio_controller.load_audio(self.pending_audio_file)
                

            self.initialization_complete = True
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.initialization_complete = False

    def is_ready(self) -> bool:
   
        return self.initialization_complete and self.camera is not None and self.hand_tracker is not None

    def run(self):

        while True:
            if not self.is_ready():
   
                loading_frame = self.create_loading_frame()
                cv2.imshow("HandDJ", loading_frame)
                time.sleep(0.1)
                continue


            success, frame = self.camera.read()
            if not success:
                time.sleep(0.1)
                continue

  
            frame = cv2.flip(frame, 1)
            
            frame = self.hand_tracker.process_hands(frame)
         
            self.update_controls_with_smoothing(frame)
            

            self.render_visuals(frame)

   
            cv2.imshow("HandDJ", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def create_loading_frame(self):

        frame = np.zeros((self.camera_height, self.camera_width, 3), dtype=np.uint8)
        loading_text = "Loading HandDJ..."
        progress_text = "Initializing camera and hand tracking..."
        audio_text = "Music will start once fully loaded..."
        

        text_size = cv2.getTextSize(loading_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (self.camera_width - text_size[0]) // 2
        text_y = (self.camera_height - text_size[1]) // 2
        

        cv2.putText(frame, loading_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, progress_text, (50, text_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        cv2.putText(frame, audio_text, (50, text_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 100), 1)
        
        return frame

    def smooth_landmarks(self, current_landmarks, previous_landmarks, smoothing_factor=0.3):

        if previous_landmarks is None:
            return current_landmarks
        
        smoothed_landmarks = []
        for i, (current_landmark, prev_landmark) in enumerate(zip(current_landmarks, previous_landmarks)):

            smooth_x = int(prev_landmark[1] * (1 - smoothing_factor) + current_landmark[1] * smoothing_factor)
            smooth_y = int(prev_landmark[2] * (1 - smoothing_factor) + current_landmark[2] * smoothing_factor)
            smoothed_landmarks.append([current_landmark[0], smooth_x, smooth_y])
        
        return smoothed_landmarks

    def update_controls_with_smoothing(self, frame):


        if self.hand_tracker.left_hand_present and self.hand_tracker.left_hand_landmarks:
   
            smoothed_left = self.smooth_landmarks(
                self.hand_tracker.left_hand_landmarks,
                self.previous_landmarks['left']
            )
            self.previous_landmarks['left'] = smoothed_left
            
          
            pitch = self.visualizer.draw_pitch_control(frame, smoothed_left)
            self.audio_controller.smooth_pitch(pitch)
        else:
   
            self.previous_landmarks['left'] = None
            

        if self.hand_tracker.right_hand_present and self.hand_tracker.right_hand_landmarks:
  
            smoothed_right = self.smooth_landmarks(
                self.hand_tracker.right_hand_landmarks,
                self.previous_landmarks['right']
            )
            self.previous_landmarks['right'] = smoothed_right
            

            reverb = self.visualizer.draw_reverb_control(frame, smoothed_right)
            self.audio_controller.smooth_reverb(reverb)
        else:
  
            self.previous_landmarks['right'] = None
            

        if (self.hand_tracker.left_hand_present and self.hand_tracker.right_hand_present and
            self.previous_landmarks['left'] and self.previous_landmarks['right']):
    
            volume = self.visualizer.draw_volume_control(
                frame, 
                self.previous_landmarks['left'], 
                self.previous_landmarks['right']
            )
            self.audio_controller.smooth_volume(volume)
            volume = self.visualizer.draw_volume_control(
                frame, 
                self.previous_landmarks['left'], 
                self.previous_landmarks['right']
            )
            self.audio_controller.smooth_volume(volume)

    def update_controls(self, frame):

        if self.hand_tracker.left_hand_present and self.hand_tracker.left_hand_landmarks:
            pitch = self.visualizer.draw_pitch_control(frame, self.hand_tracker.left_hand_landmarks)
            self.audio_controller.smooth_pitch(pitch)
        if self.hand_tracker.right_hand_present and self.hand_tracker.right_hand_landmarks:
            reverb = self.visualizer.draw_reverb_control(frame, self.hand_tracker.right_hand_landmarks)
            self.audio_controller.smooth_reverb(reverb)
        if self.hand_tracker.left_hand_present and self.hand_tracker.right_hand_present:
            volume = self.visualizer.draw_volume_control(frame, self.hand_tracker.left_hand_landmarks, self.hand_tracker.right_hand_landmarks)
            self.audio_controller.smooth_volume(volume)

    def render_visuals(self, frame):

        current_time = time.time()
        self.visualizer.draw_fps(frame, self.previous_time, current_time)
        self.previous_time = current_time

    def get_stats(self):
   
        return self.audio_controller.get_stats()

    def cleanup(self):
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
        self.audio_controller.cleanup()
        if self.hand_tracker is not None:
            self.hand_tracker.cleanup()
        pygame.quit()
