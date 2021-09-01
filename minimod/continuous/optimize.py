# %%
from typing import Callable
from minimod.continuous.benefits import Benefits
from minimod.continuous.costs import PremixCostCalculator
import pandas as pd
from minimod.continuous.data import CostDataProcessor
import re
import numpy as np
from minimod.continuous.exceptions import NonUniqueNutrient, NutrientNotFound, FunctionValueIncompatible, EmptyDataFrame
from scipy.optimize import minimize, basinhopping

class ContinuousOptimizer:
    def __init__(
        self,
        vehicle_dict: dict,
        benefit_data: pd.DataFrame,
        cost_data: pd.DataFrame,
        benefit_col: str = None,
        increment_col: str = None,
        vehicle_col: str = None,
        nutrient_col: str = None,
        fortificant_col: str = None,
        activity_col: str = None,
        fort_level_col: str = None,
        overage_col: str = None,
        price_col: str = None,
        upcharge: int = 1,
        excipient_price: float = 1.5,
        benefit_func: Callable = None,
        cost_func: Callable = None,
        strict=False,
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

        self.strict = strict

    def costs(self, nutrient_choice=None):

        cost_dict = {"vehicle": [], "fortificant": [], "cost_fit": [], 'popt_cost' : [], 'pcov_cost' : []}

        for v, f in self.vehicle_dict.items():

            cd = CostDataProcessor(
                data=self.cost_data,
                vehicle=v,
                fortificant=f,
                vehicle_col=self.vehicle_col,
                nutrient_col=self.nutrient_col,
                fortificant_col=self.fortificant_col,
                activity_col=self.activity_col,
                fort_level_col=self.fort_level_col,
                overage_col=self.overage_col,
                price_col=self.price_col
            )

            costs = PremixCostCalculator(
                data=cd, upcharge=self.upcharge, excipient_price=self.excipient_price
            )

            if nutrient_choice is None:
                nutrient, compound = f[0]
            elif isinstance(nutrient_choice, dict):
                nutrient_choice_new = nutrient_choice[v]

                # Use numpy.where to get index of match with true
                compound_index = np.where(
                    [
                        (re.search(fr"{nutrient_choice_new}", x[0], re.IGNORECASE))
                        for x in f
                    ]
                )

                # Now check if len(index) is 1 (it should be, as there should only be one entry for a nutrient in a vehicle)
                if not len(compound_index) == 1:
                    raise NonUniqueNutrient
                elif len(compound_index) == 0:
                    raise NutrientNotFound(nutrient_choice)

                nutrient, compound = f[compound_index[0][0]]
            else:
                raise Exception("Please specify a dictionary")
            
            fit = costs.line_fit(nutrient, compound, self.cost_func)

            cost_dict["vehicle"].append(v)
            cost_dict["fortificant"].append(str(f))
            cost_dict["cost_fit"].append(
                fit[0]
            )
            
            cost_dict['popt_cost'].append(fit[1])
            cost_dict['pcov_cost'].append(fit[2])

        return pd.DataFrame(cost_dict).set_index(["vehicle", "fortificant"])

    @property
    def benefits(self):

        benefit_dict = {"vehicle": [], "fortificant": [], "benefit_fit": [], 'popt_benefit' : [], 'pcov_benefit' : []}

        for v, f in self.vehicle_dict.items():

            df = self.benefit_data.loc[lambda df: df[self.vehicle_col] == v]

            if df.empty:
                raise EmptyDataFrame('benefit data', v)
            
            benefits = Benefits(df, self.benefit_col, self.increment_col)

            fit = benefits.curve_fit(self.benefit_func)
            
            benefit_dict["vehicle"].append(v)
            benefit_dict["fortificant"].append(str(f))
            benefit_dict["benefit_fit"].append(fit[0])
            benefit_dict['popt_benefit'].append(fit[1])
            benefit_dict['pcov_benefit'].append(fit[2])

        return pd.DataFrame(benefit_dict).set_index(["vehicle", "fortificant"])
    
    @property
    def func_len(self):
        return len(self.vehicle_dict)

    def data(self, nutrient):

        df = (
            self.costs(nutrient_choice=nutrient)
            .merge(
                self.benefits,
                left_index=True,
                right_index=True,
                how="outer",
                indicator=True,
            )
        )

        if not (df._merge == "both").all():
            print("[Note]: Merge was not perfect. check `_merge` column")
            if self.strict:
                raise Exception
        else:
            df = df.drop(["_merge"], axis=1)

        return df

    def _dataframe_to_func_sum(self, x, col, nutrient):
        
        funcs = self.data(nutrient = nutrient)[col].values
        
        apply_vectorized = np.vectorize(lambda f, x: f(x), otypes=[object])
        
        if len(x) != len(funcs):
            raise FunctionValueIncompatible(col)
    
        return apply_vectorized(funcs, x).sum()

    def optimize(self, nutrient, benefit_const, x0=None, basin=False, disp=True):
        
        benefit_const_func = lambda x, nutrient: benefit_const - self._dataframe_to_func_sum(x, 'benefit_fit', nutrient)
        
        bounds= [(0, None)]*self.func_len
        constraints = (
            {'type' : 'ineq', 'fun' : benefit_const_func, 'args' : (nutrient, ) }
        )
        
        if basin:
            res = basinhopping(
                self._dataframe_to_func_sum,
                x0,
                minimizer_kwargs= {
                    'method' : 'SLSQP',
                    'args' : ('cost_fit', nutrient),
                    'bounds' : bounds,
                    'constraints' : constraints
                },
                disp=disp
            )
        else:
            res = minimize(self._dataframe_to_func_sum, 
                        x0, 
                        method='SLSQP', 
                        args = ('cost_fit', nutrient),
                        bounds=bounds,
                        constraints=constraints,
                        options = {'disp' : disp})
        
        return res
        

# %%
if __name__ == "__main__":

    from example.example_data import df

    cdf = pd.read_csv("example/cost_data.csv")
    
    ## Trying with real data

    df_real = pd.read_csv("/home/lordflaron/Documents/minimod/examples/data/processed/example1.csv")

    df_real = (
        df_real
        .loc[lambda df: df['space'] == 'Cities']
        .loc[lambda df: df['time']==4]
        .loc[lambda df: df['intervention'].isin(['cube', 'maize', 'oil'])]
        .replace({'intervention' : {'oil' : 'Refined Oil',
                                    'cube' : 'Bouillon',
                                    'maize' : 'Maize Flour'}})
        .rename({'intervention' : 'vehicle'}, axis=1)
    )
    increment= np.linspace(0,500,100)

    func_benefits = lambda x, L, k, x0: L/(1 + np.exp(-k*(x - x0)))

    np.random.seed(1729)
    
    df_incremented = pd.DataFrame()
    
    for i, col in df_real.iterrows():
        
        noise = 0.2 * np.random.normal(size=increment.size)
        benefits = func_benefits(increment, col['benefit'], .3, 1) + noise
        
        df = pd.DataFrame({'increment' : increment,
                           'benefit' : benefits,
                           'vehicle' : col['vehicle']})
        df_incremented = df_incremented.append(df)

    vehicle_dict = {
        "Bouillon": [
            ("Iron", "Micronized ferric pyrophosphate"),
            ("Vitamin A", "Retinyl Palmitate- 250,000 IU/g (dry)"),
            ("Zinc", "Zinc Oxide"),
            ("Vitamin B12", "Vit. B-12 0.1% WS"),
            ("Folic Acid", "Folic Acid"),
        ],
        "Maize Flour": [("Iron", "Ferrous Fumarate"),
                        ('Folic Acid', 'Folic Acid')],
        'Refined Oil' : [('Vitamin A', 
                            "Retinyl Palmitate- 1.7 m IU/g (oil)")]
        
    }

    c = ContinuousOptimizer(
        vehicle_dict=vehicle_dict,
        benefit_data=df_incremented,
        cost_data=cdf,
        benefit_col="benefit",
        increment_col="increment",
        vehicle_col="vehicle",
        fortificant_col="compound",
        activity_col="fort_prop",
        overage_col="fort_over",
    )
    
    nutrient_choice = {"Bouillon": "Vitamin A", 
                      "Maize Flour": "iron",
                      'Refined Oil' : 'Vitamin A'}

    res = c.optimize(nutrient_choice, 80000, [1,1,1])
# %%

