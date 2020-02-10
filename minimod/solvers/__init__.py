import numpy as np
import pandas as pd
import os

## Imports for local packages
from minimod.helpers.exceptions import *
               

class BaseSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """    
    
    
    def __init__(self):
        pass


            
    def __repr__(self):
        
        return f"""
    Benefit Solver Instance initiated with:
    
    """