
import numpy as np
from pydub import AudioSegment
from scipy import signal
from typing import Dict, Tuple


class ReverbEffect:
    # This uses a convolution reverb (room, hall, plate).

    def __init__(self):
        # Cache impulse responses per (sr, time, type)
        self.cache: Dict[Tuple[int, float, str], np.ndarray] = {}
        self.setup_reverb_types()

    def setup_reverb_types(self):
        self.types = {
            'room': {
                'decay_rate': 3.0, 'room_size': 0.3, 'damping': 0.7,
                'early_reflections': [(0.008, 0.18), (0.015, 0.14), (0.025, 0.10), (0.042, 0.06)]
            },
            'hall': {
                'decay_rate': 2.0, 'room_size': 0.7, 'damping': 0.5,
                'early_reflections': [(0.012, 0.15), (0.028, 0.12), (0.048, 0.08), (0.075, 0.05)]
            },
            'plate': {
                'decay_rate': 4.0, 'room_size': 0.4, 'damping': 0.8,
                'early_reflections': [(0.003, 0.20), (0.007, 0.16), (0.013, 0.12), (0.021, 0.08)]
            },
        }

    def apply(self, audio: AudioSegment, reverb_amount: float) -> AudioSegment:
        if reverb_amount <= 0.0:
            return audio

        # Map control to tail length and pick a preset
        time_s = float(np.interp(reverb_amount, [0.0, 2.0], [0.1, 1.2]))
        rtype = self.pick_type(reverb_amount)

        x = self.to_array(audio)
        ir = self.get_ir(audio.frame_rate, time_s, rtype)
        y = self.convolve_reverb(x, ir, reverb_amount, audio.frame_rate)
        return self.to_audio(y, audio)

    def pick_type(self, reverb_amount: float) -> str:
        if reverb_amount < 0.7:
            return 'room'
        if reverb_amount < 1.4:
            return 'hall'
        return 'plate'

    def get_ir(self, sr: int, time_s: float, rtype: str) -> np.ndarray:
        # Use cached IR when possible
        key = (int(sr), round(float(time_s), 3), rtype)
        if key not in self.cache:
            self.cache[key] = self.generate_ir(sr, time_s, rtype)
        return self.cache[key]

    def generate_ir(self, sr: int, time_s: float, rtype: str) -> np.ndarray:
        # Impulse response: early echoes + fading tail + gentle tone shaping
        cfg = self.types.get(rtype, self.types['room'])
        length = max(8, int(sr * time_s))

        decay = np.exp(-np.linspace(0, cfg['decay_rate'], length))
        rng = np.random.RandomState(42)
        noise = rng.randn(length) * 0.02 * cfg['damping']

        early = np.zeros(length)
        for dt, g in cfg['early_reflections']:
            d = int(dt * sr)
            if d < length:
                ws = max(1, int(sr * 0.002))
                s = max(0, d - ws // 2)
                e = min(length, d + ws // 2)
                if e > s:
                    early[s:e] += g * signal.windows.hann(e - s)

        ir = decay * (0.85 + noise) + early * cfg['room_size']

        # Tone shaping
        nyq = sr / 2.0
        b_hp, a_hp = signal.butter(2, 80.0 / nyq, 'high')
        ir = signal.filtfilt(b_hp, a_hp, ir)
        b_lp, a_lp = signal.butter(3, min(12000.0, nyq * 0.8) / nyq, 'low')
        ir = signal.filtfilt(b_lp, a_lp, ir)
        b_hf, a_hf = signal.butter(1, 800.0 / nyq, 'high')
        ir = ir * 0.7 + signal.filtfilt(b_hf, a_hf, ir) * 0.3

        # Smooth start, remove DC, set sensible level
        nfade = int(sr * 0.001)
        if len(ir) > nfade:
            ir[:nfade] *= np.sin(np.linspace(0, np.pi / 2, nfade)) ** 2
        ir = ir - np.mean(ir)
        l2 = float(np.sqrt(np.sum(ir.astype(np.float64) ** 2)))
        if l2 > 1e-12:
            ir /= l2
        ir *= 0.35
        return ir.astype(np.float32)

    def wet_dry(self, amount: float) -> Tuple[float, float]:
        # Equal-power blend between original and reverb 
        t = float(np.clip(amount / 2.0, 0.0, 1.0))
        a = t * (np.pi / 2.0)
        return float(np.sin(a)), float(np.cos(a))

    def to_array(self, audio: AudioSegment) -> np.ndarray:
        # 16-bit PCM -> float32 [-1, 1]; stereo -> (N, 2)
        arr = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        if audio.channels == 2:
            arr = arr.reshape((-1, 2))
        return arr

    def to_audio(self, arr: np.ndarray, ref: AudioSegment) -> AudioSegment:
        arr = np.clip(arr, -1.0, 1.0)
        i16 = np.ascontiguousarray((arr * 32767.0).astype(np.int16))
        return ref._spawn(i16.tobytes())

    def convolve_reverb(self, x: np.ndarray, ir: np.ndarray, amount: float, sr: int) -> np.ndarray:
        # Convolution + small stereo crossfeed; high-pass wet; RMS match
        wet, dry = self.wet_dry(amount)
        X = x if x.ndim == 2 else x.reshape(-1, 1)
        Y = np.zeros_like(X)

        nyq = sr / 2.0
        hp = min(0.99, 120.0 / nyq)
        b_hp, a_hp = signal.butter(2, hp, 'high')

        for ch in range(X.shape[1]):
            wd = signal.fftconvolve(X[:, ch], ir, mode='same')
            if X.shape[1] == 2:
                wc = signal.fftconvolve(X[:, 1 - ch], ir, mode='same')
                w = wd * 0.8 + wc * 0.2
            else:
                w = wd
            try:
                w = signal.filtfilt(b_hp, a_hp, w)
            except Exception:
                pass
            Y[:, ch] = X[:, ch] * dry + w * wet

        xr = float(np.sqrt(np.mean(X.astype(np.float64) ** 2))) + 1e-12
        yr = float(np.sqrt(np.mean(Y.astype(np.float64) ** 2))) + 1e-12
        if yr > xr:
            Y *= (xr / yr)

        out = Y if x.ndim == 2 else Y[:, 0]
        return self.post(out)

    def post(self, y: np.ndarray) -> np.ndarray:
        # Soft clip and cap peak
        y = np.tanh(y * 0.95) * 0.92
        pk = float(np.max(np.abs(y)))
        if pk > 0.95:
            y = y / pk * 0.95
        return y