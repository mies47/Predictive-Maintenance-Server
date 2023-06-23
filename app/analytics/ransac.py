from sklearn.linear_model import RANSACRegressor


class RANSAC:
    def __init__(self):
        self.ransac = RANSACRegressor()


    def fit(self, X, y):
        if X is None or y is None:
            return False
        
        self.ransac.fit(X=X, y=y)

        return True
    

    def predict_model(self, train_X, train_y, line_X):
        if train_X is None or train_y is None:
            return
        
        self.ransac.fit(X=train_X, y=train_y)
        
        return self.ransac.predict(X=line_X)