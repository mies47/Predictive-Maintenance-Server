from sklearn.linear_model import RANSACRegressor


class RANSAC:
    def __init__(self):
        self.model = RANSACRegressor()

    def train(self, train_data = None, train_data_prediction = None):
        if train_data is None:
            return
        
        self.model.fit(train_data, train_data_prediction)