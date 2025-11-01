from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
import librosa
import librosa.display

def test_000():
    # Tiefpass definieren
    def butter_lowpass_filter(data, cutoff, fs, order=4):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    # Beispiel: Sinus + Rauschen
    fs = 500  # Abtastrate in Hz
    t = np.linspace(0, 1, fs)
    signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)

    # Filter anwenden
    cutoff = 50  # Grenzfrequenz in Hz
    filtered_signal = butter_lowpass_filter(signal, cutoff, fs)

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(t, signal, label='Original')
    plt.plot(t, filtered_signal, label='Gefiltert', linewidth=2)
    plt.legend()
    plt.title('Butterworth-Tiefpassfilter')
    plt.show()
    
def test_010():
    # Load audio file
    y, sr = librosa.load("audio.wav")

    # Compute Short-Time Fourier Transform (STFT)
    S = np.abs(librosa.stft(y))

    # Convert to decibels
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    # Plot
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', cmap='magma')
    plt.colorbar(format="%+2.0f dB")
    plt.title("Spectrogram")
    plt.tight_layout()
    plt.show()