import numpy as np

from .ransac import RANSAC
from ..utils.constants import SMOOTHING_WINDOW_SIZE

from typing import List, Dict, Tuple
from collections import defaultdict

class RemainingUsefulLifetimeModel:

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

        return (summation + np.sum(list(map(lambda point: point[1], q2)))) / (counter + len(p_2))

    
    def _get_peak_harmonic_distance_from_healthy_zone(self,
                                                     harmonic_peak: Dict[str, float],
                                                     healthy_harmonic_peaks: List[List[Dict[str, float]]]):

        harmonic_distances = [self._harmonic_peak_distance(p_1=harmonic_peak, p_2=healthy_harmonic_peak) for healthy_harmonic_peak in healthy_harmonic_peaks]
                    
        return harmonic_distances
    
    
    def _get_service_time_in_days(self, service_time: float, starting_service_time: float):
        return (service_time - starting_service_time) // (24 * 60 * 60)
    
    
    def get_measurements_distance_from_healthy_zone(self,
                                                    harmonic_peaks: Dict[str, Dict[str, List[Dict[str, float]]]],
                                                    labeled_peaks: Dict):
        
        healthy_harmonic_peaks = []
        for _, labeled_data in labeled_peaks.items():
            if labeled_peaks['zone'] == 'A':
                healthy_harmonic_peaks.append(labeled_data['harmonic_peaks'])
                
        distances = defaultdict(lambda: defaultdict(lambda: []))
        for nId, measurements in harmonic_peaks.items():
            for mId, harmonic_peak in measurements.items():
                distances[nId][mId] = self._get_peak_harmonic_distance_from_healthy_zone(harmonic_peak=harmonic_peak, healthy_harmonic_peaks=healthy_harmonic_peaks)
                
        return distances
    
    
    def get_rul_model(self,
                      starting_service_time: float,
                      all_measurements: List[Dict[str, str | float]],
                      harmonic_peaks: Dict[str, Dict[str, List[Dict[str, float]]]],
                      labeled_peaks: Dict
                      ):
        
        distances = self.get_measurements_distance_from_healthy_zone(harmonic_peaks=harmonic_peaks, labeled_peaks=labeled_peaks)
        
        measurements_distances = dict()
        for _, measurements in distances.items():
            for mId, distance in measurements.items():
                measurements_distances[mId] = distance
        
        measurements_ids = [measurement['measurementId'] for measurement in all_measurements]
        measurements_time = {measurement['measurementId']: self._get_service_time_in_days(service_time=measurement['time'], starting_service_time=starting_service_time) for measurement in all_measurements}
        
        X_train = [measurements_time[measurement_id] for measurement_id in measurements_ids]
        y_train = [measurements_distances[measurement_id] for measurement_id in measurements_ids]
        
        self._ransac.fit(X=X_train, y=y_train)
        
        return self._ransac
        