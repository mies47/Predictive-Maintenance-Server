import numpy as np

from scipy.fft import dct

from .clustering import MeanShiftClustering

from collections import defaultdict
from copy import deepcopy

from ..utils.env_vars import HANN_WINDOW_SIZE, MAXIMUM_NUMBER_OF_PEAKS

class Preprocess:

    def __init__(self,
                 vibration_data: defaultdict(lambda: defaultdict(lambda: []),) = None,
                 nodes_ids = None,
                 measurements_ids = None):

        self.vibration_data = vibration_data
        self.nodes_ids = nodes_ids
        self.measurements_ids = measurements_ids
        

    def _create_matrices(self):
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

    
    # Root Mean Square feature
    def _rms_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        rms_feature = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():

                rms_feature[nId][mId]['x'] = np.sqrt(np.mean(np.absolute(m['x']) ** 2))
                rms_feature[nId][mId]['y'] = np.sqrt(np.mean(np.absolute(m['y']) ** 2))
                rms_feature[nId][mId]['z'] = np.sqrt(np.mean(np.absolute(m['z']) ** 2))

        return rms_feature


    # Power Spectral Density feature
    def _psd_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        psd_feature = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                psd_feature[nId][mId]['x'] = (dct(m['x'], type=2, norm='ortho') ** 2) / number_of_samples
                psd_feature[nId][mId]['y'] = (dct(m['y'], type=2, norm='ortho') ** 2) / number_of_samples
                psd_feature[nId][mId]['z'] = (dct(m['z'], type=2, norm='ortho') ** 2) / number_of_samples

        return psd_feature

    
    # Using this method to pinpoint outlier sensor data
    def _compute_measurements_average_accelaration(self, vibration_measurements: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
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
    

    # Returns filtered data after outlier detection process
    def _outlier_detection(self, vibration_data: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
       
        # Computing measurements average accelaration for outlier detection
        measurement_average_accelaration = self._compute_measurements_average_accelaration(vibration_measurements=vibration_data)
        
        ms = MeanShiftClustering(vibration_data=vibration_data, measurements_average_accelaration=measurement_average_accelaration)

        return ms.outlier_detection()
    

    def _hann_window(self, n):
        return 0.5 * (1 - np.cos((2 * np.pi * n) / (HANN_WINDOW_SIZE - 1)))


    def _harmonic_peak_feature_extraction(self):
        pass


    def start(self):
        if self.vibration_data == None:
            return

        # Creating matrices from raw data
        matrices = self._create_matrices()

        # TODO: Set a threshold for doing outliter detection process
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
        harmonic_peak_feature = self._harmonic_peak_feature_extraction()