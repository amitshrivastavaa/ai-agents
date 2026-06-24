import unittest

from labs.kalman.linalg import inv, matmul, eye, transpose, trace
from labs.kalman.filter import KalmanFilter
from labs.kalman.models import constant_velocity
from labs.kalman.run import track, rmse, moving_average


class TestLinalg(unittest.TestCase):
    def test_inverse(self):
        for A in ([[4.0, 3.0], [6.0, 3.0]], [[2.0, 0.0, 0.0], [1.0, 3.0, 0.0], [0.0, 1.0, 4.0]]):
            prod = matmul(A, inv(A))
            n = len(A)
            self.assertLess(max(abs(prod[i][j] - eye(n)[i][j])
                                for i in range(n) for j in range(n)), 1e-9)

    def test_singular_raises(self):
        with self.assertRaises(ValueError):
            inv([[1.0, 2.0], [2.0, 4.0]])


class TestFilter(unittest.TestCase):
    def test_update_shrinks_covariance(self):
        F, H, Q, R = constant_velocity()
        P0 = [[100.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        kf = KalmanFilter(F, H, Q, R, [0, 0, 0, 0], P0)
        kf.predict()
        before = trace(kf.P)
        kf.update([1.0, 1.0])
        self.assertLess(trace(kf.P), before)        # a measurement reduces uncertainty

    def test_gain_in_unit_range(self):
        r = track(steps=40, seed="g")
        self.assertTrue(all(0.0 < g < 1.0 for g in r["gains"]))


class TestTracking(unittest.TestCase):
    def test_beats_measurements_and_movavg(self):
        for kind in ("line", "sine", "turn"):
            errs = [track(steps=80, meas_std=3.0, kind=kind, seed=s) for s in range(6)]
            filt = sum(e["rmse_filt"] for e in errs) / len(errs)
            meas = sum(e["rmse_meas"] for e in errs) / len(errs)
            ma = sum(e["rmse_ma"] for e in errs) / len(errs)
            self.assertLess(filt, 0.7 * meas, kind)     # clearly denoises
            self.assertLess(filt, ma, kind)             # beats naive smoothing

    def test_recovers_unmeasured_velocity(self):
        vels = [track(steps=120, meas_std=3.0, kind="line", q=0.001, seed=s)["vel"][-1]
                for s in range(8)]
        vx = sum(v[0] for v in vels) / len(vels)
        vy = sum(v[1] for v in vels) / len(vels)
        self.assertAlmostEqual(vx, 1.0, delta=0.15)     # true vx
        self.assertAlmostEqual(vy, 0.5, delta=0.15)     # true vy (never measured)

    def test_gain_converges(self):
        g = track(steps=60, kind="line", seed="c")["gains"]
        self.assertLess(abs(g[-1] - g[-2]), 1e-4)       # reached steady state

    def test_moving_average_shape(self):
        ma = moving_average([(0.0, 0.0), (2.0, 4.0)], window=2)
        self.assertEqual(ma[0], (0.0, 0.0))
        self.assertEqual(ma[1], (1.0, 2.0))

    def test_deterministic(self):
        self.assertEqual(track(steps=30, seed="d")["est"],
                         track(steps=30, seed="d")["est"])


if __name__ == "__main__":
    unittest.main()
