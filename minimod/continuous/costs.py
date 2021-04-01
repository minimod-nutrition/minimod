# %%
import pandas as pd
import math
import warnings

class DataProcessor:
    
    def __init__(self, 
                 data: pd.DataFrame,
                 vehicle: str,
                 compound: list,
                 vehicle_col: str = None,
                 nutrient_col : str = None,
                 compound_col : str = None,
                 activity_col : str = None,
                 fort_level_col :  str = None,
                 overage_col : str = None,
                 price_col : str = None):
                
        self.vehicle_col = vehicle_col if vehicle_col is not None else 'vehicle'
        self.nutrient_col = nutrient_col if nutrient_col is not None else 'nutrient'
        self.compound_col = compound_col if compound_col is not None else 'compound'
        self.activity_col = activity_col if activity_col is not None else 'activity'
        self.fort_level_col = fort_level_col if fort_level_col is not None else 'fort_level'
        self.overage_col = overage_col if overage_col is not None else 'overage'
        self.price_col = price_col if price_col is not None else 'price'
        
        self._data = (
            data
            .loc[lambda df: df[self.vehicle_col] == vehicle]
            .loc[lambda df: df[self.compound_col].isin(compound)]
            .set_index([self.nutrient_col, self.compound_col])
            )
        
        self.nutrient = self._data.index.get_level_values(self.nutrient_col)
        self.compound = self._data.index.get_level_values(self.compound_col)
        self.activity = self._data[self.activity_col]
        self.fort_level = self._data[self.fort_level_col]
        self.overage = self._data[self.overage_col]
        self.price = self._data[self.price_col]
        
    @property
    def data(self):
        return self._data
        
    @property
    def amt_fort(self):
        return (self.fort_level + (self.fort_level * self.overage))/self.activity
        
        
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


    
    
# %%
