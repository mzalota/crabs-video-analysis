import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from scipy.signal import lfilter, butter

from lib.data.Correlation import Correlation


class FourierSmoothing:
    def smooth_curve(self, column_to_smooth, column_name, cutoff_freq=0.1):

        #column_to_smooth = df[column_name]
        orig_np = column_to_smooth.to_numpy()
        dist_freq1 = self.bandpass_filter(orig_np, 1, cutoff_freq, 25)
        corr = Correlation(dist_freq1, orig_np)

        phase_shift = corr.offset_of_peak_from_center()

        dataset = pd.DataFrame()
        dataset['distance_streight'] = dist_freq1.reshape(-1)
        shifted = dataset['distance_streight'].shift(-phase_shift)

        self._draw_fft_lowpass(orig_np, column_name, 0.1)
        self.save_plot_numpy_as_png("c:/tmp/maxim_corr.png", corr.corr_np())
        print("offset_of_peak_from_center", phase_shift)
        #dataset['distance_streight'] = dataset['distance_streight'].astype(int)

        return shifted

    def _draw_fft_lowpass(self, orig_np, column_name, cutoff_freq=0.1):
        lowpass_np = self.bandpass_filter(orig_np, 1, cutoff_freq, 25)
        print(column_name, orig_np)
        png_filepath = "c:/tmp/maximFFT_" + column_name + ".png"
        self._plotFourierGraph(orig_np, column_name, png_filepath)
        self.save_plot_numpy_as_png("c:/tmp/maxim_" + column_name + ".png", orig_np[8000:10000])
        self.save_plot_numpy_as_png("c:/tmp/maxim_" + column_name + "_after_filter.png", lowpass_np[8000:10000])
        return lowpass_np

    def _plotFourierGraph(self, np_array_to_plot: np, title: str, png_filepath: str):
        # np.fft.fft
        fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(12, 18))
        fs = 25  #int(44100/4)
        N = np_array_to_plot.shape[0]  # 17680 #1e5
        time = np.arange(N) / fs

        freqs = np.fft.fftfreq(time.size, 1/fs)
        idx = np.argsort(freqs)
        ps = np.abs(np.fft.fft(np_array_to_plot))**2

        plt.xscale("symlog")
        plt.yscale("symlog")
        # plt.grid(which='minor', axis='both', linestyle='--')
        plt.grid(which='major', axis='both', linestyle='--')
        plt.xlim(left=1)
        plt.xlim(right=20)
        plt.plot(freqs[idx], ps[idx])
        plt.title(title)
        # plt.title('Power spectrum (np.fft.fft)')


        plt.savefig(png_filepath, format='png', dpi=300)
        plt.close('all')

    def save_plot_numpy_as_png(self, filepath_image: str, nparr:np):
        figure(num=None, figsize=(30, 6), facecolor='w', edgecolor='k')
        plt.plot(nparr)
        plt.gca().grid(which='major', axis='both', linestyle='--', )  # specify grid lines
        plt.savefig(filepath_image, format='png', dpi=300)

    def bandpass_filter(self, data: np, lowcut: int, highcut: int, fs:int , order:int = 6) -> np:
        b, a = self._butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def _butter_bandpass(self, lowcut, highcut, fs, order=6):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        # b, a = butter(order, [low, high], btype='band')

        b, a = butter(order, high, 'low')
        # b, a = butter(order, highcut, 'low', analog=True)
        return b, a
