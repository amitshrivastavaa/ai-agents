"""ssm — a selective state-space model (Mamba), from scratch.

State-space models are the leading linear-time alternative to the Transformer.
This MVP builds the scalar SSM core and shows the two facts that matter:

1. **The duality.** A linear time-invariant (LTI) SSM is *both* a recurrence
   (``h_t = a·h_{t-1} + b·x_t``, O(n) to run) and a causal convolution
   (``y = K * x``, parallel to train). They produce identical outputs.
2. **Why selectivity matters.** A fixed-dynamics SSM can't do *selective copy*:
   capture a value on a write and hold it across an arbitrary gap. Mamba makes
   the timestep ``Δ_t`` depend on the input, so the recurrence can choose to
   overwrite (large Δ) or hold (Δ=0) per step — and it solves the task a model
   with any constant ``(a, b)`` provably cannot.

Pure stdlib, single channel, fully deterministic.
"""
from .ssm import ssm_scan, ssm_conv, ssm_kernel
from .selective import discretize, sample_and_hold
from .tasks import make_task, best_lti, mse

__all__ = [
    "ssm_scan", "ssm_conv", "ssm_kernel",
    "discretize", "sample_and_hold",
    "make_task", "best_lti", "mse",
]
