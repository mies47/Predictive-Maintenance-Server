import numpy as np

from collections import defaultdict

from sklearn.cluster import MeanShift

class MeanShiftClustering:

    def __init__(self, vibration_data = None, measurements_average_accelaration = None):
        self.vibration_data = vibration_data
        
        self.measurements_id = None
        self.measurements_averages = None
        
        self.model = MeanShift()
        self._model_fitted = False

        if measurements_average_accelaration is not None:
            self.measurements_id = list(measurements_average_accelaration.keys())
            self.measurements_averages = list(measurements_average_accelaration.values())


    def _fit(self):
        if self.measurements_averages is None:
            raise NotImplementedError
        
        self.model.fit(self.measurements_averages)
        self._model_fitted = True


    def outlier_detection(self) -> defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))):
        if not self._model_fitted:
            try:
                self._fit()
            except NotImplementedError:
                return None

        predicted_labels = np.array(self.model.labels_)
        # Finding the most frequent label for vibration data clustering
        normal_data_label = np.bincount(predicted_labels).argmax()

        valid_measurements = [measurement for i, measurement in enumerate(self.measurements_id) if predicted_labels[i] == normal_data_label]

        filtered_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
        for nId, measurements in self.vibration_data.items():
            for mId, samples in measurements.items():
                if mId in valid_measurements:
                    filtered_data[nId][mId] = samples

        return filtered_data