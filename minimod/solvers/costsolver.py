from minimod.solvers import BaseSolver
from minimod.helpers.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd
import mip

class CostSolver(BaseSolver):
    
    def __init__(self, 
                  minimum_benefit = 15958220,
                  **kwargs):
        
        super().__init__(**kwargs)     
    
        self.minimum_benefit = minimum_benefit



    def _objective(self, model, x, **kwargs):
        
        cost = self._df[self._cost_col]
        beta = self._df['time_discount_costs']
        
        model.objective = mip.xsum(x[i]*cost[i]*beta[i] for i in range(self._N))
        
    def _constraint(self, model, x, **kwargs):
        
        benefit = self._df[self._benefit_col]
        
        gamma = self._df['time_discount_benefits']
        
        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        
        model += mip.xsum(x[i]*benefit[i]*gamma[i] for i in range(self._N)) >= self.minimum_benefit
        
    def fit(self):
        return self._fit(method = 'min')
    
    