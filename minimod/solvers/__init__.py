# Imports for local packages
from minimod.utils.exceptions import (
    MissingData,
    NotPandasDataframe,
    MissingOptimizationMethod,
    NoVars,
    NoConstraints,
    NoObjective,
)

from minimod.utils.summary import Summary

import pandas as pd
import numpy as np
import mip


class BaseSolver:
    """This class loads in data and solves the benefit maximization problem using the `mip` package
    
    
    Returns:
        BenefitSolverInstance -- An instance of the Benefit Solver class that includes methods for solving the benefit maximization problem
    """

    def __init__(
        self,
        data=None,
        intervention_col="intervention",
        space_col="space",
        time_col="time",
        benefit_col="benefit",
        cost_col="costs",
        interest_rate_cost=0.0,  # Discount factor for costs
        interest_rate_benefit=0.03,
        va_weight=1.0,  # VA Weight
    ):

        self.interest_rate_cost = interest_rate_cost
        self.interest_rate_benefit = interest_rate_benefit
        self.va_weight = va_weight
        self.discount_costs = 1 / (1 + self.interest_rate_cost)
        self.discount_benefits = 1 / (1 + self.interest_rate_benefit)

        if data is not None:
            self._data = data
        else:
            raise MissingData("No data specified.")

        self._intervention_col = intervention_col
        self._space_col = space_col
        self._time_col = time_col

        self._benefit_col = benefit_col
        self._cost_col = cost_col

        self._all_columns_list = [intervention_col, space_col, time_col]

        self._df = self._process_data()

    def _is_dataframe(self):

        if not isinstance(self._data, pd.DataFrame):
            raise NotPandasDataframe(
                "[Error]: Input data is not a dataframe. Please input a dataframe."
            )

    def _process_data(self):
        """This method processes the data and gets it ready to be used in the problem
            
        Arguments:
        data {pandas dataframe} -- A pandas dataframe with columns for each time period and a column for regions or whatever spatial dimension is used. The rows for each time period should give the benefits of each intervention at time t, and space j
        
        |k     | j   |t   | benefits   | costs |
        |------|-----|----|------------|-------|
        |maize |north|0   | 100        | 10    |
        |maize |south|0   | 50         | 20    |
        |maize |east |0   | 30         |30     |
        |maize |west |0   | 20         |40     |
        
    Raises:
        MissingColumn: If a column is not included, it raises the missing column exception
        """

        ## First do some sanity checks
        self._is_dataframe()

        df = (
            self._data.reset_index()
            .assign(
                time_col=lambda df: df[self._time_col].astype(int),
                time_rank=lambda df: (
                    df[self._time_col].rank(numeric_only=True, method="dense") - 1
                ).astype(int),
                time_discount_costs=lambda df: self.discount_costs ** df["time_rank"],
                time_discount_benefits=lambda df: self.discount_benefits
                ** df["time_rank"],
                intervention_cat=lambda df: df[self._intervention_col]
                .astype("category")
                .cat.codes,
                space_cat=lambda df: df[self._space_col].astype("category").cat.codes,
            )
            .set_index(["intervention_cat", "space_cat", "time_rank"])
            .sort_index(level=("intervention_cat", "space_cat", "time_rank"))
        )

        ## Get different lengths for each index
        self._K, self._J, self._T = df.index.levshape

        if len(df["time_discount_costs"].unique()) == 1:
            self._time_discount_costs = np.repeat(1, self._T)
        else:
            self._time_discount_costs = df["time_discount_costs"].unique()

        if len(df["time_discount_benefits"].unique()) == 1:
            self._time_discount_benefits = np.repeat(1, self._T)
        else:
            self._time_discount_benefits = df["time_discount_benefits"].unique()

        return df

    def _constraint(self, model, x):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """
        pass

    def _objective(self, model, x):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """
        pass

    def _model_create(self, sense, solver_name=mip.CBC):

        self._sense = sense

        print(
            f"""Loading MIP Model with:
              Solver = {str(solver_name)}
              Method = {self._sense},
              """
        )

        ## Tell the fitter whether to maximize or minimize
        self.model = mip.Model(sense=sense, solver_name=solver_name)

        ## set tolerances based on GAMS tolerances
        # primal tol -> infeas
        # dual tol -> opt tol
        # integer  tol -> integer_tol
        self.model.opt_tol = 1e-07
        self.model.infeas_tol = 1e-07
        self.model.integer_tol = 1e-07

        # # allowable gap/ optca -> max_mip_gap_abs
        # # ratioGap/ optcr -> max_mip_gap

        self.model.max_mip_gap_abs = 0
        self.model.max_mip_gap = 0.1

        self.model.preprocess = 0

    def _model_var_create(self):

        # x = {
        #     (k, j, t): self.model.add_var(name=f"{k} {j} {t}", var_type=mip.BINARY)
        #     for k in range(self._K)
        #     for j in range(self._J)
        #     for t in range(self._T)
        # }
        
        x = {
            (k, j, t): self.model.add_var(name=f"{k} {j} {t}", var_type=mip.BINARY)
            for (k,j,t) in self._df.index.values

        }

        return x

    def _base_constraint(self, x):

        for j in range(self._J):
            for t in range(self._T):
                self.model += (
                    mip.xsum(x[k, j, t] for k in range(self._K)) <= 1,
                    f"onesx {j} {t}"
                )

    def get_constraint(self, name=None):
        """Returns a constraint by its name. If no name is specified, returns all constraints
        
        Arguments:
            name {str} -- a string corresponding to the name of the constraint
        
        Returns:
            mip.Constr -- A `mip` constraint object
        """

        if name is None:
            return self.model.constrs

        else:
            return self.model.constr_by_name(name)

    def base_model_create(self, sense):

        self._model_create(sense, solver_name=mip.CBC)

        ## Now we create the choice variable, x, which is binary and is the size of the dataset.

        ## In this case, it should just be a column vector with the rows equal to the data:

        x = self._model_var_create()

        ## Now write the objective function
        self._objective(self.model, x)

        ## First add base constraint, which only allows one intervention per time and space
        self._base_constraint(x)

        ## Now add constraints to the model
        self._constraint(self.model, x)

    def optimize(self, **kwargs):

        self.status = None

        if self.model.num_cols == 0:
            raise NoVars("No Variables added to the model")
        if self.model.num_rows == 0:
            raise NoConstraints("No constraints added to the model.")
        try:
            self.model.objective
        except Exception:
            raise NoObjective("No Objective added to the model")

        # Now, allow for arguments to the optimize function to be given:

        max_seconds = kwargs.pop("max_seconds", mip.INF)  
        max_nodes = kwargs.pop("max_nodes", mip.INF)
        max_solutions = kwargs.pop("max_solutions", mip.INF)

        self.status = self.model.optimize(max_seconds, max_nodes, max_solutions)

        if self.status == mip.OptimizationStatus.OPTIMAL:
            print("[Note]: Optimal Solution Found")
        elif self.status == mip.OptimizationStatus.FEASIBLE:
            print("[Note]: Feasible Solution Found. This may not be optimal.")
        elif self.status == mip.OptimizationStatus.NO_SOLUTION_FOUND:
            print("[Warning]: No Solution Found")

    def process_results(self):

        ## First we construct the dataframe based on the name given for the variable `x[0,0,0]` for example, and its value.

        opt_vars = {}
        opt_vars["intervention_cat"] = []
        opt_vars["space_cat"] = []
        opt_vars["time_rank"] = []
        opt_vars["opt_vals"] = []

        for v in self.model.vars:
            v_cols = v.name.split(" ")
            opt_vars["intervention_cat"].append(int(v_cols[0]))
            opt_vars["space_cat"].append(int(v_cols[1]))
            opt_vars["time_rank"].append(int(v_cols[2]))

            opt_vars["opt_vals"].append(v.x)

        opt_var_df = pd.DataFrame(opt_vars).set_index(
            ["intervention_cat", "space_cat", "time_rank"]
        )

        df_copy_aux = self._df.copy(deep=True)

        df_copy = df_copy_aux.merge(opt_var_df, left_index=True, right_index=True)

        df_copy["opt_benefit"] = df_copy[self._benefit_col] * df_copy["opt_vals"]

        df_copy["opt_costs"] = df_copy[self._cost_col] * df_copy["opt_vals"]

        self.objective_value = self.model.objective_value
        self.objective_bound = self.model.objective_bound
        self.opt_df = df_copy.reset_index().set_index(
            [self._intervention_col, self._space_col, self._time_col]
        )[["opt_vals", "opt_benefit", "opt_costs"]]

    def _fit(self, sense, extra_const=None, clear=False, **kwargs):

        self.base_model_create(sense)
        if extra_const is not None:
            self.model += extra_const(**kwargs)
        self.optimize()
        self.process_results()
        if clear:
            self.clear()

    def clear(self):
        self.model.clear()
        
    def write(self, filename = 'model.mps'):
        self.model.write(filename)
        

    def report(self):

        s = Summary(self)

        return s._report()
