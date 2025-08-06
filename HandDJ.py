import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import os
import pygame
from AudioManipulationModule import AudioManipulator
import threading

class HandDJ:

    def __init__(self, audio_file="owa.mp3"):
        self.wCam, self.hCam = 640, 480

        try:
            self.detector = htm.handDetector(detectionCon=0.7, maxHands=2)
        except Exception as e:
            print(f"Failed to initialize HandDetector: {e}")
            raise RuntimeError(f"HandDetector initialization failed: {e}")

        # camera initialization
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Check connection and permissions.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.wCam)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.hCam)
        self.pTime = 0
        
        # audio initialization
        try:
            self.audio_manipulator = AudioManipulator(sample_rate=44100)
            print("AudioManipulator initialized successfully")
        except Exception as e:
            print(f"Failed to initialize AudioManipulator: {e}")
            self.cleanup()
            raise RuntimeError(f"AudioManipulator initialization failed: {e}")
            
        # audio parameters
        self.pitch = 1.0
        self.volume = 0.5
        self.bass = 0.0
        
        # smoothing buffer
        self.pitch_buffer = []
        self.volume_buffer = []
        self.bass_buffer = []

        # parameter update lock
        self.parameter_update_lock = threading.Lock()
        self.last_update_time = time.time()
        
        # hand tracking state
        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None
        
        # file loading
        self.audio_loaded = False
        if audio_file and os.path.exists(audio_file):
            self.load_audio(audio_file)

    def load_audio(self, audio_file):
        try:
            if self.audio_manipulator.load_file(audio_file):
                if self.audio_manipulator.play():
                    self.audio_loaded = True
                    print(f"Audio file '{audio_file}' loaded and playing")
                    return True
            return False
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def process_hands(self, img):
        img = self.detector.findHands(img)
        
        # reset hand values
        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None
        
        # get hand information
        if self.detector.results and self.detector.results.multi_hand_landmarks:
            num_hands = len(self.detector.results.multi_hand_landmarks)
            handedness_list = self.detector.results.multi_handedness
            
            for i in range(num_hands):
                landmarks = self.detector.findPosition(img, handNo=i, draw=False)
                
                # if method does not exist
                hand_type = None
                if hasattr(self.detector, 'get_hand_type'):
                    hand_type = self.detector.get_hand_type(i, handedness_list)
                else:
                    # if get_hand_type does not exist
                    if handedness_list and i < len(handedness_list):
                        hand_type = handedness_list[i].classification[0].label
                
                if hand_type == "Right":
                    self.right_hand_landmarks = landmarks
                    self.right_hand_present = True
                    if landmarks:
                        cv2.putText(img, 'Bass', (landmarks[0][1], landmarks[0][2] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                elif hand_type == "Left":
                    self.left_hand_landmarks = landmarks
                    self.left_hand_present = True
                    if landmarks:
                        cv2.putText(img, 'Pitch', (landmarks[0][1], landmarks[0][2] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        return img

    def smooth_value(self, new_value, buffer, current_value, smoothing_factor=0.2):

        buffer.append(new_value)
        if len(buffer) > 5:
            buffer.pop(0)
            
        # average
        avg_value = sum(buffer) / len(buffer)
        
        # apply smoothing
        return current_value + smoothing_factor * (avg_value - current_value)

    def control_pitch(self, img):
        if not self.left_hand_present or not self.left_hand_landmarks:
            return img
            
        # get thumb and index finger positions
        thumb_x, thumb_y = self.left_hand_landmarks[4][1], self.left_hand_landmarks[4][2]
        index_x, index_y = self.left_hand_landmarks[8][1], self.left_hand_landmarks[8][2]

        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        
        # distance to pitch
        raw_pitch = np.interp(distance, [30, 150], [0.5, 3.0])
        raw_pitch = max(0.5, min(3.0, raw_pitch))
        
        # smooth pitch
        self.pitch = self.smooth_value(raw_pitch, self.pitch_buffer, self.pitch)
        
        # update audio
        current_time = time.time()
        if current_time - self.last_update_time > 0.5:  # update every 500ms
            with self.parameter_update_lock:
                if self.audio_loaded:
                    self.audio_manipulator.set_pitch(self.pitch)
            self.last_update_time = current_time

        # draw line from thumb to index
        cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
        cv2.circle(img, (thumb_x, thumb_y), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)
        
        # display pitch values
        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(img, f"Pitch: {self.pitch:.2f}x", (mid_x - 50, mid_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)



        return img

    def control_bass(self, img):

        if not self.right_hand_present or not self.right_hand_landmarks:
            return img
            
        # get thumb and index finger positions
        thumb_x, thumb_y = self.right_hand_landmarks[4][1], self.right_hand_landmarks[4][2]
        index_x, index_y = self.right_hand_landmarks[8][1], self.right_hand_landmarks[8][2]

        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        
        # distance to bass
        raw_bass = np.interp(distance, [30, 150], [-5.0, 5.0])
        raw_bass = max(-5.0, min(5.0, raw_bass))
        
        # smooth bass
        self.bass = self.smooth_value(raw_bass, self.bass_buffer, self.bass)
        
        # update audio
        current_time = time.time()
        if current_time - self.last_update_time > 0.5:  # update every 500ms
            with self.parameter_update_lock:
                if self.audio_loaded:
                    self.audio_manipulator.set_bass(self.bass)
            self.last_update_time = current_time
            
        # draw line from thumb to index
        cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 3)
        cv2.circle(img, (thumb_x, thumb_y), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (index_x, index_y), 10, (0, 0, 255), cv2.FILLED)
        
        # display bass
        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(img, f"Bass: {self.bass:.1f}dB", (mid_x - 50, mid_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
        return img

    def control_volume(self, img):

        if not (self.left_hand_present and self.right_hand_present):
            return img
            
        # get position of both hands thumb and index
        left_thumb_x, left_thumb_y = self.left_hand_landmarks[4][1], self.left_hand_landmarks[4][2]
        left_index_x, left_index_y = self.left_hand_landmarks[8][1], self.left_hand_landmarks[8][2]
        
        right_thumb_x, right_thumb_y = self.right_hand_landmarks[4][1], self.right_hand_landmarks[4][2]
        right_index_x, right_index_y = self.right_hand_landmarks[8][1], self.right_hand_landmarks[8][2]
        
        # find middle of each hand
        left_mid_x = (left_thumb_x + left_index_x) // 2
        left_mid_y = (left_thumb_y + left_index_y) // 2
        
        right_mid_x = (right_thumb_x + right_index_x) // 2
        right_mid_y = (right_thumb_y + right_index_y) // 2
        
        # distance between middle of two hands
        distance = math.hypot(right_mid_x - left_mid_x, right_mid_y - left_mid_y)
        
        # distance to volume
        raw_volume = np.interp(distance, [50, 300], [0.0, 2.0])
        raw_volume = max(0.0, min(2.0, raw_volume))
        
        # smooth values
        self.volume = self.smooth_value(raw_volume, self.volume_buffer, self.volume, 0.1)
        
        # volume updating directly
        if self.audio_loaded:
            self.audio_manipulator.set_volume(self.volume)
            
        # draw lines and circle for visual feedback
        cv2.line(img, (left_thumb_x, left_thumb_y), (left_index_x, left_index_y), (0, 255, 0), 2)
        cv2.line(img, (right_thumb_x, right_thumb_y), (right_index_x, right_index_y), (0, 255, 0), 2)

        cv2.circle(img, (left_mid_x, left_mid_y), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (right_mid_x, right_mid_y), 10, (0, 255, 0), cv2.FILLED)

        cv2.line(img, (left_mid_x, left_mid_y), (right_mid_x, right_mid_y), (0, 255, 0), 3)
        
        # display volume
        display_x = (left_mid_x + right_mid_x) // 2
        display_y = (left_mid_y + right_mid_y) // 2
        cv2.putText(img, f"Volume: {self.volume:.2f}", (display_x - 50, display_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
        return img


    def controlTempo (self, img):
        if not (self.left_hand_present and self.right_hand_present):
            return img



    def display_status(self, img):

        status_lines = [
            f"Audio: {'Playing' if self.audio_loaded else 'No audio'}",
            f"Pitch: {self.pitch:.2f}x (Left hand)",
            f"Bass: {self.bass:.1f}dB (Right hand)",
            f"Volume: {self.volume:.2f} (Both hands)",
            "",
            "Controls: q=quit, r=reset, space=play/pause"
        ]
        
        y = 30
        for line in status_lines:
            cv2.putText(img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20
            
        return img

    def reset_parameters(self):
        self.pitch = 1.0
        self.volume = 0.5
        self.bass = 0.0
        
        self.pitch_buffer.clear()
        self.volume_buffer.clear()
        self.bass_buffer.clear()
        
        if self.audio_loaded:
            self.audio_manipulator.set_parameters(pitch=1.0, bass=0.0, treble=0.0)
            self.audio_manipulator.set_volume(0.5)
            
        print("Reset to Default")

    def toggle_playback(self):
        if not self.audio_loaded:
            print("No audio loaded")
            return
            
        if self.audio_manipulator.is_playing:
            self.audio_manipulator.pause()
            print("Audio paused")
        else:
            self.audio_manipulator.resume()
            print("Audio resumed")

    def run(self):
        print("HandDJ Starting...")
        print("Controls:")
        print("  - Left Hand: Pitch")
        print("  - Right Hand: Bass")
        print("  - Both Hands: Volume")
        print("  - Keys: q=quit, r=reset, space=play/pause")
        
        try:
            while True:
                # read camera
                success, img = self.cap.read()
                if not success:
                    print("Failed to read from camera")
                    time.sleep(0.1)
                    continue
                    
                # flip image for mirror effect
                img = cv2.flip(img, 1)
                
                # process hands and controls
                img = self.process_hands(img)
                img = self.control_pitch(img)
                img = self.control_bass(img)
                img = self.control_volume(img)

                img = self.display_status(img)
                
                # calculate and display fps
                cTime = time.time()
                if self.pTime > 0:
                    fps = 1 / (cTime - self.pTime)
                    cv2.putText(img, f"FPS: {int(fps)}", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                self.pTime = cTime
                
                # show image
                cv2.imshow("HandDJ", img)
                
                # handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.reset_parameters()
                elif key == ord(' '):
                    self.toggle_playback()
                    
        except KeyboardInterrupt:
            print("HandDJ stopped by user")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up...")
        
        try:
            if hasattr(self, 'audio_manipulator'):
                self.audio_manipulator.cleanup()
        except Exception as e:
            print(f"Error cleaning up audio: {e}")
            
        try:
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
        except Exception as e:
            print(f"Error releasing camera: {e}")
            
        cv2.destroyAllWindows()
        
        try:
            pygame.quit()
        except Exception:
            pass
            
        print("Cleanup completed")


if __name__ == "__main__":
    try:
        audio_files = ["insert_mp3_here.mp3", "test_audio.wav", "audio.mp3", "music.mp3"]
        audio_file = None
        
        for file in audio_files:
            if os.path.exists(file):
                audio_file = file
                break

        dj = HandDJ(audio_file=audio_file)
        dj.run()
        
    except Exception as e:
        print(f"Error starting HandDJ: {e}")
