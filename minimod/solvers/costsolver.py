from minimod.solvers import BaseSolver
from minimod.helpers.exceptions import NotPandasDataframe, MissingColumn

import pandas as pd
import mip

class CostSolver(BaseSolver):
    
    def __init__(self, 
                 interest_rate = 0.03 , 
                 va_weight=1):
        
        super().__init__(interest_rate, va_weight=va_weight)
        
    
    def _objective(self, model):
        
        k = self.__df[self.__intervention_col]
        beta = self.__df['time_discount']
        
        model.objective = mip.xsum(x[i]*k[i]*beta[i] for i in self.__N)
        
    def _constraint(self, model, **kwargs):
        
        model.add_constr