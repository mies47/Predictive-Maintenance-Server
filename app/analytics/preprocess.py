import numpy as np

from scipy.fft import dct, fftfreq
from scipy.signal import find_peaks, peak_prominences

from .clustering import MeanShiftClustering

from collections import defaultdict
from copy import deepcopy

from ..utils.constants import SMOOTHING_WINDOW_SIZE, SAMPLING_RATE

class Preprocess:

    def __init__(self,
                 vibration_data: defaultdict(lambda: defaultdict(lambda: [])) = None,
                 nodes_ids = None,
                 measurements_ids = None):

        self.vibration_data = vibration_data
        self.nodes_ids = nodes_ids
        self.measurements_ids = measurements_ids
        

    def _create_matrices(self):
        '''This function creates matrices from the raw data for preprocessing'''

        matrices = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

        for nId, measurements in self.vibration_data.items():
            for mId, m in measurements.items():
                for sample in m:
                    matrices[nId][mId]['x'].append(sample['x'])
                    matrices[nId][mId]['y'].append(sample['y'])
                    matrices[nId][mId]['z'].append(sample['z'])
                
                # Converting collected smaples to numpy arrays
                matrices[nId][mId]['x'] = np.array(matrices[nId][mId]['x'], dtype=np.float32)
                matrices[nId][mId]['y'] = np.array(matrices[nId][mId]['y'], dtype=np.float32)
                matrices[nId][mId]['z'] = np.array(matrices[nId][mId]['z'], dtype=np.float32)

        return matrices


    def _normalize_vibration_data(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        '''Normalized the input data to remove gravity effect'''

        normalized_matrices = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                # Subtracting the average sum of samples from the collected samples
                if number_of_samples > 1:
                    normalized_matrices[nId][mId]['x'] -= np.mean(m['x'])
                    normalized_matrices[nId][mId]['y'] -= np.mean(m['y'])
                    normalized_matrices[nId][mId]['z'] -= np.mean(m['z'])

        return normalized_matrices

    
    def _rms_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        '''Root Mean Square feature'''

        rms_feature = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():

                rms_feature[nId][mId]['x'] = np.sqrt(np.mean(np.absolute(m['x']) ** 2))
                rms_feature[nId][mId]['y'] = np.sqrt(np.mean(np.absolute(m['y']) ** 2))
                rms_feature[nId][mId]['z'] = np.sqrt(np.mean(np.absolute(m['z']) ** 2))

        return rms_feature


    def _psd_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        '''Power Spectral Density feature'''

        # Each tuple consists of (frequency, psd)
        psd_feature = defaultdict(lambda: defaultdict(lambda: tuple()))

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                x_psd_feature = (dct(m['x'], type=2, norm='ortho') ** 2) / number_of_samples
                y_psd_feature = (dct(m['y'], type=2, norm='ortho') ** 2) / number_of_samples
                z_psd_feature = (dct(m['z'], type=2, norm='ortho') ** 2) / number_of_samples

                psd_feature[nId][mId] = x_psd_feature + y_psd_feature + z_psd_feature

        return psd_feature


    def _compute_measurements_average_accelaration(self, vibration_measurements: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
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
    

    def _outlier_detection(self, vibration_data: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
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
    

    def _find_peaks(self, x):
        freqs = fftfreq(x.shape[0], d = 1/SAMPLING_RATE)
        
        return x, freqs


    def _harmonic_peak_feature_extraction(self, psd: defaultdict(lambda: defaultdict())):
        '''Extracting harmonic peak feature from PSD feature after smoothing using hann window'''

        harmonic_peaks = deepcopy(psd)

        for nId, measurements in harmonic_peaks.items():
            for mId, psd_feature in measurements.items():
                smoothed_feature = self._smooth(x=psd_feature, method='hanning')

                peaks, freqs = self._find_peaks(smoothed_feature)

                harmonic_peaks[nId][mId] = (freqs, peaks)

        return harmonic_peaks


    def start(self):

        if self.vibration_data == None:
            return

        # Creating matrices from raw data
        matrices = self._create_matrices()

        # TODO: Set a threshold for including outlier detection process
        if False:
            print(matrices, '\n\n')
            matrices = self._outlier_detection(vibration_data=matrices)
            print(matrices)

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        # Extracting RMS (Root Mean Square) feature from normalized data
        rms_feature = self._rms_feature_extraction(matrices=normalized_data)

        # Extracting PSD (Power Spectral Density) feature from normalized data
        psd_feature = self._psd_feature_extraction(matrices=normalized_data)

        # Extracting harmonic peak feature
        harmonic_peak_feature = self._harmonic_peak_feature_extraction(psd=psd_feature)