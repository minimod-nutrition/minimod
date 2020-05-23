import mip
import pandas as pd

from minimod.utils.suppress_messages import suppress_stdout_stderr

from minimod.utils.exceptions import NoVars, NoObjective, NoConstraints



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
        self.model.opt_tol = 1e-07
        self.model.infeas_tol = 1e-07
        self.model.integer_tol = 1e-07

        # # allowable gap/ optca -> max_mip_gap_abs
        # # ratioGap/ optcr -> max_mip_gap

        self.model.max_mip_gap_abs = 0
        self.model.max_mip_gap = 0.1

        self.model.preprocess = 0

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

        base_constrs = self._df["mip_vars"].groupby([space, time]).agg(mip.xsum).values

        for constr in base_constrs:

            self.model += constr <= 1

    def _intervention_subset(self, intervention, subset_names=[]):

        subset_dict = {}

        for i in subset_names:
            subset_dict[i] = self._df.loc[
                lambda df: df.index.get_level_values(level=intervention).str.contains(
                    i, case=False
                )
            ]

            if subset_dict[i].empty:
                raise Exception(f"'{i}' not found in dataset.")

        return subset_dict

    def _all_constraint(
        self,
        intervention=None,
        group_index=None,
        subset_names=None,
        over=None,
        subset_list=slice(None)
    ):
        
        if subset_list is None:
            subset_list = slice(None)

        subset_dict = self._intervention_subset(intervention, subset_names=subset_names)

        all_indices = group_index + [over]

        for sub in subset_dict.keys():

            mip_vars_all = subset_dict[sub]["mip_vars"]

            mip_vars_subset = (
                subset_dict[sub]["mip_vars"]
                .reset_index()
                .set_index(over)
                .loc[subset_list]
                .reset_index()
                .set_index(all_indices)
            )

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
                        self.add_constraint(mip_var, cv, 'eq')

    def _all_space_constraint(
        self,
        intervention=None,
        time=None,
        subset_names=None,
        over=None,
        subset_list=slice(None),
    ):

        return self._all_constraint(
            intervention=intervention,
            group_index=[intervention, time],
            subset_names=subset_names,
            over=over,
            subset_list=subset_list,
        )

    def _all_time_constraint(
        self,
        intervention=None,
        space=None,
        subset_names=None,
        over=None,
        subset_list=slice(None),
    ):

        return self._all_constraint(
            intervention=intervention,
            group_index=[intervention, space],
            subset_names=subset_names,
            over=over,
            subset_list=subset_list,
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
        
    def add_objective(self, eq):
        
        self.model.objective = eq
        
    def add_constraint(self, eq, constraint, way = 'ge'):
        
        if way == 'ge':
            self.model += eq >= constraint
        elif way == 'le':
            self.model += eq <= constraint
        elif way == 'eq':
            self.model += eq == constraint
        

    def base_model_create(self, 
                          intervention, 
                          space, 
                          time, 
                          all_time=None, 
                          all_space=None, 
                          time_subset = None, 
                          space_subset = None):

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
                intervention=intervention,
                space=space,
                subset_names=all_time,
                over=time,
                subset_list=time_subset,
            )

        if all_space is not None:

            if intervention is None or time is None:
                raise Exception("One of the subset columns were not found")

            self._all_space_constraint(
                intervention=intervention,
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
                
    def process_results(self, benefit_col, cost_col):

        opt_df = self._df.copy(deep=True).assign(
            opt_vals=lambda df: df["mip_vars"].apply(lambda y: y.x),
            opt_benefit=lambda df: df[benefit_col] * df["opt_vals"],
            opt_costs=lambda df: df[cost_col] * df["opt_vals"],
        )[["opt_vals", "opt_benefit", "opt_costs"]]
        
        return opt_df
    
    def write(self, filename="model.lp"):
        self.model.write(filename)
        
    def get_model_results(self):
        
        return (self.model.objective_value, 
                self.model.objective_bound, 
                self.model.num_solutions, 
                self.model.num_cols, 
                self.model.num_rows, 
                self.model.num_int, 
                self.model.num_nz,
                self.status)
        
        