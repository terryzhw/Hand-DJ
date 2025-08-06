import cv2
import math
import numpy as np
from modules.constants import *

class Visualizer:
    def __init__(self, camera_width=DEFAULT_CAMERA_WIDTH, camera_height=DEFAULT_CAMERA_HEIGHT):
        self.camera_width = camera_width
        self.camera_height = camera_height

    def draw_pitch_control(self, image, landmarks):
        thumb_x, thumb_y = landmarks[THUMB_TIP][1], landmarks[THUMB_TIP][2]
        index_x, index_y = landmarks[INDEX_TIP][1], landmarks[INDEX_TIP][2]
        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        raw_pitch = np.interp(distance, [PITCH_DISTANCE_MIN, PITCH_DISTANCE_MAX], [PITCH_RANGE_MIN, PITCH_RANGE_MAX])
        raw_pitch = max(PITCH_RANGE_MIN, min(PITCH_RANGE_MAX, raw_pitch))

        cv2.line(image, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
        cv2.circle(image, (thumb_x, thumb_y), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(image, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)

        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(image, f"Pitch: {raw_pitch:.2f}x", (mid_x - 50, mid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return raw_pitch

    def draw_reverb_control(self, image, landmarks):
        thumb_x, thumb_y = landmarks[THUMB_TIP][1], landmarks[THUMB_TIP][2]
        index_x, index_y = landmarks[INDEX_TIP][1], landmarks[INDEX_TIP][2]
        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        raw_reverb = np.interp(distance, [REVERB_DISTANCE_MIN, REVERB_DISTANCE_MAX], [REVERB_RANGE_MIN, REVERB_RANGE_MAX])
        raw_reverb = max(REVERB_RANGE_MIN, min(REVERB_RANGE_MAX, raw_reverb))

        cv2.line(image, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 3)
        cv2.circle(image, (thumb_x, thumb_y), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(image, (index_x, index_y), 10, (0, 0, 255), cv2.FILLED)

        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(image, f"Reverb: {raw_reverb:.1f}dB", (mid_x - 50, mid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return raw_reverb

    def draw_volume_control(self, image, left_landmarks, right_landmarks):
        left_thumb_x, left_thumb_y = left_landmarks[THUMB_TIP][1], left_landmarks[THUMB_TIP][2]
        left_index_x, left_index_y = left_landmarks[INDEX_TIP][1], left_landmarks[INDEX_TIP][2]
        right_thumb_x, right_thumb_y = right_landmarks[THUMB_TIP][1], right_landmarks[THUMB_TIP][2]
        right_index_x, right_index_y = right_landmarks[INDEX_TIP][1], right_landmarks[INDEX_TIP][2]

        left_mid_x = (left_thumb_x + left_index_x) // 2
        left_mid_y = (left_thumb_y + left_index_y) // 2
        right_mid_x = (right_thumb_x + right_index_x) // 2
        right_mid_y = (right_thumb_y + right_index_y) // 2
        distance = math.hypot(right_mid_x - left_mid_x, right_mid_y - left_mid_y)

        raw_volume = np.interp(distance, [VOLUME_DISTANCE_MIN, VOLUME_DISTANCE_MAX], [VOLUME_RANGE_MIN, VOLUME_RANGE_MAX])
        raw_volume = max(VOLUME_RANGE_MIN, min(VOLUME_RANGE_MAX, raw_volume))

        cv2.line(image, (left_thumb_x, left_thumb_y), (left_index_x, left_index_y), (0, 255, 0), 2)
        cv2.line(image, (right_thumb_x, right_thumb_y), (right_index_x, right_index_y), (0, 255, 0), 2)
        cv2.circle(image, (left_mid_x, left_mid_y), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(image, (right_mid_x, right_mid_y), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(image, (left_mid_x, left_mid_y), (right_mid_x, right_mid_y), (0, 255, 0), 3)

        display_x = (left_mid_x + right_mid_x) // 2
        display_y = (left_mid_y + right_mid_y) // 2
        cv2.putText(image, f"Volume: {raw_volume:.2f}", (display_x - 50, display_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return raw_volume

    def draw_fps(self, image, previous_time, current_time):
        if previous_time > 0:
            fps = 1 / (current_time - previous_time)
            cv2.putText(image, f"FPS: {int(fps)}", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
