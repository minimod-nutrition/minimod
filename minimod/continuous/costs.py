# %%
from typing import Callable
import pandas as pd
import math
import  numpy as np
import matplotlib.pyplot as plt
from . import DataProcessor
import scipy.optimize as opt
        
class PremixCostCalculator:
    
    def __init__(self, 
                 name: str = None,
                 data: pd.DataFrame = None,
                 vehicle: str = None,
                 compound: list = None,
                 vehicle_col: str = None,
                 nutrient_col : str = None,
                 compound_col : str = None,
                 activity_col : str = None,
                 fort_level_col :  str = None,
                 overage_col : str = None,
                 price_col : str = None,
                 upcharge : float = 1.0,
                 excipient_price : float = 1.5):
        
        self.upcharge = upcharge
        self.name = name
        self.excipient_price = excipient_price
        
        self.nutrient_col = nutrient_col
        self.compound_col = compound_col
        
        d = DataProcessor(data,
                          vehicle,
                          compound,
                          vehicle_col,
                          nutrient_col,
                          compound_col,
                          activity_col,
                          fort_level_col,
                          overage_col,
                          price_col)
        
        self._d = d
        
        self._amt_fort = d.amt_fort
        self.price = d.price
        
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

        

if __name__ == '__main__':
# %%
# Check if we change Iron

    compounds = ['Micronized ferric pyrophosphate',
    'Retinyl Palmitate- 250,000 IU/g (dry)',
    'Zinc Oxide',
    'Vit. B-12 0.1% WS',
    'Folic Acid'
    ]

    p = PremixCostCalculator(
        data = df,
        vehicle= 'Bouillon',
        compound=compounds,
        vehicle_col='vehicle',
        nutrient_col='nutrient',
        compound_col='compound',
        activity_col = 'fort_prop',
        fort_level_col = 'fort_level',
        overage_col = 'fort_over',
        price_col='price'

    )

    amt_fort_list = []

    for i in np.linspace(1, 20000, 1000):
        
        new_amt_fort = p.amt_fort
        
        new_amt_fort[1] = i
        
        p.amt_fort = new_amt_fort
        
        amt_fort_list.append(p.total_cost)


    plt.plot(np.linspace(1, 20000, 1000), amt_fort_list)

