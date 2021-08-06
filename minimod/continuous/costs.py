# %%
from typing import Callable
import pandas as pd
import math
import  numpy as np
from data import CostDataProcessor
import scipy.optimize as opt
        
class PremixCostCalculator:
    
    def __init__(self, 
                 data: CostDataProcessor = None,
                 upcharge: int = None,
                 excipient_price: float= None):
        """A class to create the functional relationship between costs and the amount of fortification.

        Args:
            data (costDataProcessor): Dataframe with costs across different levels of fortification
            upcharge (str): upcharge as an integer in the `data`
            excipient_price (flo): name of column with excipient price (as a float)
        """

        
        self.upcharge = upcharge if not None else 1
        """ if else function to provide default value of 1 for upchrage whenever not given in data
        """
        self.excipient_price = excipient_price if not None else 1.5
        """ if else function to provide default value of 1.5 for excipient price whenever not given in data
        """    
        self.data = data
        
        self._amt_fort = data.amt_fort
        self.price = data.price
        
        self.nutrient_subtotal = self.amt_fort.sum()
        """ provides information of the coloumns available of mentioned in the premixcost calculator class. The 
            data includes information on amount fortified and break up costs in terms of price for fortifying at 
            different levels.
        """
        
    @property
    def amt_fort(self):
        return self._amt_fort
        """ This function takes on the values provided in the data for anount fortified in each vehicle. @property
        suggests no changes/modifications allowed to this function and its values. 
    
        Returns:
               amount fortified as per self._amt_fort
        """
    
    @amt_fort.setter
    def amt_fort(self, value):
        if len(value) != self._amt_fort.shape[0]:
            raise ValueError("New value's length doesn't equal length of amt_fort")
            
        self._amt_fort.loc[:] = value
        
    def reset_amt_fort(self):
        
        self._amt_fort = self._d.amt_fort
        
        """ This function provides the amount fortified which equal to the amount sepcified in the data.
            if the length do not match the amount specified in the data an error message is raised. 
            Setter or reset doesn't return anything but change the attributes as defined in the function. 
       (not sure if I described this one correctly??) 
    
       
        """
        
        
        
    @property
    def excipient(self):
        return self.addition_rate - self.nutrient_subtotal
    
        """ This function explains the excipient column of the cost calculation which is addition rate minus subtotal of all
            nutrients present in the vehicle. 
    
        Returns:
               the value of excipient as defined by the function.
        """  
    
        
    @property
    def excipient_prop(self):
        return (self.addition_rate - self.nutrient_subtotal)/self.addition_rate
        """ This function is just converting the excipient into proportions. Hence it is addition rate minus subtotal of                     (costs??) all nutrients present in the vehicle divied by addition rate. 
    
        Returns:
               the value of excipient as defined by the function in proportionate terms.
        """
    
    @property
    def excipient_cost(self):
        return self.excipient_prop * self.excipient_price
        """ This function provides the excipient cost calculated using excipient proportions multiplied by excipient price. 
    
        Returns:
               the cost of excipient as defined by the function.
        """
    
    @property
    def addition_rate(self):
        return int(math.ceil((self.nutrient_subtotal*1.1)/50.0)) * 50
        """ This function defines the addition rate used in calculating excipient costs as mentioned above. 
       
    
        Returns:
               An integer value of the formula provided above???.
        """
    
    @property 
    def nutrient_total(self): 
        return self.cost_premix.sum() + self.excipient_cost
    
        """ This function defines the total nutrient cost which is the addition of cost of premix and excipient cost.
            
    
        Returns:
               It provides the cost as defined above in the function.
        """
    
    @property
    def total_cost(self):
        return self.nutrient_total + self.upcharge
    
        """ This function defines the total costs which is the addition of nutrient cost as defined above 
            plus the upcharge cost.
            
    
        Returns:
               It provides the total cost as defined above in the function.
        """
    
    @property
    def prop_fort(self):
        return self.amt_fort/self.addition_rate
    
        """ This function defines the proportion fortified which is the amount fortified divided by addition rate.
            
    
        Returns:
               It provides proportion fortified in the vehicle.
        """
    
    @property
    def cost_premix(self):
        return self.prop_fort*self.price
        """ This function defines the cost of the premix which is the proportion fortfied multiplied by the price.
            
    
        Returns:
               It provides the cost of the premix for the proportion fortified.
        """
    
    def total_vehicle(self, fmt = 'kg'):
        
        if fmt == 'kg':
            div = 1_000_000
        elif fmt == 'mt':
            div = 1_000
        
        return self.nutrient_total*(self.addition_rate/div)
    
        """ ??? (not sure if this is correct) This function defines the format of costs which can be $/kg or $/MT.
            The if else function defines that for kg we need to divide mg by 1000000 and for kg to Mt we need to divide 
            by 1000.
            
    
        Returns:
               ??? not clear what the formula is doing here.
        """
    
    @property
    def total_cost_mt_vehicle(self):
        return (self.total_cost*self.addition_rate)/1_000
    
        """ This function provides the cost per metric tonne for 
            sepcific vehicle as defined in the formula. 
            
    
        Returns:
               Cost per metric tonne ($/mt), its total cost multiplied by additon rate divided by 1000.
        """
    
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
    """ This function provides a summary of all the important functions defined above which will be sued in plotting the
        cost line at avrius levels of fortification for different vehicles and nutrients.
                    
    
        Returns:
               ??? it provides these values in the data frame ???.
        """
    
    def line_fit(self, nutrient : str, compound : str, func : Callable=None):
        
        """Fits costs data to `func` ????     

        Args:
            func (Callable, optional): Function to fit data to. If None, line is chosen. Defaults to None.
        """        
        
        if func is None:
            func = lambda x, m, b: (m*x) + b
            
        y = []
        x = np.linspace(1, 20000, 10)
            
        for i in x:
            self.amt_fort.loc[(nutrient, compound)] = i
            
            self.nutrient_subtotal = self.amt_fort.sum()
            
            y.append(self.total_cost)
                    
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
