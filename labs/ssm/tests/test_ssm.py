import math
import unittest

from labs.ssm.ssm import ssm_scan, ssm_conv, ssm_kernel
from labs.ssm.selective import discretize, sample_and_hold
from labs.ssm.tasks import make_task, best_lti, mse


class TestCore(unittest.TestCase):
    def test_duality_scan_equals_conv(self):
        """An LTI SSM's recurrence equals its convolution, to machine precision."""
        x = [1.0, -0.5, 2.0, 0.3, -1.0, 0.7, 0.0, 1.5, -2.0, 0.9]
        for (a, b, c, d) in [(0.8, 0.5, 1.2, 0.1), (0.5, 1.0, 1.0, 0.0),
                             (-0.6, 0.4, 2.0, -0.3), (0.95, 0.05, 1.0, 0.0)]:
            ys, _ = ssm_scan(x, a, b, c, d=d)
            yc = ssm_conv(x, a, b, c, d=d)
            self.assertLess(max(abs(p - q) for p, q in zip(ys, yc)), 1e-12)

    def test_impulse_response_is_kernel(self):
        impulse = [1.0] + [0.0] * 9
        y, _ = ssm_scan(impulse, 0.9, 0.1, 1.0)
        k = ssm_kernel(0.9, 0.1, 1.0, 10)
        self.assertLess(max(abs(p - q) for p, q in zip(y, k)), 1e-12)

    def test_kernel_formula(self):
        k = ssm_kernel(0.5, 2.0, 3.0, 4)
        self.assertEqual(k, [3.0 * 2.0 * 0.5 ** i for i in range(4)])

    def test_ema_smooths_a_step(self):
        # A stable EMA (a=0.9, b=0.1) turns a step input into a monotone rise to 1.
        step = [1.0] * 12
        y, _ = ssm_scan(step, 0.9, 0.1, 1.0)
        self.assertTrue(all(y[i] < y[i + 1] for i in range(len(y) - 1)))
        self.assertLess(y[0], 0.2)
        self.assertGreater(y[-1], 0.6)
        self.assertLess(y[-1], 1.0)

    def test_per_step_params_validate_length(self):
        with self.assertRaises(ValueError):
            ssm_scan([1.0, 2.0, 3.0], [0.5, 0.5], 1.0)


class TestSelective(unittest.TestCase):
    def test_discretize_regimes(self):
        # Large Δ → overwrite (a→0, b→1); Δ=0 → hold (a=1, b=0).
        a, b = discretize([20.0, 0.0], A=-1.0, B=1.0)
        self.assertAlmostEqual(a[0], 0.0, places=6)
        self.assertAlmostEqual(b[0], 1.0, places=6)
        self.assertAlmostEqual(a[1], 1.0, places=12)
        self.assertAlmostEqual(b[1], 0.0, places=12)

    def test_sample_and_hold_is_near_exact(self):
        values, gates, target = make_task(seed="mamba")
        y = sample_and_hold(values, gates, delta_write=12.0)
        self.assertLess(mse(y, target), 1e-6)

    def test_selectivity_beats_best_lti(self):
        """The crux: a selective SSM crushes the *best possible* fixed-dynamics SSM."""
        for seed in ("ssm", "mamba", "s4", "copy"):
            values, gates, target = make_task(seed=seed)
            sel = sample_and_hold(values, gates, delta_write=12.0)
            lti_mse, _, _, _ = best_lti(values, gates, target)
            self.assertGreater(lti_mse, 50 * mse(sel, target),
                               f"selectivity should dominate LTI for seed={seed}")
            self.assertGreater(lti_mse, 0.01)  # LTI genuinely fails the task

    def test_target_is_sample_and_hold(self):
        values, gates, target = make_task(n=10, writes=(0, 5), seed="t")
        self.assertEqual(target[0], values[0])
        self.assertEqual(target[4], values[0])   # held until next write
        self.assertEqual(target[5], values[5])
        self.assertEqual(target[9], values[5])

    def test_deterministic(self):
        a = make_task(seed="z")
        b = make_task(seed="z")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
