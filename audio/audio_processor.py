
import threading
from pydub import AudioSegment
import io
from typing import Optional, Callable, Dict
from audio.audio_effects import AudioEffects
from audio.playback_manager import PlaybackManager
from modules.constants import *

class AudioProcessor:

    # Heart of the audio system that handles file loading, effects, and playback coordination

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, buffer_size: int = DEFAULT_BUFFER_SIZE):
        self.original_audio: Optional[AudioSegment] = None
        self.params: Dict[str, float] = self.default_params()
        self.effects_engine = AudioEffects()
        self.playback_manager = PlaybackManager(sample_rate=sample_rate, buffer_size=buffer_size, status_callback=self.on_playback_status)
        self.parameter_lock = threading.Lock()
        self.effects_thread: Optional[threading.Thread] = None
        self.is_processing_effects = False
        self.status_callback: Optional[Callable[[str], None]] = None

    def default_params(self) -> Dict[str, float]:
 
        return {'volume': DEFAULT_VOLUME, 'pitch': DEFAULT_PITCH, 'reverb': DEFAULT_REVERB}

    def load_file(self, file_path: str) -> bool:

        try:
            self.original_audio = AudioSegment.from_file(file_path)
            self.notify_status('File loaded successfully')
            return True
        except Exception as e:
            self.notify_status(f'Error loading file: {e}')
            return False

    def load_from_bytes(self, audio_data: bytes, format: str = 'wav') -> bool:

        try:
            self.original_audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
            self.notify_status('Audio loaded from bytes')
            return True
        except Exception as e:
            self.notify_status(f'Error loading from bytes: {e}')
            return False

    def set_param(self, name: str, value: float):

        with self.parameter_lock:
            if name in self.params:
                self.params[name] = value
  
            if name == 'volume':
                self.playback_manager.set_volume(self.params['volume'])
        
            elif self.playback_manager.is_playing:
                self.apply_effects_async()
    
    def set_params(self, new_params: Dict[str, float]):

        with self.parameter_lock:
            self.params.update(new_params)
  
        if 'volume' in new_params:
            self.playback_manager.set_volume(self.params['volume'])

        if self.playback_manager.is_playing:
            self.apply_effects_async()

    def play(self, start_position_s: float = 0.0) -> bool:

        if self.original_audio is None:
            self.notify_status('No audio loaded.')
            return False

        processed_audio = self.effects_engine.apply(self.original_audio, self.params)
        return self.playback_manager.play(processed_audio, start_position_s)

    def apply_effects_async(self):

        if self.is_processing_effects or (self.effects_thread and self.effects_thread.is_alive()):
            return
        self.effects_thread = threading.Thread(target=self.effects_thread_target, daemon=True)
        self.effects_thread.start()

    def effects_thread_target(self):

        self.is_processing_effects = True

        current_pos_s = self.playback_manager.get_current_position_s()
       
        with self.parameter_lock:
            current_params = self.params.copy()
       
        processed_audio = self.effects_engine.apply(self.original_audio, current_params)

        self.playback_manager.play(processed_audio, start_position_s=current_pos_s)
        self.is_processing_effects = False

    def on_playback_status(self, message: str):

        self.notify_status(message)

    def notify_status(self, message: str):

        if self.status_callback:
            self.status_callback(message)

    def cleanup(self):

        self.playback_manager.cleanup()
        
    @property
    def is_playing(self) -> bool:
     
        return self.playback_manager.is_playing

    def pause(self):
   
        self.playback_manager.pause()

    def resume(self):

        self.playback_manager.resume()
