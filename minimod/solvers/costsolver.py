from minimod.solvers.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import Summary

import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):
    def __init__(self, minimum_benefit=None, **kwargs):

        super().__init__(sense = mip.MINIMIZE, **kwargs)

        if minimum_benefit is not None:
            self.minimum_benefit = minimum_benefit
        else:
            raise Exception("No minimum benefit specified.")

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
    
    def report(self):
        
        s = Summary(self)
        
        super().report()

        results = [
            ('Minimum Benefit', self.minimum_benefit),
            ("Total Cost", self.model.objective_value),
            ("Total Coverage", self.model.objective_bound)
        ]
        
        s.print_generic(results)
        
        s.print_ratio(name = "Coverage per Cost",
                      num = self.model.objective_bound,
                      denom = self.model.objective_value)
        
        s.print_grouper(name = "Total Cost and Coverage over Time",
                        data = self.opt_df,
                        style = 'markdown')
        
