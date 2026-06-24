"""kmeans — k-means clustering with k-means++ init and the elbow method.

Lloyd's algorithm alternates assign-to-nearest-centroid and move-centroids-to-mean,
each step monotonically lowering the within-cluster squared distance (**inertia**)
to a local optimum. **k-means++** seeds the centroids spread out (∝ squared
distance), avoiding the bad optima random init falls into. The **elbow** in
inertia-vs-k reveals the natural number of clusters.

Pure stdlib, deterministic. The unsupervised companion to the lab's `pca`.
"""
from .kmeans import KMeans
from .data import blobs
from .metrics import purity, best_of, elbow

__all__ = ["KMeans", "blobs", "purity", "best_of", "elbow"]
