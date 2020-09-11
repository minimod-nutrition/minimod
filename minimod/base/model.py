import mip
import pandas as pd

from minimod.utils.suppress_messages import suppress_stdout_stderr

from minimod.utils.exceptions import NoVars, NoObjective, NoConstraints
from itertools import combinations, permutations


class Model:
    def __init__(self, data, sense, solver_name, show_output):
        """A class that instantiates a `mip` model. 

        :param data: The input dataframe that includes benefit/cost data
        :type data: pandas.DataFrame
        :param sense: Whether the model should minimize or maximize
        :type sense: mip.MAXIMIZE or mip.MINIMIZE
        :param solver_name: The solver type (CBC or some other mip solver   )
        :type solver_name: mip.CBC
        :param show_output: Whether to show output of model construction
        :type show_output: bool
        """

        ## Tell the fitter whether to maximize or minimize
        self.model = mip.Model(sense=sense, solver_name=solver_name)

        self._df = data

        self.show_output = show_output

        if self.show_output:
            self.model.verbose = 1
        else:
            self.model.verbose = 0
        ## set tolerances based on GAMS tolerances
        # primal tol -> infeas
        # dual tol -> opt tol
        # integer  tol -> integer_tol
        self.model.opt_tol = 1e-10
        self.model.infeas_tol = 1e-10
        self.model.integer_tol = 1e-06
        self.model.seed = 0
        # self.model.clique = 0

        # # # # allowable gap/ optca -> max_mip_gap_abs
        # # # # ratioGap/ optcr -> max_mip_gap

        self.model.max_mip_gap_abs = 0
        self.model.max_mip_gap = 0.1

        self.model.preprocess = 0
        self.model.lp_method = -1
        self.cut_passes = 1

    def _stringify_tuple(self, tup):

        strings = [str(x) for x in tup]

        stringified = "".join(strings)

        return stringified

    def _model_var_create(self):

        self._df["mip_vars"] = self._df.apply(
            lambda x: self.model.add_var(
                var_type=mip.BINARY, name=f"x_{self._stringify_tuple(x.name)}"
            ),
            axis=1,
        )

    def _base_constraint(self, space, time):
        
        grouped_df = self._df["mip_vars"].groupby([space, time]).agg(mip.xsum)

        base_constrs = grouped_df.values

        # Get constraint name
        names = list(
            map(
                self._stringify_tuple,
                grouped_df.index.to_list()
            )
        )

        for constr, name in zip(base_constrs, names):

            self.model += constr <= 1, "ones_" + name

    def _intervention_subset(self, intervention, strict, subset_names=[]):

        subset_dict = {}

        for i in subset_names:

            if strict:
                subset_dict[i[0]] = self._df.loc[
                    lambda df: df.index.get_level_values(level=intervention).isin(i)
                ]

                if subset_dict[i[0]].empty:
                    raise Exception(f"'{i[0]}' not found in dataset.")

            else:
                subset_dict[i] = self._df.loc[
                    lambda df: df.index.get_level_values(
                        level=intervention
                    ).str.contains(i, case=False)
                ]

                if subset_dict[i].empty:
                    raise Exception(f"'{i}' not found in dataset.")

        return subset_dict

    def _all_constraint(
        self,
        strict,
        intervention=None,
        space=None,
        time=None,
        subset_names=None,
        over=None,
        subset_list=None,
    ):

        subset_dict = self._intervention_subset(
            intervention=intervention, strict=strict, subset_names=subset_names
        )
        for sub in subset_dict.keys():

            mip_vars_grouped_sum = (
                subset_dict[sub].groupby([space, time])["mip_vars"].agg(mip.xsum)
            )

            if over == time:
                slicer = space
            elif over == space:
                slicer = time

            unstacked = mip_vars_grouped_sum.unstack(level=slicer)

            if subset_list is None:
                subset_list = unstacked.index

            # get combinations of different choices
            constraint_combinations = permutations(unstacked.index.tolist(), 2)

            constraint_list = [
                (i, j) for (i, j) in constraint_combinations if i in subset_list
            ]

            for col in unstacked.columns:
                for (comb1, comb2) in constraint_list:
                    self.add_constraint(
                        unstacked[col].loc[comb1], unstacked[col].loc[comb2], 
                        "eq",
                        name = str(sub) + "_" + str(col) + "_" + str(comb1) + "_" + str(comb2)
                    )

    def _all_space_constraint(
        self,
        strict,
        intervention=None,
        space=None,
        time=None,
        subset_names=None,
        over=None,
        subset_list=None,
    ):

        return self._all_constraint(
            strict,
            intervention=intervention,
            space=space,
            time=time,
            subset_names=subset_names,
            over=over,
            subset_list=subset_list,
        )

    def _all_time_constraint(
        self,
        strict,
        intervention=None,
        space=None,
        time=None,
        subset_names=None,
        over=None,
        subset_list=None,
    ):

        return self._all_constraint(
            strict,
            intervention=intervention,
            space=space,
            time=time,
            subset_names=subset_names,
            over=over,
            subset_list=subset_list,
        )

    def get_equation(self, name=None, show=True):
        """Returns a constraint by its name. If no name is specified, returns all constraints
        
        Arguments:
            name {str} -- a string corresponding to the name of the constraint
        
        Returns:
            mip.Constr -- A `mip` constraint object
        """

        if name is None:
            return self.model.constrs
        elif name == 'objective':
            if show:
                return str(self.model.objective)
            else:
                return self.model.objective
        else:
            if show:
                return str(self.model.constr_by_name(name))
            else:
                return self.model.constr_by_name(name)

    def add_objective(self, eq):

        self.model.objective = eq

    def add_constraint(self, eq, constraint, way="ge", name=""):
        
        if isinstance(constraint, pd.Series):
            # Merge equation with constraint
            df = eq.merge(constraint, left_index = True, right_index= True)
            
            for i, ee, c in df.itertuples():
                if way == "ge":
                    self.model += ee >= c, name
                elif way == "le":
                    self.model += ee <= c, name
                elif way == "eq":
                    self.model += ee == c, name
                
            
        else:
            if way == "ge":
                self.model += eq >= constraint, name
            elif way == "le":
                self.model += eq <= constraint, name
            elif way == "eq":
                self.model += eq == constraint, name

    def base_model_create(
        self,
        intervention,
        space,
        time,
        all_time=None,
        all_space=None,
        time_subset=None,
        space_subset=None,
        strict=False,
    ):

        ## Now we create the choice variable, x, which is binary and is the size of the dataset.
        ## In this case, it should just be a column vector with the rows equal to the data:

        self._model_var_create()

        ## First add base constraint, which only allows one intervention per time and space
        self._base_constraint(space, time)

        ## Add all_space or all_time constraints if necessary
        if all_time is not None:

            if intervention is None or space is None:
                raise Exception("One of the subset columns were not found")

            self._all_time_constraint(
                strict,
                intervention=intervention,
                space=space,
                time=time,
                subset_names=all_time,
                over=time,
                subset_list=time_subset,
            )

        if all_space is not None:

            if intervention is None or time is None:
                raise Exception("One of the subset columns were not found")

            self._all_space_constraint(
                strict,
                intervention=intervention,
                space=space,
                time=time,
                subset_names=all_space,
                over=space,
                subset_list=space_subset,
            )

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

        if self.show_output:
            self.status = self.model.optimize(max_seconds, max_nodes, max_solutions)
        else:
            with suppress_stdout_stderr():
                self.status = self.model.optimize(max_seconds, max_nodes, max_solutions)
        if self.show_output:
            if self.status == mip.OptimizationStatus.OPTIMAL:
                print("[Note]: Optimal Solution Found")
            elif self.status == mip.OptimizationStatus.FEASIBLE:
                print("[Note]: Feasible Solution Found. This may not be optimal.")
            elif self.status == mip.OptimizationStatus.NO_SOLUTION_FOUND:
                print("[Warning]: No Solution Found")
            elif self.status == mip.OptimizationStatus.INFEASIBLE:
                print("[Warning]: Infeasible Solution Found")

    def process_results(self, benefit_col, cost_col, intervention_col, space_col):

        opt_df = self._df.copy(deep=True).assign(
            opt_vals=lambda df: df["mip_vars"].apply(lambda y: y.x),
            opt_benefit=lambda df: df[benefit_col] * df["opt_vals"],
            opt_costs=lambda df: df[cost_col] * df["opt_vals"],
            opt_costs_discounted=lambda df: df["discounted_costs"] * df["opt_vals"],
            opt_benefit_discounted=lambda df: df["discounted_benefits"]* df["opt_vals"],
            cumulative_discounted_benefits = lambda df: (df
                                                         .groupby([space_col])['opt_benefit_discounted']
                                                         .transform('cumsum')),
            cumulative_discounted_costs = lambda df: (df
                                                         .groupby([space_col])['opt_costs_discounted']
                                                         .transform('cumsum')),
            cumulative_benefits = lambda df: (df
                                                         .groupby([space_col])['opt_benefit']
                                                         .transform('cumsum')),
            cumulative_costs = lambda df: (df
                                                         .groupby([space_col])['opt_costs']
                                                         .transform('cumsum'))
        )[
            [
                "opt_vals",
                "opt_benefit",
                "opt_costs",
                "opt_costs_discounted",
                "opt_benefit_discounted",
                "cumulative_discounted_benefits",
                "cumulative_discounted_costs",
                "cumulative_benefits",
                "cumulative_costs"
            ]
        ]

        return opt_df

    def write(self, filename="model.lp"):
        self.model.write(filename)

    def get_model_results(self):

        return (
            self.model.objective_value,
            self.model.objective_values,
            self.model.objective_bound,
            self.model.num_solutions,
            self.model.num_cols,
            self.model.num_rows,
            self.model.num_int,
            self.model.num_nz,
            self.status,
        )

