"""pca — Principal Component Analysis from scratch.

Centre the data, form its covariance, and extract the top eigenvectors by
**power iteration + deflation**. Those principal components are the directions of
greatest variance, and projecting onto the first few is the optimal linear
compression. This MVP recovers known axes exactly, and shows PCA *discovering the
true dimensionality* of low-rank data (the reconstruction-error elbow).

Pure stdlib, deterministic. Pairs with the lab's `lsh` (vectors) and `gp` (linalg).
"""
from .linalg import covariance, power_iteration, deflate, mean_vector, dot
from .pca import PCA
from .data import correlated_2d, low_rank

__all__ = ["PCA", "covariance", "power_iteration", "deflate", "mean_vector", "dot",
           "correlated_2d", "low_rank"]
