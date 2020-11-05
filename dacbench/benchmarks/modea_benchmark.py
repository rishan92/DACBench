from dacbench.abstract_benchmark import AbstractBenchmark, objdict
from dacbench.envs import ModeaEnv
from gym import spaces
import numpy as np
import os
import csv

MODEA_DEFAULTS = objdict(
    {
        "action_space": spaces.MultiDiscrete([2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3]),
        "observation_space": spaces.Box(
            low=-np.inf * np.ones(5), high=np.inf * np.ones(5)
        ),
        "reward_range": (-(10 ** 12), 0),
        "cutoff": 1e6,
        "seed": 0,
        "instance_set_path": "../instance_sets/cma_train.csv",
    }
)


class ModeaBenchmark(AbstractBenchmark):
    """
    Benchmark with default configuration & relevant functions for Modea
    """

    def __init__(self, config_path=None):
        """
        Initialize Modea Benchmark

        Parameters
        -------
        config_path : str
            Path to config file (optional)
        """
        super(ModeaBenchmark, self).__init__(config_path)
        if not self.config:
            self.config = objdict(MODEA_DEFAULTS.copy())

        for key in MODEA_DEFAULTS:
            if key not in self.config:
                self.config[key] = MODEA_DEFAULTS[key]

    def get_environment(self):
        """
        Return ModeaEnv env with current configuration

        Returns
        -------
        ModeaEnv
            Modea environment
        """
        if "instance_set" not in self.config.keys():
            self.config.instance_set = [1, 0, 0, np.ones(11)]

        return ModeaEnv(self.config)

    def read_instance_set(self):
        """
        Read path of instances from config into list
        """
        path = (
            os.path.dirname(os.path.abspath(__file__))
            + "/"
            + self.config.instance_set_path
        )
        self.config["instance_set"] = {}
        with open(path, "r") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                function = int(row["fcn_id"])
                instance = int(row["inst_id"])
                dimension = int(row["dim"])
                representation = [float(row[f"rep{i}"]) for i in range(14)]
                instance = [
                    dimension,
                    function,
                    instance,
                    representation,
                ]
                self.config["instance_set"][int(row["ID"])] = instance

    # def get_benchmark(self, seed=0):
    #     """
    #     Get benchmark from the LTO paper
    #
    #     Parameters
    #     -------
    #     seed : int
    #         Environment seed
    #
    #     Returns
    #     -------
    #     env : CMAESEnv
    #         CMAES environment
    #     """
    #     self.config = objdict(MODEA_DEFAULTS.copy())
    #     self.config.seed = seed
    #     self.read_instance_set()
    #     return ModEnv(self.config)