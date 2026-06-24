"""moe — a mixture of experts: route each input to the model best suited to it.

A gating function sends every input to one of several **expert** models; the
experts *specialize* on different regimes of the data, and together they fit a
piecewise problem that no single model can. Training is competitive EM: each
point goes to whichever expert predicts it best, then every expert refits on the
points it won — so specialization emerges, and a load-balancing nudge keeps any
expert from starving.

The original Mixture-of-Experts idea (Jacobs et al., 1991), which is exactly the
sparse top-k routing inside today's MoE LLMs (Mixtral & friends). Fully offline,
deterministic.
"""
from .experts import LinearExpert
from .moe import MixtureOfExperts, single_model_error
from .data import DATASETS, get_dataset

__all__ = ["LinearExpert", "MixtureOfExperts", "single_model_error",
           "DATASETS", "get_dataset"]
