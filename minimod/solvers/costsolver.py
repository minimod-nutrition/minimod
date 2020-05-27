from minimod.base.basesolver import BaseSolver
from minimod.utils.exceptions import NotPandasDataframe, MissingColumn
from minimod.utils.summary import OptimizationSummary

from minimod.base.bau_constraint import BAUConstraintCreator


import pandas as pd
import mip
import numpy as np


class CostSolver(BaseSolver):
    def __init__(self, minimum_benefit=None, **kwargs):

        super().__init__(sense=mip.MINIMIZE, **kwargs)

        if isinstance(minimum_benefit, float) or isinstance(minimum_benefit, int):
            self.minimum_benefit = minimum_benefit
        elif isinstance(minimum_benefit, str):
            # Get sum of benefits for interventions
            self.minimum_benefit = self.bau.create_bau_constraint(
                self._df, minimum_benefit, "discounted_benefits"
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

        # Add objective and constraint
        self.model.add_objective(self._objective())
        self.model.add_constraint(self._constraint(), self.minimum_benefit)

    def _objective(self):

        cost = self._df["discounted_costs"]

        # Discounted costs
        return self._discounted_sum_all(cost)

    def _constraint(self):

        benefit = self._df["discounted_benefits"]

        ## Make benefits constraint be at least as large as the one from the minimum benefit intervention
        return self._discounted_sum_all(benefit)

    def fit(self, **kwargs):
        return self._fit(**kwargs)

    def report(self):

        s = OptimizationSummary(self)

        super().report()

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

