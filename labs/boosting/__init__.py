"""boosting — gradient boosting for regression, from scratch.

The method that dominates tabular ML (XGBoost, LightGBM, CatBoost). Build trees
**sequentially**: each one fits the residuals — where the current ensemble is
still wrong — and is added (shrunk by a learning rate) to the prediction. For
squared loss the residual is the negative gradient of the loss, so every tree is
one step of **gradient descent in function space**. Many shallow stumps, each
correcting the last, compose into a sharp non-linear fit.

Self-contained (its own small `RegTree`). Offline, deterministic. Completes the
lab's tree thread: `tree` → `forest` (bagging) → `boosting`.
"""
from .regtree import RegTree
from .gbm import GradientBoosting, mse

__all__ = ["RegTree", "GradientBoosting", "mse"]
