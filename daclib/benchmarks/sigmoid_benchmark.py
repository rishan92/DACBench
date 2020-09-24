import AbstractBenchmark
from gym import spaces
import numpy as np

ACTION_VALUES = 5

LUBY_DEFAULTS = {
    "action_space": "Discrete",
    "action_space_args": [int(np.prod(ACTION_VALUES))],
    "observation_space": "Box",
    "observation_space_type": np.float32,
    "observation_space_args": [np.array([-np.inf for _ in range(1 + len(ACTION_VALUES) * 3)]), np.array([np.inf for _ in range(1 + len(ACTION_VALUES) * 3)])],
    "reward_range": (0, 1),
    "cutoff" : 10,
    "action_values": ACTION_VALUES,
    "min_steps": 2**3,
    "slope_multiplier": 2.0
}

class SigmoidBenchmark(AbstractBenchmark):
    def __init__(self, config_path):
        super(LubyBenchmark, self).__init__(config_path)
        if not self.config:
            self.config = SIGMOID_DEFAULTS

        for key in LUBY_DEFAULTS:
            if not key in self.config:
                self.config[key] = SIGMOID_DEFAULTS[key]

    def get_benchmark_env(self):
        return LubyEnv(config)
