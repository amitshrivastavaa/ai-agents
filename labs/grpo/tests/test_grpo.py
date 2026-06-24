import math
import unittest

from labs.grpo.task import VerifiableTask
from labs.grpo.policy import SoftmaxPolicy, softmax
from labs.grpo.train import (train, group_advantages, mean_correct_prob,
                             accuracy, steps_to_threshold)


class TestPieces(unittest.TestCase):
    def test_softmax_is_a_distribution(self):
        p = softmax([1.0, 2.0, 3.0])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertTrue(all(x > 0 for x in p))
        self.assertEqual(max(range(3), key=lambda i: p[i]), 2)

    def test_fresh_policy_is_uniform(self):
        pol = SoftmaxPolicy(3, 4)
        self.assertTrue(all(abs(x - 0.25) < 1e-9 for x in pol.probs(0)))

    def test_group_advantages_centered_and_normalized(self):
        adv = group_advantages([1.0, 0.0, 0.0, 1.0], normalize=True)
        self.assertAlmostEqual(sum(adv), 0.0, places=9)          # mean removed
        std = math.sqrt(sum(a * a for a in adv) / len(adv))
        self.assertAlmostEqual(std, 1.0, places=6)               # unit variance

    def test_group_advantages_zero_when_all_equal(self):
        self.assertEqual(group_advantages([1.0, 1.0, 1.0]), [0.0, 0.0, 0.0])

    def test_task_reward_is_verifiable(self):
        task = VerifiableTask(4, 4, seed="x")
        for s in range(4):
            self.assertEqual(task.reward(s, task.answers[s]), 1.0)
            wrong = (task.answers[s] + 1) % 4
            self.assertEqual(task.reward(s, wrong), 0.0)


class TestTraining(unittest.TestCase):
    def test_grpo_solves_the_task(self):
        for seed in range(5):
            task = VerifiableTask(4, 4, seed=("t", seed))
            pol, hist = train(task, steps=300, group_size=12, lr=0.5,
                              method="grpo", seed=seed)
            self.assertEqual(accuracy(pol, task), 1.0)
            self.assertGreater(hist[-1], 0.9)
            self.assertGreater(hist[-1], task.chance() + 0.5)

    def test_grpo_beats_reinforce_convergence(self):
        """The crux: the group baseline converges faster than no baseline."""
        def avg_steps(method):
            xs = []
            for seed in range(6):
                task = VerifiableTask(5, 5, seed=("c", seed))
                _, h = train(task, steps=400, group_size=16, lr=0.5,
                             method=method, seed=seed)
                xs.append(steps_to_threshold(h, 0.95))
            return sum(xs) / len(xs)
        grpo_steps = avg_steps("grpo")
        reinforce_steps = avg_steps("reinforce")
        self.assertLess(grpo_steps, reinforce_steps)
        self.assertLess(grpo_steps, 0.75 * reinforce_steps)      # clear margin

    def test_learning_curve_is_monotone_ish(self):
        task = VerifiableTask(4, 4, seed="m")
        _, hist = train(task, steps=200, group_size=16, lr=0.5, method="grpo", seed=1)
        self.assertGreater(hist[-1], hist[0])
        self.assertGreater(hist[-1], 0.9)

    def test_deterministic(self):
        task = VerifiableTask(4, 4, seed="d")
        a = train(task, steps=120, method="grpo", seed=7)[1]
        b = train(task, steps=120, method="grpo", seed=7)[1]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
