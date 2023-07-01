from sklearn.linear_model import RANSACRegressor


class RANSAC:
    def __init__(self):
        self.ransac = RANSACRegressor()
        self.fitted = False


    def fit(self, X, y):
        if X is None or y is None:
            return False
        
        self.ransac.fit(X=X, y=y)
        self.fitted = True

        return True
    

    def predict(self, line_X = None):
        if not self.fitted:
            return None
        
        return self.ransac.predict(X=line_X)