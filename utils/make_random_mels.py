import numpy as np
import librosa
import librosa.filters
from addict import Dict
from audiomentations import *
from scipy import signal

# Default hyperparameters
hp = Dict(
    
	num_mels=96,        # Number of mel-spectrogram channels and local conditioning dimensionality
	n_fft=800,          # Extra window size is filled with 0 paddings to match this parameter
	hop_size=200,       # For 16000Hz, 200 = 12.5 ms (0.0125 * sample_rate)
	win_size=800,       # For 16000Hz, 800 = 50 ms (If None, win_size = n_fft) (0.05 * sample_rate)
	sample_rate=16000,  # 16000Hz (corresponding to librispeech) (sox --i <filename>)
	
	# Contribution by @begeekmyfriend
	# Spectrogram Pre-Emphasis (Lfilter: Reduce spectrogram noise and helps model certitude 
	# levels. Also allows for better G&L phase reconstruction)
	preemphasis=0.97,  # filter coefficient.
	
    
    # for normalization
	max_abs_value=4., # max absolute value of data. 
                      # If symmetric, data will be [-max, max] else [0, max] 
                      # (Must not  be too big to avoid gradient explosion, 
                      # not too small for fast convergence)
    
	# Limits
	min_level_db=-100,
	ref_level_db=20,
    
    fmin=55, # Set this to 55 if your speaker is male! if female, 95 should help taking off noise. 
             # (To test depending on dataset. Pitch info: male~[65, 260], female~[100, 525])
	fmax=7600,  # To be increased/reduced depending on data.
)


def load_wav(path, sr=hp.sample_rate):
    return librosa.core.load(path, sr=sr)[0]

def melspectrogram(wav):
    D = _stft(preemphasis(wav, hp.preemphasis))
    S = _amp_to_db(_linear_to_mel(np.abs(D))) - hp.ref_level_db
    return _normalize(S)

def _stft(y):
    return librosa.stft(y=y, n_fft=hp.n_fft, hop_length=hp.hop_size, win_length=hp.win_size)

def _amp_to_db(x):
    min_level = np.exp(hp.min_level_db / 20 * np.log(10))
    return 20 * np.log10(np.maximum(min_level, x))

def preemphasis(wav, k):
    return signal.lfilter([1, -k], [1], wav)

def _normalize(S):
    return np.clip((2 * hp.max_abs_value) * ((S - hp.min_level_db) / (-hp.min_level_db)) - hp.max_abs_value,
                      -hp.max_abs_value, hp.max_abs_value)


def _build_mel_basis():
    assert hp.fmax <= hp.sample_rate // 2
    return librosa.filters.mel(hp.sample_rate, hp.n_fft, n_mels=hp.num_mels,
                               fmin=hp.fmin, fmax=hp.fmax)


def _linear_to_mel(spectogram):
    return np.dot(_mel_basis, spectogram)


_mel_basis = _build_mel_basis()


#################################################################
from pathlib import Path

def load_wav_to_mels(wav_path):
    wav  = load_wav(wav_path)
    augment = SomeOf(
        2,
        [AddGaussianNoise(p=0.5),
        AddGaussianSNR(p=0.5),
        AirAbsorption(p=0.5),
        BandPassFilter(p=0.5),
        BandStopFilter(p=0.5),
        ClippingDistortion(p=0.5),
        LowPassFilter(p=0.5),
        PitchShift(p=0.5),
        RoomSimulator(p=0.5),
        SevenBandParametricEQ(p=0.5),
        TanhDistortion(p=0.5)
    ])  
    wav_aug = augment(samples=wav, sample_rate=hp.sample_rate)
    return  melspectrogram(wav_aug) 

def save_mels(wav_path):
    for i in range(100):
        spec = load_wav_to_mels(wav_path) 
        mels_path = Path(wav_path).parent/f'mels_{i:03d}'
    
        np.savez_compressed(mels_path, spec=spec)
