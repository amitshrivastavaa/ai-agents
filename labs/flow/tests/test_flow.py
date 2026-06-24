import math
import unittest

from labs.flow import targets
from labs.flow.field import base_sample, denoiser, velocity, weights
from labs.flow.sample import (integrate, generate, nearest_data_rmse,
                              mode_coverage, straightness)


class TestField(unittest.TestCase):
    def test_base_is_standard_normal(self):
        pts = base_sample(4000, 2, seed="n")
        mean = [sum(p[d] for p in pts) / len(pts) for d in range(2)]
        self.assertLess(abs(mean[0]), 0.1)
        self.assertLess(abs(mean[1]), 0.1)

    def test_weights_form_a_distribution(self):
        data = targets.get("clusters")
        w = weights([1.0, 1.0], 0.5, data)
        self.assertAlmostEqual(sum(w), 1.0)
        self.assertTrue(all(x >= 0 for x in w))

    def test_denoiser_approaches_nearest_point_near_t1(self):
        data = targets.get("clusters")          # corners (±4, ±4)
        yhat = denoiser([3.5, 3.6], 0.99, data)
        self.assertLess(math.dist(yhat, [4.0, 4.0]), 0.3)

    def test_velocity_at_t0_points_to_centroid(self):
        # At t=0 all posterior weights are equal, so ŷ is the data centroid and
        # v = centroid − x (no mode is selected yet). Ring centroid = origin.
        data = targets.get("ring")
        yhat = denoiser([2.0, 1.0], 0.0, data)
        self.assertAlmostEqual(yhat[0], 0.0, places=6)
        self.assertAlmostEqual(yhat[1], 0.0, places=6)
        v = velocity([2.0, 1.0], 0.0, data)
        self.assertAlmostEqual(v[0], -2.0, places=6)
        self.assertAlmostEqual(v[1], -1.0, places=6)


class TestGeneration(unittest.TestCase):
    def test_lands_on_every_target(self):
        for name in targets.NAMES:
            data = targets.get(name)
            gen = generate(data, 200, steps=16, seed="g")
            self.assertLess(nearest_data_rmse(gen, data), 0.05, name)
            # near-total coverage — no mode collapse (spiral's dense centre can
            # leave a point or two without a nearest sample out of 200).
            self.assertGreaterEqual(mode_coverage(gen, data), 0.9, name)

    def test_more_steps_reduce_error(self):
        data = targets.get("spiral")
        coarse = nearest_data_rmse(generate(data, 160, steps=4, seed="s"), data)
        fine = nearest_data_rmse(generate(data, 160, steps=32, seed="s"), data)
        self.assertGreater(coarse, fine)
        self.assertLess(fine, 0.05)

    def test_ring_samples_have_target_radius(self):
        data = targets.get("ring")              # radius 4
        for x, y in generate(data, 150, steps=24, seed="r"):
            self.assertAlmostEqual(math.hypot(x, y), 4.0, delta=0.1)

    def test_trajectories_are_nearly_straight(self):
        data = targets.get("ring")
        strs = [straightness(integrate(x0, data, 32, "euler")[1])
                for x0 in base_sample(40, 2, seed="t")]
        self.assertLess(sum(strs) / len(strs), 1.3)

    def test_midpoint_method_also_converges(self):
        data = targets.get("moons")
        gen = generate(data, 150, steps=16, method="midpoint", seed="m")
        self.assertLess(nearest_data_rmse(gen, data), 0.1)

    def test_deterministic(self):
        data = targets.get("grid")
        a = generate(data, 80, steps=16, seed="d")
        b = generate(data, 80, steps=16, seed="d")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
