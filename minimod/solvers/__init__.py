## Imports for local packages
from minimod.utils.exceptions import MissingData, NotPandasDataframe, MissingOptimizationMethod

from minimod.utils.summary import Summary

import pandas as pd    
import mip     

class BaseSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """    
    
    
    def __init__(self, 
                 data  =None,
                 intervention_col = 'intervention',
                 space_col = 'space',
                 time_col = 'time',
                 benefit_col = 'benefit',
                 cost_col = 'costs',
                 interest_rate_cost = 0.0, # Discount factor for costs
                 interest_rate_benefit = 0.03,
                 va_weight =1.0 # VA Weight
                 ):
        
        self.interest_rate_cost = interest_rate_cost
        self.interest_rate_benefit = interest_rate_benefit
        self.va_weight = va_weight
        self.discount_costs = 1/(1 + self.interest_rate_cost)
        self.discount_benefits = 1/(1 + self.interest_rate_benefit)
        
        if data is not None:
            self._data = data  
        else:
            raise MissingData("No data specified.")
        
        self._intervention_col = intervention_col
        self._space_col = space_col
        self._time_col = time_col
        
        self._benefit_col = benefit_col
        self._cost_col = cost_col
        
        self._all_columns_list = [intervention_col, space_col, time_col]
        
        self._df = self._process_data()

    
    def _is_dataframe(self):
        
        if isinstance(self._data, pd.DataFrame) == False:
            
            raise NotPandasDataframe("[Error]: Input data is not a dataframe. Please input a dataframe.")        
        
        
    def _process_data(self):
        """This method processes the data and gets it ready to be used in the problem
            
        Arguments:
        data {pandas dataframe} -- A pandas dataframe with columns for each time period and a column for regions or whatever spatial dimension is used. The rows for each time period should give the benefits of each intervention at time t, and space j
        
        |k     | j   |t   | benefits   | costs |
        |------|-----|----|------------|-------|
        |maize |north|0   | 100        | 10    |
        |maize |south|0   | 50         | 20    |
        |maize |east |0   | 30         |30     |
        |maize |west |0   | 20         |40     |
        
    Raises:
        MissingColumn: If a column is not included, it raises the missing column exception
        """        
        
        ## First do some sanity checks
        self._is_dataframe()
        
        
        df = (
            self._data
            .assign(time_col = lambda df: df[self._time_col].astype(float),
                    time_rank = lambda df: df[self._time_col].rank(numeric_only=True, method= 'dense') -1 ,
                    time_discount_costs = lambda df: self.discount_costs**df['time_rank'],
                    time_discount_benefits = lambda df: self.discount_benefits**df['time_rank'])
            .set_index(self._all_columns_list)
            .sort_index(level = tuple(self._all_columns_list)) 
            )
        return df
                
    
    def _constraint(self, model, x , **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """        
        pass
    
    def _objective(self, model, x , **kwargs):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """        
        pass
    
    def _fit(self, method = None, solver_name = mip.CBC,
             **kwargs):
                
        self.status = None
        
        if method is None:
            raise MissingOptimizationMethod("Please add an optimization method ('max' or 'min')")
        else:
            self._method = method
        
        print(f"""
              Loading MIP Model with:
              Solver = {str(solver_name)}
              Method = {self._method}
              """)
        
        ## Tell the fitter whether to maximize or minimize
        if self._method == 'min':
            m = mip.Model(sense = mip.MINIMIZE, solver_name= solver_name)
        if self._method == 'max':
            m = mip.Model(sense = mip.MAXIMIZE, solver_name = solver_name)
            
        ## Now we create the choice variable, x, which is binary and is the size of the dataset. 
        
        ## In this case, it should just be a column vector with the rows equal to the data:
        
        
        self._N = len(self._df)
        
        x = [m.add_var(var_type= mip.BINARY) for i in range(self._N)]
        
        ## Now write the objective function
        self._objective(m, x)
        
        ## Now add constraints to the model
        self._constraint(m, x)

            
        ## Now, allow for arguments to the optimize function to be given:

        max_seconds = kwargs.pop('max_seconds', mip.INF)
        max_nodes = kwargs.pop('max_nodes', mip.INF)
        max_solutions = kwargs.pop('max_solutions', mip.INF)
        
        self.status = m.optimize(max_seconds, max_nodes, max_solutions)
        
        if self.status == mip.OptimizationStatus.OPTIMAL:
            print("[Note]: Optimal Solution Found")
        elif self.status == mip.OptimizationStatus.FEASIBLE:
            print("[Note]: Feasible Solution Found. This may not be optimal.")
        elif self.status == mip.OptimizationStatus.NO_SOLUTION_FOUND:
            print('[Warning]: No Solution Found')
            
        opt_vars = [v.x for v in m.vars]

        df_copy= self._df.copy(deep = True)
        
        df_copy['opt_vals'] = opt_vars
        
        df_copy['opt_benefit'] = df_copy[self._benefit_col] * df_copy['opt_vals']
        
        df_copy['opt_costs'] = df_copy[self._cost_col] * df_copy['opt_vals']
        
        self._objective_value = m.objective_value
        self._objective_bound = m.objective_bound
        self._opt_df = df_copy[['opt_vals', 'opt_benefit', 'opt_costs']]
        
        m.clear()
        
        return self._opt_df
    
    def report(self):
        
        s = Summary(self)
        
        return s._report()
    
            
        
        

        
                 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        