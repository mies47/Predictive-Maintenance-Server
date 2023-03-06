import numpy as np

from sklearn.cluster import MeanShift

class MeanShiftClustering:

    def __init__(self, data = None):
        self.data = data
        self.model = MeanShift()


    def fit(self):
        if self.data is None:
            return
        
        self.model.fit(self.data)