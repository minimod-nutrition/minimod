from minimod.solvers import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd

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



        
        
    
    
    
    



        