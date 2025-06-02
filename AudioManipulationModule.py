import pygame
import numpy as np
from pydub import AudioSegment
import threading
import time
import tempfile
import os
import io
from typing import Optional, Callable, Dict, Any
from threading import Lock


class AudioManipulator:

    def __init__(self, sample_rate: int = 22050, buffer_size: int = 1024):

        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=buffer_size)
        pygame.mixer.init()

        self.original_audio: Optional[AudioSegment] = None
        self.current_audio: Optional[AudioSegment] = None
        self.is_playing: bool = False
        self.current_position: float = 0.0
        self.audio_length: float = 0.0
        self.temp_file: Optional[str] = None
        self.sample_rate = sample_rate

        self._volume: float = 1.0
        self._speed: float = 1.0
        self._pitch: float = 1.0
        self._bass: float = 0.0
        self._treble: float = 0.0

        self._parameter_lock = Lock()
        self._file_lock = Lock()
        self._effects_processing = False

        self._update_thread: Optional[threading.Thread] = None
        self._stop_update: bool = False

        self._progress_callback: Optional[Callable[[float, float], None]] = None
        self._status_callback: Optional[Callable[[str], None]] = None

        self._temp_files = []

    def load_file(self, file_path: str) -> bool:

        try:
            with self._file_lock:
                self.original_audio = AudioSegment.from_file(file_path)
                self.current_audio = self.original_audio
                self.audio_length = len(self.original_audio)
                self.current_position = 0.0
                self._notify_status("File loaded successfully")
                return True
        except Exception as e:
            self._notify_status(f"Error loading file: {str(e)}")
            return False

    def load_from_bytes(self, audio_data: bytes, format: str = "mp3") -> bool:
        try:
            with self._file_lock:
                self.original_audio = AudioSegment.from_file(
                    io.BytesIO(audio_data), format=format
                )
                self.current_audio = self.original_audio
                self.audio_length = len(self.original_audio)
                self.current_position = 0.0
                self._notify_status("Audio loaded from bytes")
                return True
        except Exception as e:
            self._notify_status(f"Error loading audio from bytes: {str(e)}")
            return False

    def set_volume(self, volume: float) -> None:
        with self._parameter_lock:
            self._volume = max(0.0, min(2.0, volume))
            if self.is_playing:
                pygame.mixer.music.set_volume(self._volume)

    def set_speed(self, speed: float) -> None:
        with self._parameter_lock:
            self._speed = max(0.1, min(3.0, speed))
            if self.is_playing and not self._effects_processing:
                self._apply_effects_async()

    def set_pitch(self, pitch: float) -> None:
        with self._parameter_lock:
            self._pitch = max(0.1, min(3.0, pitch))
            if self.is_playing and not self._effects_processing:
                self._apply_effects_async()

    def set_bass(self, bass: float) -> None:
        with self._parameter_lock:
            self._bass = max(-10.0, min(10.0, bass))
            if self.is_playing and not self._effects_processing:
                self._apply_effects_async()

    def set_treble(self, treble: float) -> None:
        with self._parameter_lock:
            self._treble = max(-10.0, min(10.0, treble))
            if self.is_playing and not self._effects_processing:
                self._apply_effects_async()

    def get_parameters(self) -> Dict[str, float]:
        with self._parameter_lock:
            return {
                'volume': self._volume,
                'speed': self._speed,
                'pitch': self._pitch,
                'bass': self._bass,
                'treble': self._treble
            }

    def set_parameters(self, **kwargs) -> None:
        with self._parameter_lock:
            effects_changed = False

            if 'volume' in kwargs:
                self._volume = max(0.0, min(2.0, kwargs['volume']))
                if self.is_playing:
                    pygame.mixer.music.set_volume(self._volume)

            if 'speed' in kwargs:
                self._speed = max(0.1, min(3.0, kwargs['speed']))
                effects_changed = True

            if 'pitch' in kwargs:
                self._pitch = max(0.1, min(3.0, kwargs['pitch']))
                effects_changed = True

            if 'bass' in kwargs:
                self._bass = max(-10.0, min(10.0, kwargs['bass']))
                effects_changed = True

            if 'treble' in kwargs:
                self._treble = max(-10.0, min(10.0, kwargs['treble']))
                effects_changed = True

        if effects_changed and self.is_playing and not self._effects_processing:
            self._apply_effects_async()

    def reset_parameters(self) -> None:
        with self._parameter_lock:
            self._volume = 1.0
            self._speed = 1.0
            self._pitch = 1.0
            self._bass = 0.0
            self._treble = 0.0

        if self.is_playing:
            pygame.mixer.music.set_volume(self._volume)
            if not self._effects_processing:
                self._apply_effects_async()

    def play(self, start_position: float = 0.0) -> bool:
        if self.original_audio is None:
            self._notify_status("No audio file loaded")
            return False

        try:
            with self._file_lock:
                self.current_position = start_position * 1000
                self._apply_effects()
                temp_file = self._save_temp_file()

                if temp_file:
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play(start=start_position)
                    pygame.mixer.music.set_volume(self._volume)

                    self.is_playing = True
                    self._notify_status("Playing")
                    self._start_progress_tracking()
                    return True
        except Exception as e:
            self._notify_status(f"Error starting playback: {str(e)}")
            return False

        return False

    def pause(self) -> None:
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self._stop_update = True
            self._notify_status("Paused")

    def resume(self) -> None:
        if not self.is_playing and self.original_audio:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self._notify_status("Playing")
            self._start_progress_tracking()

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_position = 0.0
        self._stop_update = True
        self._notify_status("Stopped")

    def seek(self, position: float) -> bool:
        if self.original_audio is None:
            return False

        position_ms = position * 1000
        if 0 <= position_ms <= self.audio_length:
            was_playing = self.is_playing
            if was_playing:
                self.stop()

            self.current_position = position_ms

            if was_playing:
                return self.play(position)
            return True
        return False

    def get_position(self) -> float:
        return self.current_position / 1000.0

    def get_duration(self) -> float:
        return self.audio_length / 1000.0

    def get_progress(self) -> float:
        if self.audio_length > 0:
            return (self.current_position / self.audio_length) * 100
        return 0.0

    def is_audio_loaded(self) -> bool:
        return self.original_audio is not None

    def export_current_audio(self, output_path: str, format: str = "mp3") -> bool:
        if self.original_audio is None:
            return False

        try:
            with self._file_lock:
                self._apply_effects()
                self.current_audio.export(output_path, format=format)
                self._notify_status(f"Audio exported to {output_path}")
                return True
        except Exception as e:
            self._notify_status(f"Error exporting audio: {str(e)}")
            return False

    def set_progress_callback(self, callback: Callable[[float, float], None]) -> None:
        self._progress_callback = callback

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        self._status_callback = callback

    def _apply_effects(self) -> None:
        if self.original_audio is None:
            return

        try:
            with self._parameter_lock:
                volume = self._volume
                speed = self._speed
                pitch = self._pitch
                bass = self._bass
                treble = self._treble

            audio = self.original_audio

            if volume != 1.0:
                if volume > 0.001:
                    volume_db = 20 * np.log10(volume)
                    audio = audio + volume_db
                else:
                    audio = audio - 60

            if speed != 1.0:
                new_sample_rate = int(audio.frame_rate * speed)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(self.sample_rate)

            if pitch != 1.0 and pitch != speed:
                pitch_shift = pitch / speed
                new_sample_rate = int(audio.frame_rate * pitch_shift)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(self.sample_rate)

            if bass != 0.0:
                bass_gain = bass * 0.5
                audio = audio + bass_gain

            if treble != 0.0:
                treble_gain = treble * 0.3
                audio = audio + treble_gain

            self.current_audio = audio

        except Exception as e:
            print(f"Error applying effects: {e}")
            self.current_audio = self.original_audio

    def _apply_effects_async(self) -> None:
        if self._effects_processing:
            return

        def apply_in_thread():
            try:
                self._effects_processing = True

                if not pygame.mixer.music.get_busy():
                    return

                current_pos = self.current_position / 1000.0

                with self._file_lock:
                    self._apply_effects()
                    temp_file = self._save_temp_file()

                    if temp_file and os.path.exists(temp_file):
                        pygame.mixer.music.load(temp_file)
                        pygame.mixer.music.play(start=current_pos)
                        pygame.mixer.music.set_volume(self._volume)

            except Exception as e:
                print(f"Error in async effects application: {e}")
            finally:
                self._effects_processing = False

        threading.Thread(target=apply_in_thread, daemon=True).start()

    def _save_temp_file(self) -> Optional[str]:
        if self.current_audio is None:
            return None

        try:
            temp_fd, temp_file = tempfile.mkstemp(suffix='.wav', prefix='handdj_')
            os.close(temp_fd)

            self.current_audio.export(temp_file, format="wav")

            self._cleanup_old_temp_files()

            self._temp_files.append(temp_file)
            self.temp_file = temp_file

            return temp_file

        except Exception as e:
            print(f"Error saving temp file: {e}")
            return None

    def _cleanup_old_temp_files(self):
        try:
            while len(self._temp_files) > 2:
                old_file = self._temp_files.pop(0)
                if old_file and os.path.exists(old_file):
                    try:
                        os.unlink(old_file)
                    except OSError:
                        pass
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

    def _start_progress_tracking(self) -> None:
        self._stop_update = False
        if self._update_thread and self._update_thread.is_alive():
            return

        self._update_thread = threading.Thread(target=self._update_progress, daemon=True)
        self._update_thread.start()

    def _update_progress(self) -> None:
        while not self._stop_update and self.is_playing:
            try:
                if pygame.mixer.music.get_busy():
                    self.current_position += 100
                    if self.current_position >= self.audio_length:
                        self.current_position = self.audio_length
                        self._stop_update = True
                        self.is_playing = False
                        self._notify_status("Finished")
                        break

                    if self._progress_callback:
                        self._progress_callback(
                            self.current_position / 1000.0,
                            self.audio_length / 1000.0
                        )
                else:
                    self.stop()
                    break

                time.sleep(0.1)
            except Exception as e:
                print(f"Error in progress update: {e}")
                break

    def _notify_status(self, message: str) -> None:
        if self._status_callback:
            try:
                self._status_callback(message)
            except Exception as e:
                print(f"Error in status callback: {e}")

    def cleanup(self) -> None:
        self.stop()

        for temp_file in self._temp_files[:]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
        self._temp_files.clear()

        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except OSError:
                pass

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    def progress_callback(current, total):
        print(f"Progress: {current:.1f}s / {total:.1f}s ({current / total * 100:.1f}%)")

    def status_callback(status):
        print(f"Status: {status}")

    manipulator = AudioManipulator()

    manipulator.set_progress_callback(progress_callback)
    manipulator.set_status_callback(status_callback)

    print("Audio manipulator module loaded successfully!")
    print("Usage example:")
    print("  manipulator = AudioManipulator()")
    print("  manipulator.load_file('audio.mp3')")
    print("  manipulator.set_volume(1.5)")
    print("  manipulator.set_speed(0.8)")
    print("  manipulator.play()")