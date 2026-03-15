import heapq
from typing import List, Tuple, Union
from scipy.signal import butter, filtfilt
import numpy as np

class SignalUtils:

    @staticmethod
    def sma(data : list, window : int) -> list:
        """
        smoothing moving average
        
        computes the moving average of a list of numbers

        :param data: list of numbers
        :param window: size of moving window
        :return: smoothed list of numbers
        """
        if not data or window <= 0:
            return []

        result = []
        for i in range(len(data) - window + 1):
            data_win = data[i : i + window]      # aktuelles Fenster
            avg = sum(data_win) / window       # Mittelwert berechnen
            result.append(avg)
        return result

    @staticmethod
    def lowpass_filter(data : Union[np.ndarray | list], f_cutoff : float, fs : float, order : int = 1) -> np.ndarray:
        """ applies a low pass filter defined by cut-off frequency `f_cutoff` and `order`

        Args:
            data (Union[np.ndarray  |  list]): _description_
            f_cutoff (float): _description_
            fs (float): _description_
            order (int, optional): _description_. Defaults to 1.

        Returns:
            np.ndarray: _description_
        """
        nyquist = 0.5 * fs
        normal_cutoff = f_cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def highpass_filter(data : Union[np.ndarray | list], f_cutoff : float, fs : float, order : int = 1) -> np.ndarray:
        """ Apply a zero-phase Butterworth high-pass filter to a 1-D signal.
        This function designs a digital Butterworth high-pass filter with the given
        cutoff frequency and order, and applies it using forward-backward filtering
        (scipy.signal.filtfilt) to avoid phase distortion.
        
        Args:        
            data (Union[np.ndarray, list]):
                1-D input signal samples. Can be a list or NumPy array. The signal is
                filtered along its only dimension; multi-dimensional inputs are not
                supported.
            f_cutoff : float
                Cutoff frequency of the high-pass filter in Hz. This is the frequency
                above which signal components are preserved.
            fs : float
                Sampling frequency of the input signal in samples per second (Hz).
            order : int, optional
                Order of the Butterworth filter. Higher values give a steeper
                roll-off. Default is 1.
        Returns:            
            np.ndarray : Filtered signal as a NumPy array with the same shape as the input.
        Raises
        ------
        ValueError
            If fs is non-positive, f_cutoff is not in the valid range (0 < f_cutoff < fs/2),
            or if order is not a positive integer.
        TypeError
            If the input data cannot be interpreted as a 1-D sequence of numeric values.
        Notes
        -----
        - The filter is designed using scipy.signal.butter and applied with
            scipy.signal.filtfilt for zero-phase filtering (no phase shift).
        - The normalized cutoff frequency passed to butter is f_cutoff / (fs/2).
        - For very low cutoff frequencies or short signals, filtfilt may produce
            edge artifacts; consider padding or a different filtering strategy if needed.
        Examples
        --------
        >>> import numpy as np
        >>> t = np.linspace(0, 1.0, 500, endpoint=False)
        >>> x = np.sin(2*np.pi*1*t) + 0.5*np.sin(2*np.pi*50*t)
        >>> y = highpass_filter(x, f_cutoff=10.0, fs=500.0, order=2)
        """
        nyquist = 0.5 * fs
        normal_cutoff = f_cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return filtfilt(b, a, data)

    @staticmethod
    def bandpass_filter(data : Union[np.ndarray | list], f_low : float, f_high : float, fs : float, order : int = 1) -> np.ndarray:
        """Band-pass filter a 1-D signal using a Butterworth filter and zero-phase filtering.
                
        Args:
            data (Union[np.ndarray, list]): 1-D input signal (array-like). Will be treated as a numpy array.
            f_low (float): Lower cutoff frequency in Hz. Must be >= 0.
            f_high (float): Upper cutoff frequency in Hz. Must be > f_low and < fs/2 (Nyquist).
            fs (float): Sampling frequency of the signal in Hz. Must be > 0.
            order (int, optional): Order of the Butterworth filter (positive integer). Defaults to 1.
            np.ndarray: The bandpass-filtered signal (same shape as the input).
        Raises:
            ValueError: If fs <= 0, f_low < 0, f_low >= f_high, or f_high >= fs / 2.
            ValueError: If the input signal is shorter than the minimum length required by scipy.signal.filtfilt for the given filter order.
            TypeError: If the input data cannot be converted to a 1-D numpy array.
        Notes:
            The function designs a digital Butterworth bandpass filter using scipy.signal.butter
            with normalized cutoff frequencies (cutoff / (fs/2)) and applies zero-phase filtering
            with scipy.signal.filtfilt to avoid phase distortion. Because filtfilt uses edge
            padding, the input signal must be sufficiently long relative to the filter order
            (see scipy.signal.filtfilt documentation for padlen behavior). For very narrow bands
            or high orders, consider increasing the signal length or lowering the filter order.
        Example:
            >>> import numpy as np
            >>> t = np.linspace(0, 1.0, 500, endpoint=False)
            >>> sig = np.sin(2*np.pi*10*t) + 0.5*np.sin(2*np.pi*50*t)
            >>> filtered = bandpass_filter(sig, f_low=8.0, f_high=12.0, fs=500.0)
        """
        nyquist = 0.5 * fs
        normal_low_cutoff = f_low / nyquist
        normal_high_cutoff = f_high / nyquist
        b, a = butter(order, [normal_low_cutoff, normal_high_cutoff], btype='bandpass', analog=False)
        return filtfilt(b, a, data)
    
    @staticmethod
    def fft(data : Union[np.ndarray | list], f_s : float) -> Tuple[np.ndarray, np.ndarray]:
        """
        computes the amplitude spectrum of th signal `data`
        
        Parameters
        ----------
        y : array-like
            input signal in time domain
        f_s : float
            sample rate in Hz

        Returns
        -------
        f : ndarray
            frequency domain in Hz
        A : ndarray
            Amplitude of spectrum
        """

        n = len(data)                       # number of samples
        p = np.fft.rfft(data)               # einseitige FFT
        a = np.abs(p) * 2 / n            # Amplitude skalieren
        
        f = np.fft.rfftfreq(n, d = 1 / f_s)  # Frequenzachse
        return f, a
    
    @staticmethod
    def timeseries_thinning(timestamps : list | np.ndarray, n : int) ->  Tuple[Union[List[float], np.ndarray], Union[List[float], np.ndarray]]: 
        """
        Reduces the number of timestamps in a time series to a specified number `n` by iteratively removing points that form the tightest clusters, preserving the overall distribution as much as possible.
        
        Args:
            timestamps (list or np.ndarray): The original sequence of timestamps to be thinned.
            n (int): The desired number of timestamps to retain.
        
        Returns:
            Tuple[Union[List[float], np.ndarray], Union[List[float], np.ndarray]]:
                A tuple containing:
                    - The thinned list or array of timestamps.
                    - The corresponding indices of the retained timestamps in the original sequence.
        """
        indices : np.ndarray = np.linspace(0, len(timestamps) - 1, len(timestamps))
        indices : list = indices.tolist()
        if len(timestamps) <= n:
            if isinstance(timestamps, list):
                return timestamps, indices
            else:
                return timestamps, np.ndarray(indices)
        
        new_timestamps = list(timestamps)
    
        while len(new_timestamps) > n:
            heap = []
            # compute removal cost for each interior element
            for i in range(1, len(new_timestamps) - 1):

                prev_gap = new_timestamps[i] - new_timestamps[i-1]
                next_gap = new_timestamps[i+1] - new_timestamps[i]

                merged_gap = prev_gap + next_gap

                # smaller merged gap → tighter cluster → higher removal priority
                heapq.heappush(heap, (merged_gap, i))

            _, idx = heapq.heappop(heap)

            new_timestamps.pop(idx)
            indices.pop(idx)
        if isinstance(timestamps, np.ndarray):
            return np.ndarray(new_timestamps), np.ndarray(indices)
        else:
            return new_timestamps, indices