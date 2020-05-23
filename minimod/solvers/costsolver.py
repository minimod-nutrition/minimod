from minimod.base.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import OptimizationSummary

from minimod.base.bau_constraint import BAUConstraintCreator


import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):
    def __init__(self, minimum_benefit=None, **kwargs):
        
        super().__init__(sense = mip.MINIMIZE, **kwargs)
                
        if isinstance(minimum_benefit, float) or isinstance(minimum_benefit, int):
            self.minimum_benefit = minimum_benefit
        elif isinstance(minimum_benefit, str):
            # Get sum of benefits for interventions
            self.minimum_benefit = self.bau.create_bau_constraint(self._df, minimum_benefit, 'discounted_benefits')
            
        # Add objective and constraint
        self.model.add_objective(self._objective())
        self.model.add_constraint(self._constraint(), self.minimum_benefit)

    def _objective(self):

        cost = self._df['discounted_costs']

        # Discounted costs
        return self._discounted_sum_all(cost)

    def _constraint(self):

        benefit = self._df['discounted_benefits']

        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        return self._discounted_sum_all(benefit) 

    def fit(self, **kwargs):
        return self._fit(**kwargs)
    
    def report(self):
        
        s = OptimizationSummary(self)
        
        super().report()

        results = [
            ('Minimum Benefit', self.minimum_benefit),
            ("Total Cost", self.objective_value),
            ("Total" + self.benefit_title, self.objective_bound)
        ]
        
        s.print_generic(results)
        
        s.print_ratio(name = "Cost per Benefit",
                      num = self.objective_bound,
                      denom = self.objective_value)
        
        s.print_grouper(name = "Total Cost and Benefits over Time",
                        data = self.opt_df,
                        style = 'markdown')
        
