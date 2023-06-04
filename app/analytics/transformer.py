import numpy as np

from collections import defaultdict


class Transformer:
    def __init__(self, vibration_data: defaultdict(lambda: defaultdict(lambda: [])) = None):
        self.vibration_data = vibration_data

    
    def get_matrices(self):
        '''This function creates matrices from the raw data for preprocessing'''
        if self.vibration_data is None:
            raise ValueError('There is no vibration data!')

        matrices = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

        for nId, measurements in self.vibration_data.items():
            for mId, m in measurements.items():
                for sample in m:
                    matrices[nId][mId]['x'].append(sample['x'])
                    matrices[nId][mId]['y'].append(sample['y'])
                    matrices[nId][mId]['z'].append(sample['z'])
                
                # Converting collected samples to numpy arrays
                matrices[nId][mId]['x'] = np.array(matrices[nId][mId]['x'], dtype=np.float64)
                matrices[nId][mId]['y'] = np.array(matrices[nId][mId]['y'], dtype=np.float64)
                matrices[nId][mId]['z'] = np.array(matrices[nId][mId]['z'], dtype=np.float64)

        return matrices