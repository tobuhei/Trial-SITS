"""
online_variance.py
"""

class OnlineVariance:
    """
    リアルタイムで標準偏差を計算するクラス

    Methods:
    - update(x): Updates the mean and variance with a new value x.
    - get_variance(): Returns the variance.
    """
    def __init__(self):
        self.num = 0
        self.mean = 0
        self.square = 0

    def update(self, variable):
        """
        Updates the mean and variance with a new value x.

        Parameters:
        pydocstyle . (float): current number
        """
        self.num += 1
        delta = variable - self.mean
        self.mean += delta / self.num
        delta2 = variable - self.mean
        self.square += delta * delta2

    def get_variance(self):
        """
        Returns the variance.

        Returns:
        float: variance
        """
        if self.num < 2:
            return float('nan')
        return self.square / (self.num - 1)
