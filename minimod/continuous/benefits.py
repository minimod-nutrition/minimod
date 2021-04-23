# %%

import pandas as pd
import numpy as np
import scipy.optimize as opt
from typing import Callable
from functools import partial

class Benefits:
    
    def __init__(self,
                 data: pd.DataFrame,
                 benefit_col: str,
                 increment_col: str
                 ):
        """A class to create the functional relationship between benefits and the amount of fortification.

        Args:
            data (pd.DataFrame): Dataframe with benefits across different levels of fortification
            benefit_col (str): name of benefit column in `data`
            increment_col (str): name of column with levels of fortificant
        """        
        
        self.data = data
        self.benefit_col = benefit_col
        self.increment_col = increment_col
    
    @property
    def increment(self):
        """Checks if increment is equal across all levels of fortification
        """        
        
        increment = self.data.assign(lag = lambda df: df[self.increment_col].shift(-1),
                                     diff = lambda df: df[self.increment_col] - df['lag'])['diff']
        
        if increment.nunique() > 1:
            print("increment isn't equal across fortification levels. Using mean increment...")
        
        return increment.mean()
    
    def curve_fit(self, func : Callable=None):
        """Fits benefits data to `func`     

        Args:
            func (Callable, optional): Function to fit data to. If None, logistic curve is chosen. Defaults to None.
        """        
        
        if func is None:
            func = lambda x, L, k, x0: L/(1 + np.exp(-k*(x - x0)))
            
        x = self.data[self.increment_col]
        y = self.data[self.benefit_col]
        
        popt, pcov = opt.curve_fit(func, x, y)
        
        def f(x):
            return func(x, *popt)
        
        return f, popt, pcov

    
# %%
if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    from example.example_data import benefits, increment, df
    
    b = Benefits(data=df,
                 benefit_col='benefits',
                 increment_col='increment')
    
    f, params, cov = b.curve_fit()
    
    plt.scatter(increment, benefits)
    plt.plot(increment, f(increment), color='tab:red')


# %%
