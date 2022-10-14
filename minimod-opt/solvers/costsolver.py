from minimod.base.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import OptimizationSummary

from minimod.base.bau_constraint import BAUConstraintCreator
from minimod.base.model import Model


import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):  
    def __init__(self,         
                 all_time=None, 
                 all_space=None, 
                 time_subset = None, 
                 space_subset = None,
                 strict = False,
                 main_constraint_over = None, 
                 minimum_benefit =None,
                 drop_bau = False,
                 **kwargs):

        super().__init__(sense=mip.MINIMIZE, **kwargs)
        
        self.bau = BAUConstraintCreator()

        if isinstance(minimum_benefit, float) or isinstance(minimum_benefit, int):
            self.minimum_benefit = minimum_benefit
            over=None
        elif isinstance(minimum_benefit, str):
            # Get sum of benefits for interventions
            if main_constraint_over == 'space':
                over = self.space_col
            elif main_constraint_over == 'time':
                over = self.time_col
            elif main_constraint_over == 'both':
                over = [self.space_col, self.time_col]
            elif main_constraint_over is None:
                over = None
            self.minimum_benefit = self.bau.create_bau_constraint(
                self._df, minimum_benefit, "discounted_benefits", over
            )
        
            self.bau_df = self.bau.bau_df(
                self._df,
                minimum_benefit,
                [
                    self.benefit_col,
                    self.cost_col,
                    "discounted_benefits",
                    "discounted_costs",
                ],
            )
            
            summed_bau_df = self.bau_df.sum()
            
            self.cost_per_benefit = summed_bau_df[self.cost_col]/summed_bau_df[self.benefit_col]
            
            if drop_bau:
                self._df = self._df.drop(minimum_benefit, level=self.intervention_col)
                   
        self.model = Model(data = self._df, sense = self.sense, solver_name=self.solver_name, show_output=self.show_output)
        
        ## Create base model
        self.model.base_model_create(self.intervention_col, 
                                    self.space_col, 
                                    self.time_col, 
                                    all_time=all_time, 
                                    all_space=all_space, 
                                    time_subset = time_subset, 
                                    space_subset = space_subset,
                                    strict = strict)

        # Add objective and constraint
        self.model.add_objective(self._objective())
        self.model.add_constraint(self._constraint(over = over), self.minimum_benefit, name = "base_constraint")
        

    def _objective(self):

        cost = "discounted_costs"

        # Discounted costs
        return self._discounted_sum_all(col_name = cost)

    def _constraint(self, over = None):

        benefit = "discounted_benefits"
        
        if over is not None:
            return self._discounted_sum_over(benefit, over = over)

        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        return self._discounted_sum_all(benefit)

    def fit(self, sol_num=None, **kwargs):
        return self._fit(**kwargs)
    
    def report(self, sol_num = None, intervention_groups = False, quiet=False):

        s = OptimizationSummary(self)

        super().report(sol_num=sol_num, quiet=quiet)
        
        if quiet:
            return
        if self.num_solutions == 1:
            obj_values = self.objective_value
        elif self.num_solutions > 1:
            obj_values = self.objective_values

        sum_costs = self.opt_df["opt_costs_discounted"].sum()
        sum_benefits = self.opt_df["opt_benefit_discounted"].sum()

        results = [
            ("Minimum Benefit", self.minimum_benefit),
            ("Objective Bounds", obj_values),
            ("Total Cost", sum_costs),
            ("Total " + self.benefit_title, sum_benefits),
        ]

        s.print_generic(results)
        s.print_ratio(name="Cost per Benefit", num=sum_costs, denom=sum_benefits)

        s.print_grouper(
            name="Total Cost and Benefits over Time",
            data=self.opt_df[["opt_vals", "opt_benefit", "opt_costs"]],
            style="markdown",
        )
        
        print()
        print("Optimal Interventions")
        print()
        opt_chosen = self.opt_df.loc[lambda df: df['opt_vals']>0]['opt_vals'].unstack(level='time').fillna(0)
        
        s.print_df(opt_chosen)
        
        if isinstance(intervention_groups, dict):
            opt_chosen_reset = opt_chosen.reset_index()
            for intervention in intervention_groups:
                opt_chosen_reset[intervention_groups[intervention]] \
                    = opt_chosen_reset[self.intervention_col].str.contains(intervention).astype(int)
            
            intervention_grouper_df = (
                opt_chosen_reset
                .drop(columns = [self.intervention_col, 'opt_vals'])
                .set_index([self.space_col, self.time_col])
                .stack()
                .unstack(level=self.time_col)
                )

            s.print_df(intervention_grouper_df)
                
            # Use for later
            # a = intervention_grouper_df.reset_index(level='region')[list(range(1,11))].mul(intervention_grouper_df.reset_index(level='region')['region'], axis='index')
            # b = a.groupby(a.index).agg(list)

        return opt_chosen
        
        
        

