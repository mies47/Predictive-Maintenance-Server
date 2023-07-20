import numpy as np

from scipy.fft import dct, fftfreq
from scipy.signal import find_peaks

from .clustering import MeanShiftClustering

from collections import defaultdict
from copy import deepcopy
from typing import List, Dict

from ..utils.constants import SMOOTHING_WINDOW_SIZE, SAMPLING_RATE, MAXIMUM_NUMBER_OF_PEAKS

class Preprocesser:

    def __init__(self,
                 matrices: Dict[str, Dict[str, Dict[str, List]]] = None,
                 nodes_ids = None,
                 measurements_ids = None):

        self.matrices = matrices
        self.nodes_ids = nodes_ids
        self.measurements_ids = measurements_ids

        # TODO: Set a threshold for including outlier detection process
        if False:
            self.matrices = self._outlier_detection(vibration_data=matrices)

        # Normalizing samples to remove gravity effect
        self.normalized_data = self._normalize_vibration_data()


    def _normalize_vibration_data(self):
        '''Normalized the input data to remove gravity effect'''

        if self.matrices is None:
            raise ValueError('Matrices are not created!')

        normalized_matrices = deepcopy(self.matrices)

        for nId, measurements in normalized_matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                # Subtracting the average sum of samples from the collected samples
                if number_of_samples > 1:
                    normalized_matrices[nId][mId]['x'] -= np.mean(m['x'])
                    normalized_matrices[nId][mId]['y'] -= np.mean(m['y'])
                    normalized_matrices[nId][mId]['z'] -= np.mean(m['z'])

        return normalized_matrices

    
    def rms_feature_extraction(self):
        '''Root Mean Square feature'''

        rms_feature = deepcopy(self.normalized_data)

        for nId, measurements in rms_feature.items():
            for mId, m in measurements.items():

                rms_feature[nId][mId]['x'] = np.sqrt(np.mean(np.absolute(m['x']) ** 2))
                rms_feature[nId][mId]['y'] = np.sqrt(np.mean(np.absolute(m['y']) ** 2))
                rms_feature[nId][mId]['z'] = np.sqrt(np.mean(np.absolute(m['z']) ** 2))

        return rms_feature


    def psd_feature_extraction(self):
        '''Power Spectral Density feature'''

        psd_feature = defaultdict(lambda: defaultdict(lambda: []))

        for nId, measurements in self.normalized_data.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                x_psd_feature = (dct(m['x'], type=2, norm='ortho') ** 2) / number_of_samples
                y_psd_feature = (dct(m['y'], type=2, norm='ortho') ** 2) / number_of_samples
                z_psd_feature = (dct(m['z'], type=2, norm='ortho') ** 2) / number_of_samples
                
                psd_values = x_psd_feature + y_psd_feature + z_psd_feature
                freqs = fftfreq(m['x'].shape[0], d=1/SAMPLING_RATE)
                
                for _, (freq, psd_value) in enumerate(zip(freqs, psd_values)):
                    psd_feature[nId][mId].append({
                        'psd_value': psd_value,
                        'frequency': freq
                    })

        return psd_feature


    def _compute_measurements_average_accelaration(self, vibration_measurements: Dict[str, Dict[str, Dict[str, List]]]):
        '''Using this method to pinpoint outlier sensor data'''
        
        # Creating a 3-cells vector for each measurement indicating x, y, z means for each measurement
        average_accelaration_points = defaultdict(lambda: [0.0, 0.0, 0.0])
        measurements_samples = defaultdict(lambda: 0)

        for _, measurements in vibration_measurements.items():
            for mId, m in measurements.items():
                measurements_samples[mId] += m['x'].shape[0]

                average_accelaration_points[mId][0] += np.sum(m['x'])
                average_accelaration_points[mId][1] += np.sum(m['y'])
                average_accelaration_points[mId][2] += np.sum(m['z'])
        
        for mId in average_accelaration_points.keys():
            average_accelaration_points[mId][0] /= measurements_samples[mId]
            average_accelaration_points[mId][1] /= measurements_samples[mId]
            average_accelaration_points[mId][2] /= measurements_samples[mId]

        return average_accelaration_points
    

    def _outlier_detection(self, vibration_data: Dict[str, Dict[str, Dict[str, List]]]):
        '''Returns filtered data after outlier detection process'''

        # Computing measurements average accelaration for outlier detection
        measurement_average_accelaration = self._compute_measurements_average_accelaration(vibration_measurements=vibration_data)
        
        ms = MeanShiftClustering(vibration_data=vibration_data, measurements_average_accelaration=measurement_average_accelaration)

        return ms.outlier_detection()
    

    def _check_parseval_theorem(self, psd, rms):
        '''A simple function to check the correctness of feature extraction'''

        for nId, measurements in psd.items():
            for mId, measurement in measurements.items():
                print(
                    rms[nId][mId]['x'] ** 2 + rms[nId][mId]['y'] ** 2 + rms[nId][mId]['z'] ** 2,
                    np.sum(psd[nId][mId][1])
                )


    def _smooth(self, x, method='hanning'):
        if x is None:
            raise ValueError('No Input Matrix!')

        if method not in ('hanning'):
            raise NotImplementedError('The requested smoothing window is not implemented')

        smoothing_window = eval(f'np.{method}({SMOOTHING_WINDOW_SIZE})')

        smoothed = np.convolve(smoothing_window, x, mode = 'valid')
    
        return smoothed
    

    def _find_peaks(self, x, freqs):
        '''Returning the most dominant peaks and corresponding frequencies of a specific signal'''

        peaks_index, _ = find_peaks(x)

        harmonic_peak_feature = [(freqs[i], x[i]) for i in peaks_index]
        harmonic_peak_feature = sorted(harmonic_peak_feature, key=lambda t: t[1], reverse=True)
        harmonic_peak_feature = harmonic_peak_feature[:MAXIMUM_NUMBER_OF_PEAKS]
        
        result = [{'peak_value': peak_value, 'frequency': freq} for (freq, peak_value) in harmonic_peak_feature]

        return result


    def harmonic_peak_feature_extraction(self):
        '''Extracting harmonic peak feature from PSD feature after smoothing using hann window'''

        harmonic_peaks = self.psd_feature_extraction()

        for nId, measurements in harmonic_peaks.items():
            for mId, psd_features in measurements.items():
                frequencies, psd_values = [], []
                
                for psd_feature in psd_features:
                    psd_values.append(psd_feature['psd_value'])
                    frequencies.append(psd_feature['frequency'])

                # smoothed_feature = self._smooth(x=psd_values, method='hanning')

                harmonic_peaks[nId][mId] = self._find_peaks(x=psd_values, freqs=frequencies)

        return harmonic_peaks