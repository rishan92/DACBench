import pytest
import unittest

from sklearn.metrics import mutual_info_score
import numpy as np
from dacbench.benchmarks import LubyBenchmark
from dacbench.wrappers import InstanceSamplingWrapper


class TestInstanceSamplingWrapper(unittest.TestCase):
    def test_init(self):
        bench = LubyBenchmark()
        env = bench.get_environment()

        with pytest.raises(Exception):
            wrapped = InstanceSamplingWrapper(env)

        def sample():
            return [0, 0]

        wrapped = InstanceSamplingWrapper(env, sampling_function=sample)
        self.assertFalse(wrapped.sampling_function is None)

    def test_reset(self):
        bench = LubyBenchmark()
        env = bench.get_environment()

        def sample():
            return [0, 0]

        wrapped = InstanceSamplingWrapper(env, sampling_function=sample)

        self.assertFalse(np.array_equal(wrapped.instance, sample()))
        self.assertFalse(np.array_equal(wrapped.instance_set, [sample()]))
        self.assertTrue(wrapped.inst_id == 0)

        wrapped.reset()
        self.assertTrue(np.array_equal(wrapped.instance, sample()))
        self.assertTrue(np.array_equal(wrapped.instance_set, [sample()]))
        self.assertTrue(wrapped.inst_id == 0)

    def test_fit(self):
        bench = LubyBenchmark()
        bench.config.instance_set_path = "../instance_sets/luby/luby_train.csv"
        bench.read_instance_set()
        instances = bench.config.instance_set
        env = bench.get_environment()

        wrapped = InstanceSamplingWrapper(env, instances=instances)
        samples = []
        for _ in range(100):
            samples.append(wrapped.sampling_function())
        mi1 = mutual_info_score(np.array(instances)[:, 0], np.array(samples)[:, 0])
        mi2 = mutual_info_score(np.array(instances)[:, 1], np.array(samples)[:, 1])

        self.assertTrue(mi1 > 0.99)
        self.assertTrue(mi1 != 1)
        self.assertTrue(mi2 > 0.99)
        self.assertTrue(mi2 != 1)
