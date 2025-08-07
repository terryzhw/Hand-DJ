import time
import threading
from typing import List
from audio.audio_processor import AudioProcessor
from modules.constants import *


class AudioController:
    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE):
        self.audio_processor = AudioProcessor(sample_rate=sample_rate)
        self.pitch = DEFAULT_PITCH
        self.volume = DEFAULT_VOLUME
        self.reverb = DEFAULT_REVERB
        self.pitch_buffer: List[float] = []
        self.volume_buffer: List[float] = []
        self.reverb_buffer: List[float] = []
        self.parameter_update_lock = threading.Lock()
        self.last_update_time = time.time()
        self.audio_loaded = False

    def load_audio(self, audio_file: str) -> bool:
        try:
            if self.audio_processor.load_file(audio_file) and self.audio_processor.play():
                self.audio_loaded = True
                return True
            return False
        except Exception:
            return False

    def set_pitch(self, pitch: float):
        self.pitch = self.smooth_value(pitch, self.pitch_buffer, self.pitch)
        self.update_parameters()

    def set_reverb(self, reverb: float):
        self.reverb = self.smooth_value(reverb, self.reverb_buffer, self.reverb)
        self.update_parameters()

    def set_volume(self, volume: float):
        self.volume = self.smooth_value(volume, self.volume_buffer, self.volume, VOLUME_SMOOTHING_FACTOR)
        if self.audio_loaded:
            self.audio_processor.set_param('volume', self.volume)

    def update_parameters(self):
        current_time = time.time()
        if current_time - self.last_update_time > PARAMETER_UPDATE_INTERVAL:
            with self.parameter_update_lock:
                if self.audio_loaded:
                    self.audio_processor.set_param('pitch', self.pitch)
                    self.audio_processor.set_param('reverb', self.reverb)
            self.last_update_time = current_time

    def smooth_value(self, new_value: float, buffer: List[float], current_value: float, smoothing_factor: float = SMOOTHING_FACTOR) -> float:
        buffer.append(new_value)
        if len(buffer) > BUFFER_SIZE:
            buffer.pop(0)
        avg_value = sum(buffer) / len(buffer)
        return current_value + smoothing_factor * (avg_value - current_value)

    def get_stats(self):
        return {"pitch": self.pitch, "reverb": self.reverb, "volume": self.volume}

    def reset_parameters(self):
        self.pitch = DEFAULT_PITCH
        self.volume = DEFAULT_VOLUME
        self.reverb = DEFAULT_REVERB
        self.pitch_buffer.clear()
        self.volume_buffer.clear()
        self.reverb_buffer.clear()
        if self.audio_loaded:
            self.audio_processor.set_params({
                'pitch': DEFAULT_PITCH, 'reverb': DEFAULT_REVERB, 
                'treble': DEFAULT_TREBLE, 'volume': DEFAULT_VOLUME
            })

    def toggle_playback(self):
        if not self.audio_loaded:
            return
        if self.audio_processor.is_playing:
            self.audio_processor.pause()
        else:
            self.audio_processor.resume()

    def cleanup(self):
        self.audio_processor.cleanup()
