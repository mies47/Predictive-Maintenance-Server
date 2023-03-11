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

                psd_feature[nId][mId]['x'] = dct(m['y'], type=2, norm='ortho') ** 2
                psd_feature[nId][mId]['y'] = dct(m['y'], type=2, norm='ortho') ** 2
                psd_feature[nId][mId]['z'] = dct(m['z'], type=2, norm='ortho') ** 2

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

                average_accelaration[nId][mId]['x'] = np.mean(m['x'])
                average_accelaration[nId][mId]['y'] = np.mean(m['y'])
                average_accelaration[nId][mId]['z'] = np.mean(m['z'])

        return average_accelaration


    def start(self):
        if self.vibration_data == None:
            return

        # Creating matrices from raw data
        matrices = self._create_matrices()

        # Normalizing samples to remove gravity effect
        normalized_data = self._normalize_vibration_data(matrices=matrices)

        # Extracting RMS (Root Mean Square) feature from normalized data
        rms_feature = self._rms_feature_extraction(matrices=normalized_data)

        # Extracting PSD (Power Spectral Density) feature from normalized data
        psd_feature = self._psd_feature_extraction(matrices=normalized_data)

        # for nId, measurements in rms_feature.items():
        #     for mId, m in measurements.items():

        #         print(rms_feature[nId][mId]['x'] ** 2, np.sum(psd_feature[nId][mId]['x']), psd_feature[nId][mId]['x'])