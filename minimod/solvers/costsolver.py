from minimod.solvers import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd
import mip
import numpy as np

class CostSolver(BaseSolver):
    
    def __init__(self, 
                  minimum_benefit = 15958220,
                  **kwargs):
        
        super().__init__(**kwargs)     
    
        self.minimum_benefit = minimum_benefit



    def _objective(self, model, x, **kwargs):
        
        cost = self._df[self._cost_col]
        beta = self._time_discount_costs
        
        # Discounted costs
        
        model.objective = mip.xsum(beta[t]*x[k,j,t]*cost.loc[k,j,t] \
                for k in range(self._K) \
                    for j in range(self._J) for t in range(self._T))
        
    def _constraint(self, model, x, **kwargs):
        
        benefit = self._df[self._benefit_col]
        
        gamma = self._time_discount_benefits
        
        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        
        
        model += mip.xsum(gamma[t]*\
            (mip.xsum(x[k,j,t]*benefit.loc[k,j,t] \
                for k in range(self._K) \
                    for j in range(self._J))) \
                 for t in range(self._T) ) >= self.minimum_benefit
        
        ## Also add constraint that only allows one intervention in a time period and region
        
    def fit(self, clear = False, extra_const = None):
        return self._fit(sense = mip.MINIMIZE, 
                         extra_const = extra_const,clear=clear)
    
    