# %%
from typing import Callable
from benefits import Benefits
from costs import PremixCostCalculator
import pandas as pd
from data import CostDataProcessor
import re
import numpy as np
from exceptions import NonUniqueNutrient, NutrientNotFound, FunctionValueIncompatible
from scipy.optimize import minimize

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

        cost_dict = {"vehicle": [], "fortificant": [], "cost_fit": []}

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

            cost_dict["vehicle"].append(v)
            cost_dict["fortificant"].append(str(f))
            cost_dict["cost_fit"].append(
                costs.line_fit(nutrient, compound, self.cost_func)[0]
            )

        return pd.DataFrame(cost_dict).set_index(["vehicle", "fortificant"])

    @property
    def benefits(self):

        benefit_dict = {"vehicle": [], "fortificant": [], "benefit_fit": []}

        for v, f in self.vehicle_dict.items():

            df = (
                self.benefit_data.loc[lambda df: df[self.vehicle_col] == v]
                # .loc[lambda df: df[self.fortificant_col].isin(f)]
            )

            benefits = Benefits(df, self.benefit_col, self.increment_col)

            benefit_dict["vehicle"].append(v)
            benefit_dict["fortificant"].append(str(f))
            benefit_dict["benefit_fit"].append(benefits.curve_fit(self.benefit_func)[0])

        return pd.DataFrame(benefit_dict).set_index(["vehicle", "fortificant"])
    
    @property
    def func_len(self):
        return len(self.vehicle_dict)

    def data(self, nutrient=None):

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

    def optimize(self, nutrient, benefit_const, x0=None):
        
        benefit_const_func = lambda x, nutrient: benefit_const - self._dataframe_to_func_sum(x, 'benefit_fit', nutrient)
        
        bounds= [(0, None)]*self.func_len
        constraints = (
            {'type' : 'ineq', 'fun' : benefit_const_func, 'args' : (nutrient, ) }
        )
        
        res = minimize(self._dataframe_to_func_sum, 
                       x0, 
                       method='SLSQP', 
                       args = ('cost_fit', nutrient),
                       bounds=bounds,
                       constraints=constraints,
                       options = {'disp' : True})
        
        return res
        

# %%
if __name__ == "__main__":

    from example.example_data import df

    cdf = pd.read_csv("example/cost_data.csv")

    vehicle_dict = {
        "Bouillon": [
            ("Iron", "Micronized ferric pyrophosphate"),
            ("Vitamin A", "Retinyl Palmitate- 250,000 IU/g (dry)"),
            ("Zinc", "Zinc Oxide"),
            ("Vitamin B12", "Vit. B-12 0.1% WS"),
            ("Folic Acid", "Folic Acid"),
        ],
        "Maize Flour": [("Calcium", "Calcium Carbonate")],
    }

    c = ContinuousOptimizer(
        vehicle_dict=vehicle_dict,
        benefit_data=df,
        cost_data=cdf,
        benefit_col="benefits",
        increment_col="increment",
        vehicle_col="vehicle",
        fortificant_col="compound",
        activity_col="fort_prop",
        overage_col="fort_over",
    )

    res = c.optimize({"Bouillon": "zinc", "Maize Flour": "calcium"}, 10, [3,5])
# %%
