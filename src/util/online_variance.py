import statistics
import math
import numpy as np

# リアルタイムで標準偏差を計算するクラス
class OnlineVariance:
    def __init__(self):
        self.n = 0
        self.mean = 0
        self.M2 = 0

    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2

    def get_variance(self):
        if self.n < 2:
            return float('nan')
        else:
            return self.M2 / (self.n - 1)