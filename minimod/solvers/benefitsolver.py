from minimod.solvers import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd
import mip
import numpy as np

class BenefitSolver(BaseSolver):
    """This is the solver for benefit maximization. This fitter solves the problem of maximizing effective coverage subject to a cost constraint. This problem solved by this fitter is:
    
    ..math::

        \max \sum_{k} \sum_{t} Y_{k,t} \sum_{j} \frac{EfCvg_{k,j,t}}{(1+r)^t} + \sum_{k} \sum_{j} \sum_{t} X_{k,j,t} \frac{EfCvg_{k,j,t}}{(1+r)^t}
        s.t. 
        \sum_{t} Y_{k,t} \sum_{j} \frac{TC_{k,j,t}}{(1+r)^t} + \sum_{k} \sum_{j} \sum_{t} X_{k,j,t} \frac{TC_{k,j,t}}{(1+r)^t} \leq TF
    
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
        
        super().__init__(**kwargs)     
    
        self.total_funds = total_funds


    def _objective(self, model, x, **kwargs):
        
        benefit = self._df[self._benefit_col]
        
        gamma = self._time_discount_benefits
        

        
        # Discounted costs
        
        model.objective = mip.xsum(gamma[t]*\
            (mip.xsum(x[k,j,t]*benefit.loc[k,j,t] \
                for k in range(self._K) \
                    for j in range(self._J))) \
                 for t in range(self._T) )
        
        
    def _constraint(self, model, x, **kwargs):
        
        cost = self._df[self._cost_col]
        beta = self._time_discount_costs
        
        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        
        
        model += mip.xsum(beta[t]*\
            (mip.xsum(x[k,j,t]*cost.loc[k,j,t] \
                for k in range(self._K) \
                    for j in range(self._J))) \
                 for t in range(self._T) ) <= self.total_funds
        
        ## Also add constraint that only allows one intervention in a time period and region
        
    def fit(self, extra_const = None):
        return self._fit(sense = mip.MAXIMIZE, 
                         extra_const = extra_const)


        
        
    
    
    
    



        