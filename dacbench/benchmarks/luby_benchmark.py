from dacbench.abstract_benchmark import AbstractBenchmark, objdict
from dacbench.envs import LubyEnv, luby_gen
from dacbench.wrappers import RewardNoiseWrapper

import numpy as np
import os
import csv

MAX_STEPS = 2 ** 6
LUBY_SEQUENCE = np.log2([next(luby_gen(i)) for i in range(1, 2 * MAX_STEPS + 2)])
HISTORY_LENGTH = 5

LUBY_DEFAULTS = objdict(
    {
        "action_space_class": "Discrete",
        "action_space_args": [int(np.log2(MAX_STEPS))],
        "observation_space_class": "Box",
        "observation_space_type": np.float32,
        "observation_space_args": [
            np.array([-1 for _ in range(HISTORY_LENGTH + 1)]),
            np.array([2 ** max(LUBY_SEQUENCE + 1) for _ in range(HISTORY_LENGTH + 1)]),
        ],
        "reward_range": (-1, 0),
        "cutoff": MAX_STEPS,
        "hist_length": HISTORY_LENGTH,
        "min_steps": 2 ** 3,
        "seed": 0,
        "instance_set_path": "../instance_sets/luby/luby_default.csv",
    }
)


class LubyBenchmark(AbstractBenchmark):
    """
    Benchmark with default configuration & relevant functions for Sigmoid
    """

    def __init__(self, config_path=None):
        """
        Initialize Luby Benchmark

        Parameters
        -------
        config_path : str
            Path to config file (optional)
        """
        super(LubyBenchmark, self).__init__(config_path)
        if not self.config:
            self.config = objdict(LUBY_DEFAULTS.copy())

        for key in LUBY_DEFAULTS:
            if key not in self.config:
                self.config[key] = LUBY_DEFAULTS[key]

    def get_environment(self):
        """
        Return Luby env with current configuration

        Returns
        -------
        LubyEnv
            Luby environment
        """
        if "instance_set" not in self.config.keys():
            self.read_instance_set()

        return LubyEnv(self.config)

    def set_cutoff(self, steps):
        """
        Set cutoff and adapt dependencies

        Parameters
        -------
        int
            Maximum number of steps
        """
        self.config.cutoff = steps
        self.config.action_space_args = [int(np.log2(steps))]
        LUBY_SEQUENCE = np.log2([next(luby_gen(i)) for i in range(1, 2 * steps + 2)])
        self.config.observation_space_args = [
            np.array([-1 for _ in range(self.config.hist_length + 1)]),
            np.array(
                [
                    2 ** max(LUBY_SEQUENCE + 1)
                    for _ in range(self.config.hist_length + 1)
                ]
            ),
        ]

    def set_history_length(self, length):
        """
        Set history length and adapt dependencies

        Parameters
        -------
        int
            History length
        """
        self.config.hist_length = length
        self.config.observation_space_args = [
            np.array([-1 for _ in range(length + 1)]),
            np.array([2 ** max(LUBY_SEQUENCE + 1) for _ in range(length + 1)]),
        ]

    def read_instance_set(self):
        """Read instance set from file"""
        path = (
            os.path.dirname(os.path.abspath(__file__))
            + "/"
            + self.config.instance_set_path
        )
        self.config["instance_set"] = {}
        with open(path, "r") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                self.config["instance_set"][int(row["ID"])] = [
                    float(shift) for shift in row["start"].split(",")
                ] + [float(slope) for slope in row["sticky"].split(",")]
        self.config["instance_set"] = list(self.config["instance_set"].values())

    def get_benchmark(self, L=8, fuzziness=1.5, seed=0):
        """
        Get Benchmark from DAC paper

        Parameters
        -------
        L : int
            Minimum sequence lenght, was 8, 16 or 32 in the paper
        fuzziness : float
            Amount of noise applied. Was 1.5 for most of the experiments
        seed : int
            Environment seed

        Returns
        -------
        env : LubyEnv
            Luby environment
        """
        self.config = objdict(LUBY_DEFAULTS.copy())
        self.config.min_steps = L
        self.config.seed = seed
        self.config.instance_set = [[0, 0]]
        self.config.reward_range = (-10, 10)
        env = LubyEnv(self.config)
        rng = np.random.RandomState(self.config.seed)

        def fuzz():
            return rng.normal(-1, fuzziness)

        fuzzy_env = RewardNoiseWrapper(env, noise_function=fuzz)
        return fuzzy_env
