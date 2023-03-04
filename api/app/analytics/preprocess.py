import numpy as np

from scipy.fft import dct

from .clustering import MeanShiftClustering

from collections import defaultdict
from copy import deepcopy

class Preprocess:

    def __init__(self, vibration_data: defaultdict(lambda: defaultdict(lambda: [])) = None):
        self.vibration_data = vibration_data


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
                sum_of_x_samples = np.sum(m['x'])
                sum_of_y_samples = np.sum(m['y'])
                sum_of_z_samples = np.sum(m['z'])

                # Subtracting the average sum of samples from the collected samples
                if number_of_samples > 1:
                    normalized_matrices[nId][mId]['x'] -= sum_of_x_samples / number_of_samples
                    normalized_matrices[nId][mId]['y'] -= sum_of_y_samples / number_of_samples
                    normalized_matrices[nId][mId]['z'] -= sum_of_z_samples / number_of_samples

        return normalized_matrices

    
    # Root Mean Square feature
    def _rms_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        rms_feature = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]
                l2_norm_of_x_samples = np.linalg.norm(m['x'])
                l2_norm_of_y_samples = np.linalg.norm(m['y'])
                l2_norm_of_z_samples = np.linalg.norm(m['z'])

                rms_feature[nId][mId] = (l2_norm_of_x_samples / np.sqrt(number_of_samples)) ** 2 \
                    + (l2_norm_of_y_samples / np.sqrt(number_of_samples)) ** 2 \
                        + (l2_norm_of_z_samples / np.sqrt(number_of_samples)) ** 2

        return rms_feature


    # Power Spectral Density feature
    def _psd_feature_extraction(self, matrices: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))):
        psd_feature = deepcopy(matrices)

        for nId, measurements in matrices.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                # Creating a number_of_samples * number_of_samples DCT matrix based on each measurement
                dct_matrix = dct(np.eye(number_of_samples), axis=0)

                converted_x_samples = np.sum((m['x'] @ dct_matrix) ** 2) / (2 * number_of_samples)
                converted_y_samples = np.sum((m['y'] @ dct_matrix) ** 2) / (2 * number_of_samples)
                converted_z_samples = np.sum((m['z'] @ dct_matrix) ** 2) / (2 * number_of_samples)

                psd_feature[nId][mId] = converted_x_samples + converted_y_samples + converted_z_samples

        return psd_feature


    # Outlier detection using mean shift clustering
    def _outlier_detection(self, matrices):
        pass

    
    # Using this method to pinpoint outlier sensor data
    def _compute_average_accelaration(self):
        if self.vibration_data == None:
            return
        
        average_accelaration = self._create_matrices()

        for nId, measurements in average_accelaration.items():
            for mId, m in measurements.items():
                number_of_samples = m['x'].shape[0]

                average_of_x_accelaration = np.sum(m['x']) / number_of_samples
                average_of_y_accelaration = np.sum(m['y']) / number_of_samples
                average_of_z_accelaration = np.sum(m['z']) / number_of_samples

                average_accelaration[nId][mId]['x'] = average_of_x_accelaration
                average_accelaration[nId][mId]['y'] = average_of_y_accelaration
                average_accelaration[nId][mId]['z'] = average_of_z_accelaration

        return average_accelaration


    def start(self):
        if self.vibration_data == None:
            return

        # Creating matrices from raw data
        matrices = self._create_matrices()

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        # Extracting RMS (Root Mean Square) feature from normalized data
        rms_feature = self._rms_feature_extraction(matrices=normalized_data)\


        # Extracting PSD (Power Spectral Density) feature from normalized data
        psd_feature = self._psd_feature_extraction(matrices=normalized_data)