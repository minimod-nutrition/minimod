# %%
from typing import Callable
import pandas as pd
import math
import  numpy as np
from .data import CostDataProcessor
import scipy.optimize as opt
        
class PremixCostCalculator:
    
    def __init__(self, 
                 data: CostDataProcessor = None,
                 upcharge: int = None,
                 excipient_price: float= None):
        
        self.upcharge = upcharge if not None else 1
        self.excipient_price = excipient_price if not None else 1.5
        
        self.data = data
        
        self._amt_fort = data.amt_fort
        self.price = data.price
        
        self.nutrient_subtotal = self.amt_fort.sum()
        
    @property
    def amt_fort(self):
        return self._amt_fort
    
    @amt_fort.setter
    def amt_fort(self, value):
        if len(value) != self._amt_fort.shape[0]:
            raise ValueError("New value's length doesn't equal length of amt_fort")
            
        self._amt_fort.loc[:] = value
        
    def reset_amt_fort(self):
        
        self._amt_fort = self._d.amt_fort
        
    @property
    def excipient(self):
        return self.addition_rate - self.nutrient_subtotal
        
    @property
    def excipient_prop(self):
        return (self.addition_rate - self.nutrient_subtotal)/self.addition_rate
    
    @property
    def excipient_cost(self):
        return self.excipient_prop * self.excipient_price
    
    @property
    def addition_rate(self):
        return int(math.ceil((self.nutrient_subtotal*1.1)/50.0)) * 50
    
    @property 
    def nutrient_total(self): 
        return self.cost_premix.sum() + self.excipient_cost
    
    @property
    def total_cost(self):
        return self.nutrient_total + self.upcharge
    
    @property
    def prop_fort(self):
        return self.amt_fort/self.addition_rate
    
    @property
    def cost_premix(self):
        return self.prop_fort*self.price
    
    def total_vehicle(self, fmt = 'kg'):
        
        if fmt == 'kg':
            div = 1_000_000
        elif fmt == 'mt':
            div = 1_000
        
        return self.nutrient_total*(self.addition_rate/div)
    
    @property
    def total_cost_mt_vehicle(self):
        return (self.total_cost*self.addition_rate)/1_000
    
    def premix_cost_summary(self):
        cost_summary = {
            'Nutrients Total ($/kg)' : self.nutrient_total,
            'Upcharge ($/kg)' : self.upcharge,
            'Total Cost ($/kg vehicle)' : self.total_cost,
            'Total ($/kg vehicle)' : self.total_vehicle(fmt = 'kg'),
            'Total ($/MT vehicle)' : self.total_vehicle(fmt = 'mt'),
            'Total Cost per kg Premix' : self.total_cost,
            'Total Cost per MT of Vehicle' : self.total_cost_mt_vehicle
        }

        return pd.DataFrame(data = cost_summary.values(), 
                            index = cost_summary.keys()) 
        
    def recalculate_total_costs(self):
        
        self.amt_fort
        self.nutrient_subtotal
        self.addition_rate
        self.prop_fort
        self.price
        self.excipient_prop 
        self.excipient_price
        self.cost_premix.sum() 
        self.excipient_cost
        self.nutrient_total
        self.upcharge
        
        return self.total_cost
    
    def line_fit(self, nutrient : str, compound : str, func : Callable=None):
        """Fits benefits data to `func`     

        Args:
            func (Callable, optional): Function to fit data to. If None, line is chosen. Defaults to None.
        """        
        
        if func is None:
            func = lambda x, m, b: (m*x) + b
            
        y = []
        x = np.linspace(1, 20000, 10)
            
        for i in x:
            self.amt_fort.loc[(nutrient, compound)] = i
                        
            y.append(self.recalculate_total_costs())
                    
        popt, pcov = opt.curve_fit(func, x, y)
        
        def f(x):
            return func(x, *popt)
        
        return f, popt, pcov
            
if __name__ == '__main__':

    import matplotlib.pyplot as plt

    # Load data from github
    df = pd.read_csv("example/cost_data.csv")
# Check if we change Iron

    fortificants = ['Micronized ferric pyrophosphate',
    'Retinyl Palmitate- 250,000 IU/g (dry)',
    'Zinc Oxide',
    'Vit. B-12 0.1% WS',
    'Folic Acid'
    ]
    
    d = CostDataProcessor(
        data = df,
        vehicle = 'Bouillon',
        fortificant_col = 'compound',
        fortificant=fortificants,
        activity_col = 'fort_prop',
        overage_col = 'fort_over'
    )

    p = PremixCostCalculator(
        data = d
    )

    f, params, cov = p.line_fit()

    x = np.linspace(1, 20000, 10)
    plt.plot(x, f(x))


# %%
