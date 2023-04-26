import numpy as np

from ..utils.constants import SMOOTHING_WINDOW_SIZE

from typing import List, Tuple
from copy import deepcopy


def find_closest_point_index(peak_features: List[Tuple[float, float]], peak: Tuple[float, float]):
    if not peak_features:
        return None

    freqs = np.array(list(map(lambda point: point[0], peak_features)))
    freq_to_find = peak[0]

    return np.abs(freqs - freq_to_find).argmin()


def harmonic_peak_distance(p_1: List[Tuple[float, float]], p_2: List[Tuple[float, float]]) -> float:
    '''This function estimates the dissimilarity between two harmonic peaks'''

    q1 = deepcopy(p_1)
    q2 = deepcopy(p_2)

    # Normalizing input peaks
    maximum_peak = 0
    maximum_frequency = 0

    for freq, peak in p_1:
        maximum_peak = np.maximum(peak, maximum_peak)
        maximum_frequency = np.maximum(freq, maximum_frequency)

    for freq, peak in p_2:
        maximum_peak = np.maximum(peak, maximum_peak)
        maximum_frequency = np.maximum(freq, maximum_frequency)

    q1 = list(map(lambda point: (point[0] / maximum_frequency, point[1] / maximum_peak), q1))
    q2 = list(map(lambda point: (point[0] / maximum_frequency, point[1] / maximum_peak), q2))

    summation = 0
    counter = 0
    dist = 0

    while q1:
        freq, peak = q1.pop()
        q2_closest_point_index = find_closest_point_index(q2, (freq, peak))
        
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