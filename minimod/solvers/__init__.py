# Imports for local packages
from minimod.utils.exceptions import (
    MissingData,
    NotPandasDataframe,
    MissingOptimizationMethod,
    NoVars,
    NoConstraints,
    NoObjective,
)

from minimod.version import __version__

from minimod.utils.summary import Summary
from minimod.utils.plotting import Plotter

import pandas as pd
import numpy as np
import mip


class BaseSolver:
    """The BaseSolver instance from which the CostSolver and BenefitSolver classes are made.
    
    Raises:
        MissingData: Data not defined
        NotPandasDataframe: Data that is input is not a pandas dataframe
        NoVars: Variables not defined
        NoConstraints: No Constraints Defined
        NoObjective: No Objective Function Defined
    
    Returns:
        BaseSolver Instance -- An instance of BaseSolver that starts a `mip` model instance 
    """

    def __init__(
        self,
        interest_rate_cost=0.0,  # Discount factor for costs
        interest_rate_benefit=0.03,  # Discount factor for benefits
        va_weight=1.0,  # VA Weight
        sense=None,  # MIP optimization type (maximization or minimization)
        solver_name=mip.CBC,  # Solver for MIP to use
    ):

        self.interest_rate_cost = interest_rate_cost
        self.interest_rate_benefit = interest_rate_benefit
        self.va_weight = va_weight
        self.discount_costs = 1 / (1 + self.interest_rate_cost)
        self.discount_benefits = 1 / (1 + self.interest_rate_benefit)

        if sense is not None:
            self.sense = sense
        else:
            raise Exception("No Optimization Method was specified")

        if solver_name is not None:

            self.solver_name = solver_name
        else:
            raise Exception("No Solver name was specified.")

        ## Tell the fitter whether to maximize or minimize
        self.model = mip.Model(sense=self.sense, solver_name=solver_name)

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

        print(
            f"""
              MiniMod Nutrition Intervention Tool
              Optimization Method: {str(self.sense)}
              Version: {__version__}
              Solver: {str(self.solver_name)}
              
              """
        )

    def _is_dataframe(self, data):

        if not isinstance(data, pd.DataFrame):
            raise NotPandasDataframe(
                "[Error]: Input data is not a dataframe. Please input a dataframe."
            )

    def _process_data(
        self,
        data=None,
        intervention="intervention",
        space="space",
        time="time",
        benefits="benefits",
        costs="costs",
    ):
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
        if data is None:
            raise MissingData("No data specified.")

        # Check if dataframe
        self._is_dataframe(data)

        df = (
            data.reset_index()
            .assign(
                time_col=lambda df: df[time].astype(int),
                time_rank=lambda df: (
                    df[time].rank(numeric_only=True, method="dense") - 1
                ).astype(int),
                time_discount_costs=lambda df: self.discount_costs ** df["time_rank"],
                time_discount_benefits=lambda df: self.discount_benefits
                ** df["time_rank"],
                discounted_costs=lambda df: df["time_discount_costs"] * df[costs],
                discounted_benefits=lambda df: df["time_discount_benefits"]
                * df[benefits],
            )
            .set_index([intervention, space, time])
            .sort_index(level=(intervention, space, time))
        )

        return df

    def _constraint(self):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """
        pass

    def _objective(self):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """
        pass

    def _discounted_sum_all(self, data):

        eq = mip.xsum(
            self._df["mip_vars"].loc[k, j, t] * data[k, j, t]
            for (k, j, t) in self._df.index.values
        )

        return eq

    def _stringify_tuple(self, tup):
        
        strings= [str(x) for x in tup]
        
        stringified = ''.join(strings)
        
        return stringified

    def _model_var_create(self):

        self._df["mip_vars"] = self._df.apply(
            lambda x: self.model.add_var(var_type=mip.BINARY, name= f"x_{self._stringify_tuple(x.name)}"), axis=1
        )

    def _base_constraint(self):

        base_constrs = (
            self._df["mip_vars"].groupby(["space", "time"]).agg(mip.xsum).values
        )

        for constr in base_constrs:

            self.model += constr <= 1

    def _intervention_subset(self, intervention, subset_names=[]):

        subset_dict = {}

        for i in subset_names:
            subset_dict[i] = self._df.loc[
                lambda df: df.index.get_level_values(level=intervention).str.contains(i)
            ]

        return subset_dict

    def _all_constraint(
        self,
        intervention=None,
        group_index=None,
        subset_names=None,
        over = None,
        subset_list=slice(None),
    ):

        subset_dict = self._intervention_subset(intervention, subset_names=subset_names)
        
        all_indices = group_index + [over]

        for sub in subset_dict.keys():
            
            mip_vars_all = subset_dict[sub]["mip_vars"]

            mip_vars_subset = (subset_dict[sub]["mip_vars"]
                            .reset_index()
                            .set_index(over)
                            .loc[subset_list]
                            .reset_index()
                            .set_index(all_indices)
                            )

            # Get mip_vars from each subset
            

            # Now we group by the variables we aren't doing the constraints for
            grouped_mip = (
                mip_vars_subset.groupby(group_index)
                .agg(lambda x: list(x))
                .rename({"mip_vars": "constraining_var"}, axis="columns")
            )

            grouped_subset = (
                mip_vars_all.reset_index()
                .set_index(group_index)
                .merge(grouped_mip, left_index=True, right_index=True)[
                    ["mip_vars", "constraining_var"]
                ]
            )

            for _, mip_var, constraining_var in grouped_subset.itertuples():

                for cv in constraining_var:
                    if str(cv) != str(mip_var):
                        self.model += mip_var == cv

    def _all_space_constraint(
        self, intervention=None, time=None, subset_names=None, over = None, subset_list=slice(None)
    ):

        return self._all_constraint(
            intervention=intervention,
            group_index=[intervention, time],
            subset_names=subset_names,
            over = over,
            subset_list=subset_list
        )

    def _all_time_constraint(
        self, intervention=None, space=None, subset_names=None, over = None, subset_list=slice(None)
    ):

        return self._all_constraint(
            intervention=intervention,
            group_index=[intervention, space],
            subset_names=subset_names,
            over = over,
            subset_list=subset_list
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

    def base_model_create(self, all_time=None, all_space=None, **kwargs):

        ## Now we create the choice variable, x, which is binary and is the size of the dataset.

        ## In this case, it should just be a column vector with the rows equal to the data:

        self._model_var_create()

        ## Now write the objective function
        self._objective()

        ## First add base constraint, which only allows one intervention per time and space
        self._base_constraint()

        ## Add all_space or all_time constraints if necessary
        if all_time is not None:

            intervention = kwargs.get("intervention")
            space = kwargs.get("space")
            time = kwargs.get('time')
            time_subset = kwargs.get("time_subset")

            if intervention is None or space is None:
                raise Exception("One of the subset columns were not found")

            self._all_time_constraint(
                intervention=intervention,
                space=space,
                subset_names=all_time,
                over = time,
                subset_list=time_subset,
            )

        if all_space is not None:

            intervention = kwargs.get("intervention")
            time = kwargs.get("time")
            space = kwargs.get('space')
            space_subset = kwargs.get("space_subset")

            if intervention is None or time is None:
                raise Exception("One of the subset columns were not found")

            self._all_space_constraint(
                intervention=intervention,
                time=time,
                subset_names=all_space,
                over = space,
                subset_list=space_subset,
            )

        ## Now add solver-specific constraints to the model
        self._constraint()

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
        elif self.status == mip.OptimizationStatus.INFEASIBLE:
            print("[Warning]: Infeasible Solution Found")

    def process_results(self, benefits, costs):

        self.opt_df = self._df.copy(deep=True).assign(
            opt_vals=lambda df: df["mip_vars"].apply(lambda y: y.x),
            opt_benefit=lambda df: df[benefits] * df["opt_vals"],
            opt_costs=lambda df: df[costs] * df["opt_vals"],
        )[["opt_vals", "opt_benefit", "opt_costs"]]

    def _fit(
        self,
        data=None,
        intervention="intervention",
        space="space",
        time="time",
        benefits="benefit",
        costs="costs",
        all_space=None,
        all_time=None,
        space_subset=slice(None),
        time_subset=slice(None),
        clear=False,
        **kwargs,
    ):
        """Fits the model that is created above using the sense provided by `self.sense`.
        
        Keyword Arguments:
            data {pandas.DataFrame} -- A pandas dataframe (default: {None})
            intervention {str} -- the column denoting the interventions (default: {"intervention"})
            space {str} -- column denoting space/region (default: {"space"})
            time {str} -- column denoting time period (default: {"time"})
            benefits {str} -- column denoting benefits/effective coverage (default: {"benefit"})
            costs {str} -- column denoting costs (default: {"costs"})
            clear {bool} -- Clears the model (default: {False})
        """

        self._benefits = benefits
        self._intervention = intervention
        self._space = space
        self._time = time

        # Process Data
        print("[Note]: Processing Data...")
        self._df = self._process_data(
            data=data,
            intervention=intervention,
            space=space,
            time=time,
            benefits=benefits,
            costs=costs,
        )

        print("[Note]: Creating Base Model with constraints")
        self.base_model_create(
            all_space=all_space,
            all_time=all_time,
            intervention=intervention,
            space=space,
            time=time,
            space_subset=space_subset,
            time_subset=time_subset,
        )
        print("[Note]: Optimizing...")
        self.optimize()
        self.process_results(benefits, costs)
        if clear:
            self.clear()

    def clear(self):
        self.model.clear()

    def write(self, filename="model.lp"):
        self.model.write(filename)

    def report(self):

        s = Summary(self)

        return s._report()
    
    def plot_time(self, 
                  fig = None, 
                  ax = None,
                  save = None):
        
        p = Plotter(self)
        
        return p._plot_lines(to_plot = ['opt_benefit', 'opt_costs'],
                             title= "Optima over Time",
                             xlabel = 'Time',
                             ylabel = 'Coverage',
                             twin =True,
                             twin_ylabel= "Currency",
                             save = save,
                             legend = ['Optimal Coverage',
                                       'Optimal Costs'],
                             figure=fig,
                             axis=ax)

    def plot_opt_val_hist(self, 
                          fig = None, 
                          ax = None, 
                          save = None):
        
        p = Plotter(self)
        
        return p._plot_hist(to_plot = 'opt_vals',
                            title = "Optimal Choices",
                            xlabel = "Time",
                            ylabel= "",
                            figure = fig,
                            axis = ax,
                            save = save)
        
    def plot_chloropleth(self,
                         intervention = slice(None),
                         time = None,
                         optimum_interest = 'b',
                         map_df = None,
                         merge_key = None,
                         ax = None,
                         save = None):
        
        p = Plotter(self)
                
        if optimum_interest == 'b':
            opt = 'opt_benefit'
        elif optimum_interest == 'c':
            opt = 'opt_costs'
        elif optimum_interest == 'v':
            opt = 'opt_vals'
        else:
            raise Exception("Not one of the allowed variables for map plotting. Try again.")
        
        if time is not None and len(time) == 1:                
                return p._plot_chloropleth(intervention = intervention,
                                        time = time,
                                        optimum_interest = opt,
                                        map_df = map_df,
                                        merge_key = merge_key,
                                        title = None,
                                        ax= ax,
                                        save = save)
        else:            
            return p._plot_multi_chloropleth(t= time,
                                             intervention=intervention,
                                             optimum_interest=opt,
                                             map_df=map_df,
                                             merge_key = merge_key,
                                             save = save)
