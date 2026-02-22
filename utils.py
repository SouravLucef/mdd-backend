import numpy as np
import mne
from scipy.stats import kurtosis, skew
from scipy.signal import welch

common_channels = [
    'EEG F3-LE', 'EEG F4-LE', 'EEG F7-LE', 'EEG F8-LE',
    'EEG Fp1-LE', 'EEG Fp2-LE', 'EEG Fz-LE', 'EEG O1-LE',
    'EEG O2-LE', 'EEG P3-LE', 'EEG P4-LE', 'EEG Pz-LE',
    'EEG T3-LE', 'EEG T4-LE', 'EEG T5-LE', 'EEG T6-LE'
]

def preprocess_eeg(filepath):
    raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
    raw.pick_channels(common_channels)
    raw.filter(1., 40., fir_design='firwin')
    raw.set_eeg_reference('average', projection=True)
    events = mne.make_fixed_length_events(raw, duration=10.0, overlap=0.5)
    epochs = mne.Epochs(raw, events, tmin=0, tmax=10.0, baseline=None, detrend=1, preload=True, verbose=False)
    return epochs

def extract_features(epochs):
    features = []
    for ep in epochs.get_data():  # shape: (n_channels, n_times)
        feat = []
        for ch in ep:
            f, psd = welch(ch, fs=epochs.info['sfreq'])
            psd_mean = np.mean(psd)
            psd_std = np.std(psd)
            hjorth_activity = np.var(ch)
            hjorth_mobility = np.std(np.diff(ch)) / np.std(ch)
            hjorth_complexity = (np.std(np.diff(np.diff(ch))) / np.std(np.diff(ch))) / hjorth_mobility
            aar = np.polyfit(range(len(ch)), ch, deg=3)[:3]
            feat.extend([psd_mean, psd_std, hjorth_activity, hjorth_mobility, hjorth_complexity, *aar, skew(ch), kurtosis(ch)])
        features.append(feat)
    return np.array(features)

def extract_eeg_plot_data(filepath, duration_sec=5):
    raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
    raw.pick_channels(common_channels)
    raw.filter(1., 40., fir_design='firwin')
    raw.set_eeg_reference('average', projection=True)
    channels=common_channels
    sfreq = raw.info['sfreq']
    n_samples = int(5 * sfreq)

    data = raw.get_data(picks=channels)[:, :n_samples]
    times = raw.times[:n_samples]

    eeg_data = {
        ch: data[i].tolist()
        for i, ch in enumerate(channels)
    }

    return eeg_data, times.tolist()
