
import numpy as np
import pandas as pd
import os

## Imports for local packages
from minimod.helpers.exceptions import *
               

class BenefitSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """    
    
    
    def __init__(self, data = None):
        
        self.data = data
        
        if self.data is None:
            raise DataNotLoaded("Pandas Dataframe requirement.")
        if data is not None:
            self.ds = self.load_data()
            
    def __repr__(self):
        
        return f"""
    Benefit Solver Instance initiated with:
    Data from: {self.data}
    
    """
        
        
    # def _load_data(self):
        
    #     """
    #     Loads in a data that includes benefits and costs
    #     This data must include a interventions, time and space over which interventions take place.
        
    #     The structure of the data must have columns for time, a column for space (cities, states, regions), and a column for the benefits or costs, depending on the problem to be solved.
        
    #     Arguments:
    #         filename {csv, xlsx, xls} -- A dataset in the correct format described above
                    
    #     Raises:
    #         Exception: raises an error if a data with a forbidden data extension is given.
        
    #     Returns:
    #         Pandas dataframe
    #     """ 
        
    #     _ , file_ext = os.path.splitext(self.data)
        
    #     if file_ext == ".csv":
    #         imported_data = pd.read_csv(self.data)
    #     elif (file_ext == ".xlsx" or file_ext == '.xls'):
    #         imported_data = pd.read_excel(self.data)
    #     else:
    #         raise ForbiddenExtensionException("This is not a supported extension. Only csv, xlsx or xls are allowed.")
        
    #     return imported_data
    
def _process_imported_data(self):
"""This method takes the loaded data from `_load_data` and processes it so that it can be used in the solver

Returns:
    Processed pandas dataframe
"""    
    imported_data  = self._load_data()
    
    

    
    
    
    
            
        
if __name__ == "__main__":
    
    a = BenefitSolver(data = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/GAMS_R Project/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx")
    
    print(a)