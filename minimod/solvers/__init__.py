## Imports for local packages
from minimod.helpers.exceptions import *

import pandas as pd    
import mip     

class BaseSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """    
    
    
    def __init__(self, 
                 data,
                 intervention_col,
                 space_col,
                 time_col,
                 interest_rate, # Discount factor for the problem 
                 va_weight = 1 # VA Weight
                 ):
        
        self.interest_rate = interest_rate
        self.va_weight = va_weight
        self.discount = 1/(1 + self.interest_rate)
        
        self.__data = data
        
        self.__intervention_col = intervention_col
        self.__space_col = space_col
        self.__time_col = time_col
        
        self._all_columns_list = [intervention_col, space_col, time_col]
        
        self.__df = self._process_data()

            
    def __repr__(self):
        
        return f"""
    Benefit Solver Instance initiated with:
    
    """
    
    def _is_column_none(self):
        
        ## Find keys for empty values
        key_for_empty_vals = [k for k in self._all_columns_list  if k is None]
        
        if key_for_empty_vals is not None:
        
            raise MissingColumn(f" [Error]: You're missing {','.join(key_for_empty_vals)}")
    
    def _is_dataframe(self):
        
        if isinstance(self.__data, pd.DataFrame) == False:
            
            raise NotPandasDataframe("[Error]: Input data is not a dataframe. Please input a dataframe.")        
        
        
    def _process_data(self):
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
        
        ## First do some sanity checks
        self._is_dataframe()
        
        ## check if columns are empty
        self._is_column_none()
        
        df = (
            self.__data
            .assign(time_col = lambda df: df[self.__time_col].astype(float),
                    time_rank = lambda df: df[self.__time_col].rank(numeric_only=True, method= 'dense') -1 ,
                    time_discount = lambda df: self.discount**df['time_rank'])
            .set_index(self._all_columns_list)
            .sort_index(level = tuple(self._all_columns_list)) ## sort by time first
            )
        return df
                
    
    def _constraint(self, model , **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """        
        pass
    
    def _objective(self, model , **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """        
        pass
    
    def _fit(self, method = None, solver_name = mip.CBC, **kwargs):
        
        
        if method is None:
            raise MissingOptimizationMethod("Please add an optimization method ('max' or 'min')")
        
        print(f"""
              Loading MIP Model with:
              Solver = {solver_name.__class__.__name__}
              Method = {method}
              """)
        
        ## Tell the fitter whether to maximize or minimize
        if method == 'min':
            m = mip.Model(sense = mip.MINIMIZE, solver_name= solver_name)
        if method == 'max':
            m = mip.Model(sense = mip.MAXIMIZE, solver_name = solver_name)
            
        ## Now we create the choice variable, x, which is binary and is the size of the dataset. 
        
        ## In this case, it should just be a column vector with the rows equal to the data:
        
        
        self.__N = len(self.__df)
        
        x = [m.add_var(var_type= mip.BINARY) for i in range(N)]
        
        ## Now write the objective function
        self._objective(m)
        
        ## Now add constraints to the model
        self._constraint(m)

            
        ## Now, allow for arguments to the optimize function to be given:

        max_seconds = kwargs.pop('max_seconds', mip.INF)
        max_nodes = kwargs.pop('max_nodes', mip.INF)
        max_solutions = kwargs.pop('max_solutions', mip.INF)
        
        return m.optimize(max_seconds, max_nodes, max_solutions)
        
        
        
        
        
            
        
        

        
                 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        