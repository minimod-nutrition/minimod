from minimod.base.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import OptimizationSummary

import pandas as pd
import mip
import numpy as np

class BenefitSolver(BaseSolver):
    """This is the solver for benefit maximization. This fitter solves the problem of maximizing effective coverage subject to a cost constraint. This problem solved by this fitter is:
    
        $$
        \max \sum_{k} \sum_{t} Y_{k,t} \sum_{j} \frac{EfCvg_{k,j,t}}{(1+r)^t} + \sum_{k} \sum_{j} \sum_{t} X_{k,j,t} \frac{EfCvg_{k,j,t}}{(1+r)^t}
        s.t. 
        \sum_{t} Y_{k,t} \sum_{j} \frac{TC_{k,j,t}}{(1+r)^t} + \sum_{k} \sum_{j} \sum_{t} X_{k,j,t} \frac{TC_{k,j,t}}{(1+r)^t} \leq TF
        $$
        
    Arguments:
        data {pandas dataframe} -- A pandas dataframe with columns for each time period and a column for regions or whatever spatial dimension is used. The rows for each time period should give the benefits of each intervention at time t, and space j
        
        |k     | j   |t   | benefits/costs   |
        |------|-----|----|------------------|
        |maize |north|0   | 100              |
        |maize |south|0   | 50               |
        |maize |east |0   | 30               |
        |maize |west |0   | 20               |
        
                
    """

    def __init__(self, 
                  total_funds = 35821703,
                  **kwargs):
        
        super().__init__(sense = mip.MAXIMIZE, **kwargs)     

        if total_funds is not None:
            self.total_funds = total_funds
        else:
            raise Exception("No total funds constraint specified.")


    def _objective(self, model, x, **kwargs):
        
        benefit = self._df[self._benefit_col]     
        # Discounted costs
        
        model.objective = self._discounted_sum_all(benefit)
        
        
    def _constraint(self, model, x, **kwargs):
        
        cost = self._df[self._cost_col]
        
        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention

        
        model += self._discounted_sum_all(cost) <= self.total_funds
        
        ## Also add constraint that only allows one intervention in a time period and region
        
    def fit(self, extra_const = None):
        return self._fit(extra_const = extra_const)
    
    def report(self):
        
        s = OptimizationSummary(self)
        
        super().report()
        
        total_costs = self.model.objective_bound
        total_benefits = self.model.objective_value

        results = [
            ('Total Funds', self.total_funds),
            ("Total Cost", total_costs ),
            ("Total Coverage", total_benefits)
        ]
        
        s.print_generic(results)
        
        s.print_ratio(name = "Coverage per Cost",
                      num = total_benefits,
                      denom = total_costs)
        
        s.print_grouper(name = "Total Cost and Coverage over Time",
                        data = self.opt_df,
                        style = 'markdown')


        
        
    
    
    
    



        