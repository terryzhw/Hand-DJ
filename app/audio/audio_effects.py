import numpy as np
from pydub import AudioSegment
from typing import Dict
from modules import constants as C
from audio.reverb_effect import ReverbEffect


class AudioEffects:
    # This is the audio effects processor which manages volume, pitch, and reverb
    
    def __init__(self):
        self.reverb = ReverbEffect()

    def apply(self, audio: AudioSegment, params: Dict) -> AudioSegment:
        # Apply all audio effects based on provided parameters.
        
        if not isinstance(audio, AudioSegment):
            raise TypeError("Input must be a pydub AudioSegment")

        # Extract parameters with defaults
        volume = params.get('volume', C.DEFAULT_VOLUME)
        pitch = params.get('pitch', C.DEFAULT_PITCH)
        reverb = params.get('reverb', C.DEFAULT_REVERB)
        target_sample_rate = params.get('sample_rate', C.DEFAULT_SAMPLE_RATE)

        # Apply effects in optimal order (volume -> pitch -> reverb)
        processed_audio = self.apply_volume(audio, volume)
        processed_audio = self.apply_pitch(processed_audio, pitch, target_sample_rate)
        processed_audio = self.apply_reverb(processed_audio, reverb)
        
        return processed_audio

    def apply_volume(self, audio: AudioSegment, volume: float) -> AudioSegment:
        # Apply volume adjustment using logarithmic scaling.
        if abs(volume - 1.0) < 0.001: 
            return audio
            
        if volume > 0.001:
            db_change = 20 * np.log10(volume)
            db_change = np.clip(db_change, -60, 12)  
            return audio + db_change
        else:
            return audio - 60

    def apply_pitch(self, audio: AudioSegment, pitch: float, target_sample_rate: int) -> AudioSegment:

        # Applies pitch by altering frame rate
        if abs(pitch - 1.0) < 0.001:  
            return audio
        
        new_frame_rate = int(audio.frame_rate * pitch)
        pitched_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
        return pitched_audio.set_frame_rate(target_sample_rate)

    def apply_reverb(self, audio: AudioSegment, reverb: float) -> AudioSegment:
        # Using reverb class, apply reverb to audio
        return self.reverb.apply(audio, reverb)
