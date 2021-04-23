from typing import Callable
from benefits import Benefits
from costs import PremixCostCalculator
import pandas as pd
from data import CostDataProcessor
from dataclasses import make_dataclass

class ContinuousOptimizer:
    
    def __init__(self, 
                 vehicle_dict: dict,
                 benefit_data : pd.DataFrame,
                 cost_data: pd.DataFrame,
                 benefit_col: str = None,
                 increment_col : str = None,
                 vehicle_col: str = None,
                 nutrient_col: str = None,
                 fortificant_col: str = None,
                 activity_col: str = None,
                 fort_level_col: str = None,
                 overage_col: str = None,
                 price_col: str = None,
                 upcharge: int = None,
                 excipient_price: float = None,
                 benefit_func : Callable = None,
                 cost_func : Callable = None
                 ):
        
        self.vehicle_dict = vehicle_dict
        self.cost_data = cost_data
        self.benefit_data = benefit_data
        
        self.benefit_col = benefit_col
        self.increment_col = increment_col
        
        self.vehicle_col = vehicle_col
        self.nutrient_col = nutrient_col
        self.fortificant_col = fortificant_col
        self.activity_col = activity_col
        self.fort_level_col = fort_level_col
        self.overage_col = overage_col
        self.price_col = price_col
        self.upcharge = upcharge
        self.excipient_price = excipient_price
        
        self.benefit_func = benefit_func
        self.cost_func = cost_func
     
    @property   
    def costs(self):
        
        cost_dict = {}
        
        for v, f in self.vehicle_dict.items():
        
            cost_data = CostDataProcessor(
                data =self.cost_data,
                vehicle = v,
                fortificant = f,
                vehicle_col = self.vehicle_col,
                nutrient_col = self.nutrient_col,
                fortificant_col = self.fortificant_col,
                activity_col = self.activity_col,
                fort_level_col = self.fort_level_col,
                overage_col = self.overage_col,
                price_col = self.price_col
            )
            
            costs = PremixCostCalculator(
                data = cost_data,
                upcharge=self.upcharge,
                excipient_price=self.excipient_price
            )
            
            cost_dict.update({'vehicle' : v,
                              'fortificant' : f,
                              'cost_fit' : costs.line_fit(self.cost_func)})
            
            return pd.DataFrame(cost_dict).set_index(['vehicle', 'fortificant'])
            
            
    @property      
    def benefits(self):
        
        benefit_dict = {}
        
        for v,f in self.vehicle_dict.items():
            
            df = (
                self.benefit_data
                .loc[lambda df: df[self.vehicle_col] == v]
                .loc[lambda df: df[self.fortificant_col].isin(f)]
                )
        
        
            benefits = Benefits(
                self.df,
                self.benefit_col,
                self.increment_col
            )
            
            benefit_dict.update(
                {'vehicle' : v,
                 'fortificant' : f,
                 'benefit_fit' : benefits.curve_fit(self.benefit_func)}
            )
            
            return pd.DataFrame(benefit_dict).set_index(['vehicle', 'fortificant'])

        
    @property
    def data(self):
        
        df = (
            self.costs
            .merge(self.benefits,
                   left_index=True,
                   right_index=True,
                   how='outer',
                   indicator=True
                   )
        )
        
        if not (df._merge == 'both').all():
            print("Merge was not perfect. check `_merge`")
        else:
            df = df.drop(['_merge'], axis=1)
            
        return df

    def optimize(self)
    
        
        