from minimod.base.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import OptimizationSummary

import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):
    def __init__(self, minimum_benefit=None, **kwargs):

        super().__init__(sense = mip.MINIMIZE, **kwargs)
        
        if isinstance(minimum_benefit, float) or isinstance(minimum_benefit, int):
            self.minimum_benefit = minimum_benefit
        elif isinstance(self.minimum_benefit, str):
            # Get sum of benefits for interventions
            self.minimum_benefit = self.bau.create_bau_constraint()

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
        
        s = OptimizationSummary(self)
        
        super().report()

        results = [
            ('Minimum Benefit', self.minimum_benefit),
            ("Total Cost", self.model.objective_value),
            ("Total" + self.benefit_title, self.model.objective_bound)
        ]
        
        s.print_generic(results)
        
        s.print_ratio(name = "Cost per Benefit",
                      num = self.model.objective_bound,
                      denom = self.model.objective_value)
        
        s.print_grouper(name = "Total Cost and Benefits over Time",
                        data = self.opt_df,
                        style = 'markdown')
        
