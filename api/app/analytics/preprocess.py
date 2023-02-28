import numpy as np

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


    def start(self):
        if self.vibration_data == None:
            return

        # Creating matrices from raw data
        matrices = self._create_matrices()

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        # Extracting RMS (Root Mean Square) feature from normalized data
        rms_feature = self._rms_feature_extraction(matrices=normalized_data)