"""Principal Component Analysis — find the directions of greatest variance.

Centre the data, form its covariance, and pull out the top eigenvectors one by
one (power iteration + deflation). Those **principal components** are the axes
along which the data varies most; projecting onto the first few is the optimal
linear compression (it minimizes reconstruction error for that many dimensions).
"""
from __future__ import annotations

from .linalg import (mean_vector, covariance, power_iteration, deflate, trace, dot)


class PCA:
    def __init__(self, n_components=2):
        self.n_components = n_components
        self.mean = None
        self.components = []          # list of unit eigenvectors
        self.explained_variance = []  # eigenvalues
        self.total_variance = 0.0

    def fit(self, X):
        self.mean = mean_vector(X)
        C = covariance(X, self.mean)
        self.total_variance = trace(C)
        self.components, self.explained_variance = [], []
        for k in range(min(self.n_components, len(self.mean))):
            v, lam = power_iteration(C, seed=("comp", k))
            self.components.append(v)
            self.explained_variance.append(max(lam, 0.0))
            C = deflate(C, v, lam)
        return self

    @property
    def explained_variance_ratio(self):
        if self.total_variance <= 0:
            return [0.0] * len(self.explained_variance)
        return [e / self.total_variance for e in self.explained_variance]

    def transform(self, X):
        return [[dot([xi - mi for xi, mi in zip(x, self.mean)], comp)
                 for comp in self.components] for x in X]

    def inverse_transform(self, Z):
        out = []
        for z in Z:
            rec = list(self.mean)
            for zk, comp in zip(z, self.components):
                for i in range(len(rec)):
                    rec[i] += zk * comp[i]
            out.append(rec)
        return out

    def reconstruct(self, X):
        return self.inverse_transform(self.transform(X))
