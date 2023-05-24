import numpy as np
from scipy import signal


class Correlation:
    def __init__(self, dist_freq1: np, orig_np: np):
        self._corr = self.__correlate_two_numpy_arrays(dist_freq1, orig_np)

    def corr_np(self) ->np:
        return self._corr

    def argmax(self) -> int:
        return np.argmax(self._corr)

    def argmin(self) -> int:
        return np.argmin(self._corr)

    def max_correlation(self) ->float:
        return np.max(self._corr)

    def min_correlation(self)->float:
        return np.min(self._corr)

    def location_of_peak(self) -> int:
        if self.__min_corr_is_better_than_max():
            return self.argmin()
        else:
            return self.argmax()

    def location_of_center(self) -> int:
        return int(self.length() / 2)

    def offset_of_peak_from_center(self) -> int:
        return self.location_of_peak() - self.location_of_center()

    def __min_corr_is_better_than_max(self):
        if abs(self.min_correlation()) > self.max_correlation():
            return True
        else:
            return False

    def length(self) -> int:
        return len(self._corr)

    def __correlate_two_numpy_arrays(self, signal_to_search: np, snippet: np) -> np:
        # values input nparrays are expected to be of type float. If they are integers, correlation produces wierd results
        signal_to_search_float = signal_to_search.astype(float)
        snippet_float = snippet.astype(float)

        # MemoryAllocation problem described here: https://github.com/scipy/scipy/issues/5986
        return signal.correlate(signal_to_search_float, snippet_float, mode='same') / (sum(signal_to_search) * sum(snippet))
        # return signal.correlate(signal_to_search_float, snippet_float, mode='valid') / (sum(signal_to_search) * sum(snippet))
        # return signal.correlate(signal_to_search_float, snippet_float, mode='full') / (sum(signal_to_search) * sum(snippet))
