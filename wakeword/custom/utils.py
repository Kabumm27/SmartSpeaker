import numpy as np
from scipy.io import wavfile
from python_speech_features import mfcc, delta


def wav2mfcc(file_path, max_padding=31, target_sample_rate = 16000, noise_probability = 0.0):
    sample_rate, samples = wavfile.read(file_path)
    return audio2mfcc(samples, sample_rate, max_padding, noise_probability)

def audio2mfcc(samples, sample_rate, max_padding=31, noise_probability = 0.0):
    # Add noise
    if noise_probability >= 0.0:
        rand = np.random.rand(1)
        if rand <= noise_probability:
            intensity = np.random.rand(1) * 0.2 + 0.1
            sampples = add_noise(samples, sample_rate, intensity)

    # Mel Spectogram
    # S = librosa.feature.melspectrogram(samples.astype(np.float32), sr=sample_rate, n_mels=128)
    # log_S = librosa.power_to_db(S, ref=np.max) # shape = 128 x ?

    # MFCC
    # mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=13)
    # delta2_mfcc = librosa.feature.delta(mfcc, order=2) # shape = 13 x ?

    mfcc_features = mfcc(samples, sample_rate, nfft=2000, winlen=0.100, winstep=0.03)
    delta_mffc_features = delta(mfcc_features, 2)
    delta_mffc_features = delta_mffc_features.T

    # Padding
    pad_width = max_padding - delta_mffc_features.shape[1]
    delta_mffc_features = np.pad(delta_mffc_features, pad_width=((0, 0), (0, pad_width)), mode='constant') # shape = 13 x 31 for 1 sec data

    return delta_mffc_features

def add_noise(samples, sample_rate, intensity):
    # noise_samples, _ = librosa.load(join('data/_background_noise_', 'pink_noise.wav'), mono=True, sr=sample_rate)
    
    # start_index = np.random.randint(len(samples), len(noise_samples) - len(samples))
    # noise_samples = noise_samples[start_index:start_index + len(samples)]

    noise_samples = np.random.rand(samples.shape[0])

    return samples * noise_samples


