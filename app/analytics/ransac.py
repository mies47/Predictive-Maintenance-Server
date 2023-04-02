from sklearn.linear_model import RANSACRegressor


class RANSAC:
    def __init__(self):
        self.ransac = RANSACRegressor()

    def get_inlier_mask(self, X, y):
        if X is None or y is None:
            return
        
        self.ransac.fit(X=X, y=y)

        return self.ransac.inlier_mask_