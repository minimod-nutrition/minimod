from minimod.solvers.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):
    def __init__(self, minimum_benefit=15958220, **kwargs):

        super().__init__(sense = mip.MINIMIZE, **kwargs)

        self.minimum_benefit = minimum_benefit

    def _objective(self):

        cost = self._df['discounted_costs']

        # Discounted costs

        self.model.objective = self._discounted_sum_all(cost)

    def _constraint(self):

        benefit = self._df['discounted_benefits']

        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention

        self.model += self._discounted_sum_all(benefit) >= self.minimum_benefit

        ## Also add constraint that only allows one intervention in a time period and region

    def fit(self, **kwargs):
        return self._fit(**kwargs)

