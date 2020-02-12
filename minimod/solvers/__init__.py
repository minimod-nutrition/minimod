## Imports for local packages
from minimod.helpers.exceptions import *

import pandas as pd        

class BaseSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """    
    
    
    def __init__(self,
                 total_funds_available = 35821703,
                 total_benefits = 13458058,
                 va_weight = 1,
                 va_weight_alpha = 1,
                 va_weight_wra = 0,
                 zinc_weight = 0,
                 zinc_weight_costs = 0,
                 
                 percentage_bau_benefits = 1,
                 interest_funds_loaned_out = 0,
                 interest_benefits = 0.03):


            
    def __repr__(self):
        
        return f"""
    Benefit Solver Instance initiated with:
    
    """
    
    def _is_column_none(self, **kwargs):
        
        ## Find keys for empty values
        key_for_empty_vals = [k for k, v in kwargs.items() if v is None]
        
        if key_for_empty_vals is not None:
        
            raise MissingColumn(f"You're missing {','.join(key_for_empty_vals)}")
    
    def _is_dataframe(self, d):
        
        if isinstance(d, pd.DataFrame) == False:
            
            raise NotPandasDataframe("[Error]: Input data is not a dataframe. Please input a dataframe.") 
        
    def _process_data(self, **kwargs):
        """This method processes the data and gets it ready to be used in the problem
            
            Arguments:
            data {pandas dataframe} -- A pandas dataframe with columns for each time period and a column for regions or whatever spatial dimension is used. The rows for each time period should give the benefits of each intervention at time t, and space j
            
            |k     | j   |t   | benefits/costs   |
            |------|-----|----|------------------|
            |maize |north|0   | 100              |
            |maize |south|0   | 50               |
            |maize |east |0   | 30               |
            |maize |west |0   | 20               |
            
        Raises:
            MissingColumn: If a column is not included, it raises the missing column exception
        """        
        
        data = kwargs.pop('data')
        time_col = kwargs.pop('time_col')
        space_col = kwargs.pop('space_col')
        intervention_col = kwargs.pop('intervention_col')
        
        ## First do some sanity checks
        self._is_dataframe(data)
        
        ## check if columns are empty
        self._is_column_none(**kwargs)
        
        space = data[space_col]
        time = data[time_col]
        interventions = data[intervention_col]
        
        df = data.set_index([space, time, interventions])
        
        return df
    
    def _constraint(self, **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """        
        pass
    
    def _objective(self, **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """        
        pass
    
    def _fit(self, objective, constraint, method = None ):
        
        if method is None:
            raise MissingOptimizationMethod("Please add an optimization method ('max' or 'min')")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        