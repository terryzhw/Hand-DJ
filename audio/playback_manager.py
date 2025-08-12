
import os
import pygame
import threading
import time
import tempfile
from pydub import AudioSegment
from typing import Optional, Callable


TEMP_FILE_PREFIX = 'hand_dj_temp_'
TEMP_FILE_SUFFIX = '.wav'
PROGRESS_UPDATE_INTERVAL_S = 0.1
MAX_TEMP_FILES = 2

class PlaybackManager:
    def __init__(self, sample_rate: int, buffer_size: int, 
                 progress_callback: Optional[Callable[[float, float], None]] = None,
                 status_callback: Optional[Callable[[str], None]] = None):
        # Initialize pygame mixer with specified audio settings
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=buffer_size)
        pygame.mixer.init()
        

        self.is_playing = False
        self.current_position_ms = 0.0
        self.audio_length_ms = 0.0
  
        self.temp_files = []

        self.playback_thread: Optional[threading.Thread] = None
        self.stop_thread = False
  
        self.progress_callback = progress_callback
        self.status_callback = status_callback

    def play(self, audio: AudioSegment, start_position_s: float = 0.0) -> bool:
        # Start playing audio from a specific position with progress tracking
        if not isinstance(audio, AudioSegment):
            self.notify_status("Error: Invalid audio data")
            return False


        temp_file = self.save_to_temp(audio)
        if not temp_file:
            return False

        try:
  
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play(start=start_position_s)

            self.is_playing = True
            self.audio_length_ms = len(audio)
            self.current_position_ms = start_position_s * 1000

            self.start_progress_tracking()
            self.notify_status("Playing")
            return True
        except pygame.error as e:
            self.notify_status(f"Playback error: {e}")
            return False

    def set_volume(self, volume: float):

        if self.is_playing:
            pygame.mixer.music.set_volume(volume)

    def pause(self):

        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.stop_thread = True
            self.notify_status("Paused")

    def resume(self):

        if not self.is_playing and self.audio_length_ms > 0:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.start_progress_tracking()
            self.notify_status("Resumed")

    def stop(self):

        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_position_ms = 0.0
        self.stop_thread = True
        self.notify_status("Stopped")

    def get_current_position_s(self) -> float:

        return self.current_position_ms / 1000.0

    def save_to_temp(self, audio: AudioSegment) -> Optional[str]:
        # Save audio to temporary file for pygame playback
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix=TEMP_FILE_SUFFIX, prefix=TEMP_FILE_PREFIX)
            os.close(temp_fd)

            audio.export(temp_path, format='wav')

            self.temp_files.append(temp_path)
            self.cleanup_old_temp_files()
            return temp_path
        except Exception as e:
            self.notify_status(f"Temp file error: {e}")
            return None

    def cleanup_old_temp_files(self):

        while len(self.temp_files) > MAX_TEMP_FILES:
            old_file = self.temp_files.pop(0)
            try:
                if os.path.exists(old_file):
                    os.unlink(old_file)
            except OSError:
                pass  

    def start_progress_tracking(self):
  
        self.stop_thread = False
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=self.track_progress, daemon=True)
            self.playback_thread.start()

    def track_progress(self):
        # Background thread that monitors playback progress and updates callbacks
        while self.is_playing and not self.stop_thread:

            if not pygame.mixer.music.get_busy():
                self.stop()
                self.notify_status("Finished")
                break
            

            self.current_position_ms += (PROGRESS_UPDATE_INTERVAL_S * 1000)

            if self.progress_callback:
                current_s = self.get_current_position_s()
                total_s = self.audio_length_ms / 1000.0
                self.progress_callback(current_s, total_s)

            time.sleep(PROGRESS_UPDATE_INTERVAL_S)

    def notify_status(self, message: str):

        if self.status_callback:
            self.status_callback(message)

    def cleanup(self):

        self.stop()

        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError:
                pass  
        self.temp_files.clear()

        pygame.mixer.quit()
