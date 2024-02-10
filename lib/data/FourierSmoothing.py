import math

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import lfilter, butter, filtfilt

from lib.VideoStream import VideoStream
from lib.infra.FolderStructure import FolderStructure


class FourierSmoothing:

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
    def smooth_array(self, orig_signal: np, cutoff_freq: float) -> np:
        b, a = self.__butter_bandpass(1, cutoff_freq, 25, order=6)
        smooth_signal = filtfilt(b, a, orig_signal, padlen=150)
        return smooth_signal.reshape(-1)

    def saveGraphFFT(self, smooth_signal: np, column_name: str, folder_struct: FolderStructure):
        filepath_prefix = folder_struct.getSubDirpath() + "graph_debug_fft_" + column_name
        png_filepath = filepath_prefix + ".png"
        self._fourierTransformAndPlot(smooth_signal, column_name, png_filepath)

    def __butter_bandpass(self, lowcut, highcut, fs, order=6):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        # b, a = butter(order, [low, high], btype='band')

        b, a = butter(order, high, 'low')
        # b, a = butter(order, highcut, 'low', analog=True)
        return b, a

    def _fourierTransformAndPlot(self, np_array_to_plot: np, title: str, png_filepath: str):
        # np.fft.fft
        #fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(12, 18))

        maximum_frequency = math.ceil(VideoStream.FRAMES_PER_SECOND/2)

        frames_per_second = VideoStream.FRAMES_PER_SECOND  #int(44100/4)
        N = np_array_to_plot.shape[0]  # 17680 #1e5
        time = np.arange(N) / frames_per_second

        freqs = np.fft.fftfreq(time.size, 1/frames_per_second)
        idx = np.argsort(freqs)
        ps = np.abs(np.fft.fft(np_array_to_plot))**2

        plt.xscale("symlog")
        plt.yscale("symlog")

        plt.grid(which='minor', axis='both', linestyle='--')
        plt.grid(which='major', axis='both', linestyle='--')
        plt.xlim(left=0) # don't show negative x axis (values there are just mirror image of postivie, because signal has no complex part)
        plt.xlim(right=maximum_frequency)
        plt.plot(freqs[idx], ps[idx])
        plt.title(title + " - Frequency Domain (logarithmic scales)")
        # plt.title('Power spectrum (np.fft.fft)')

        plt.savefig(png_filepath, format='png', dpi=300)
        plt.close('all')

    def bandpass_filter(self, data: np, lowcut: int, highcut: int, fs:int , order:int = 6) -> np:
        b, a = self.__butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y
