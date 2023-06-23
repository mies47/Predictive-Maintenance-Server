import numpy as np

from .ransac import RANSAC
from ..utils.constants import SMOOTHING_WINDOW_SIZE

from typing import List, Dict, Tuple


class RUL:

    def __init__(self):
        self._ransac = RANSAC()


    def _find_closest_point_index(self, peak_features: List[Tuple[float, float]], peak: Tuple[float, float]):
        if not peak_features:
            return None

        freqs = np.array(list(map(lambda point: point[0], peak_features)))
        freq_to_find = peak[0]

        return np.abs(freqs - freq_to_find).argmin()


    def _harmonic_peak_distance(self, p_1: List[Dict[str, float]], p_2: List[Dict[str, float]]) -> float:
        '''This function estimates the dissimilarity between two harmonic peak features. The model learning process in based on this function.'''

        q1 = [(harmonic_peak['frequency'], harmonic_peak['peak_value']) for harmonic_peak in p_1]
        q2 = [(harmonic_peak['frequency'], harmonic_peak['peak_value']) for harmonic_peak in p_2]

        # Normalizing input peaks
        maximum_peak = 0
        maximum_frequency = 0

        for freq, peak in q1:
            maximum_peak = np.maximum(peak, maximum_peak)
            maximum_frequency = np.maximum(freq, maximum_frequency)

        for freq, peak in q2:
            maximum_peak = np.maximum(peak, maximum_peak)
            maximum_frequency = np.maximum(freq, maximum_frequency)

        q1 = list(map(lambda point: (point[0] / maximum_frequency, point[1] / maximum_peak), q1))
        q2 = list(map(lambda point: (point[0] / maximum_frequency, point[1] / maximum_peak), q2))

        summation = 0
        counter = 0
        dist = 0

        while q1:
            freq, peak = q1.pop()
            q2_closest_point_index = self._find_closest_point_index(q2, (freq, peak))
            
            if q2_closest_point_index is None:
                continue

            closest_point_freq, closest_point_peak = q2[q2_closest_point_index]

            if np.abs(freq - closest_point_freq) * maximum_frequency < SMOOTHING_WINDOW_SIZE:
                dist += np.linalg.norm(np.array([freq, peak]) - np.array([closest_point_freq, closest_point_peak]))
                q2.pop(q2_closest_point_index)
            else:
                dist = np.linalg.norm(np.array([freq, peak]))

            summation += dist
            counter += 1

        return (summation + np.sum(list(map(lambda point: point[1], q2)))) / (counter + len(q2))


    def fit_model(self, measurements, harmonic_peaks, labeled_harmonic_peaks):
        X = np.arange(start=0, stop=len(measurements), step=1)
        y = np.array([self._harmonic_peak_distance(harmonic_peaks[measurement], labeled_harmonic_peaks) for measurement in measurements], dtype=np.float64)
        
        return self._ransac.fit(X=X, y=y)