from scipy.signal import butter, filtfilt
import numpy as np
import matplotlib.pyplot as plt

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