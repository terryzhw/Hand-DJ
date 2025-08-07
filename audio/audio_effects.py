import numpy as np
from pydub import AudioSegment
from modules.constants import *


class AudioEffects:
    def apply(self, audio: AudioSegment, params: dict) -> AudioSegment:
        if not isinstance(audio, AudioSegment):
            raise TypeError("Input must be a pydub AudioSegment")

        volume = params.get('volume', DEFAULT_VOLUME)
        speed = params.get('speed', DEFAULT_SPEED)
        pitch = params.get('pitch', DEFAULT_PITCH)
        reverb = params.get('reverb', DEFAULT_REVERB)
        treble = params.get('treble', DEFAULT_TREBLE)
        target_sample_rate = params.get('sample_rate', DEFAULT_SAMPLE_RATE)

        modified_audio = self.apply_volume(audio, volume)
        modified_audio = self.apply_speed_and_pitch(modified_audio, speed, pitch, target_sample_rate)
        modified_audio = self.apply_eq(modified_audio, reverb, treble)
        return modified_audio

    def apply_volume(self, audio: AudioSegment, volume: float) -> AudioSegment:
        if volume == 1.0:
            return audio
        if volume > 0.001:
            db = 20 * np.log10(volume)
            return audio + db
        else:
            return audio - 60

    def apply_speed_and_pitch(self, audio: AudioSegment, speed: float, pitch: float, target_sample_rate: int) -> AudioSegment:
        if speed == 1.0 and pitch == 1.0:
            return audio

        if speed != 1.0:
            new_frame_rate = int(audio.frame_rate * speed)
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
            audio = audio.set_frame_rate(target_sample_rate)
        
        if pitch != 1.0 and pitch != speed:
            pitch_shift_ratio = pitch / speed
            new_frame_rate = int(audio.frame_rate * pitch_shift_ratio)
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
            audio = audio.set_frame_rate(target_sample_rate)

        return audio

    def apply_eq(self, audio: AudioSegment, reverb: float, treble: float) -> AudioSegment:
        if reverb > 0.0:
            audio += reverb * 0.5
        if treble != 0.0:
            audio += treble * 0.3
        return audio
