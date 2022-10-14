import mip
import pandas as pd

from minimod.utils.suppress_messages import suppress_stdout_stderr

from minimod.utils.exceptions import NoVars, NoObjective, NoConstraints
from itertools import combinations, permutations


class Model:


    def __init__(self, data:pd.DataFrame, sense:str, solver_name:str, show_output:bool):
        """A class that instantiates a `mip` model.

        Args:
            data (pd.DataFrame): The input dataframe that includes benefit/cost data
            sense (str): Whether the model should minimize (MINIMIZE) or maximize (MAXIMIZE)
            solver_name (str): The solver type (CBC or some other mip solver)
            show_output (bool):  Whether to show output of model construction
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

    def _stringify_tuple(self, tup:tuple)->str:
        """This function converts all the items of a tuple into one string

        Args:
            tup (tuple): general tuple 

        Returns:
            str: output string generated from all items in the tuple
        """

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

    def _base_constraint(self, space:str, time:str):
        """Constraint making the 'ones' constraint, making an intervention a binary intervention.

        Args:
            space (str): name of dataframe's column with information on regions/locations
            time (str): name of dataframe's column with information on time/years
        """
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

    def _intervention_subset(self, intervention:str, strict:bool, subset_names:list =[])-> dict:
        """This function creates a dictionary for the subset of specified interventions

        Args:
            intervention (str): name of dataframe's column with set of interventions 
            strict (bool): whether to look for specific intervention names (using DataFrame.isin) or whether to look for a regex (using DataFrame.str.contains)
            subset_names (list, optional): Which intervention names to look for. Defaults to [].

        Returns:
            dict: dictionary with subset of interventions
        """

        subset_dict = {}

        for i in subset_names:

            if strict:
                subset_dict[i[0]] = self._df.loc[
                    lambda df: df.index.get_level_values(level=intervention).isin([i])
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
        strict:bool,
        intervention:str=None,
        space:str=None,
        time:str=None,
        subset_names:list=None,
        over:str=None,
        subset_list:list=None,
    ):
        """A constraint across space or time, where an intervention is tied to other interventions across space time (for a given subset). For instance, if you wanted to
        create a national intervention, for some intervention X, with 2 regions, this constraint would do the following:
        
        $X_{region1,t} == X_{region2,t}$ -> _all_constraint(over='space', subset_names=None)
        
        If you wanted to make sure that interventions were tied across time so that period 2 could only be used if period 1 was used:
        
        $X_{region1, 1} == X_{region1, 2}$
       
        Args:
            strict (bool): whether to look for specific intervention names (using DataFrame.isin) or whether to look for a regex (using DataFrame.str.contains)
            intervention (str, optional): name of dataframe's column with set of interventions. Defaults to None.
            space (str, optional): name of dataframe's column with information on regions/locations. Defaults to None.
            time (str, optional): name of dataframe's column with information on time/year. Defaults to None.
            subset_names (list, optional): Which intervention names to look for. Defaults to None.
            over (str, optional): name of dataframe's column  with attribute used to group data by (e.g., time, region). Defaults to None.
            subset_list (list, optional): A list of interventions that are being constrained. Defaults to None.
        """

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
        strict:bool,
        intervention:str=None,
        space:str=None,
        time:str=None,
        subset_names:list=None,
        over:str=None,
        subset_list:list=None,
    )->None:
        """This function invokes the function `_all_constraint' to create national interventions

        Args:
            strict (bool): whether to look for specific intervention names (using DataFrame.isin) or whether to look for a regex (using DataFrame.str.contains)
            intervention (str, optional): name of dataframe's column with set of interventions. Defaults to None.
            space (str, optional): name of dataframe's column with informaiton on regions/locations. Defaults to None.
            time (str, optional): name of dataframe's column with information on time/year. Defaults to None.
            subset_names (list, optional): Which intervention names to look for. Defaults to None.
            over (str, optional): name of dataframe's column  with attribute used to group data by (e.g., time, region). Defaults to None.
            subset_list (list, optional): A list of interventions that are being constrained. Defaults to None.
        """

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
        strict:bool,
        intervention:str=None,
        space:str=None,
        time:str=None,
        subset_names:list=None,
        over:str=None,
        subset_list:list=None,
    )->None:
        """This function invokes the function `_all_constraint'

        Args:
            strict (bool): whether to look for specific intervention names (using DataFrame.isin) or whether to look for a regex (using DataFrame.str.contains)
            intervention (str, optional): name of dataframe's column with set of interventions. Defaults to None.
            space (str, optional): name of dataframe's column with information on regions/locations. Defaults to None.
            time (str, optional): name of dataframe's column with information on time/year. Defaults to None.
            subset_names (list, optional): Which intervention names to look for. Defaults to None.
            over (str, optional): name of dataframe's column  with attribute used to group data by (e.g., time, region). Defaults to None.
            subset_list (list, optional): A list of interventions that are being constrained. Defaults to None.
        """

        return self._all_constraint(
            strict,
            intervention=intervention,
            space=space,
            time=time,
            subset_names=subset_names,
            over=over,
            subset_list=subset_list,
        )

    
    def get_equation(self, name:str=None, show:bool=True)->str or mip.LinExpr or mip.Constr :
        """This function returns a constraint by its name. If no name is specified, returns all constraints

        Args:
            name (str, optional): a string corresponding to the name of the constraint. Defaults to None.
            show (bool, optional): whether to return the contraint in string type or not. Defaults to True.

        Returns:
            str or mip.LinExpr or mip.Constr: A `mip` constraint object
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

    def add_objective(self, eq:mip.LinExpr):
        """Sets the objective function of the problem as a linear expression

        Args:
            eq (mip.LinExpr): equation defining the objective function
        """

        self.model.objective = eq

    def add_constraint(self, eq:mip.LinExpr, constraint:mip.LinExpr, way:str="ge", name:str=""):
        """This function merges the objective function of the model with its constraint

        Args:
            eq (mip.LinExpr): equation defining the objective function
            constraint (mip.LinExpr):equation defining the constraint function
            way (str, optional): whether greater or equal (ge), less or equal(le), or equal(eq). Defaults to "ge".
            name (str, optional): optional name for the constraint. Defaults to "".
        """
        
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
        intervention:str,
        space:str,
        time:str,
        all_time:list=None,
        all_space:list=None,
        time_subset:list=None,
        space_subset:list=None,
        strict:bool=False,
    ):
        """A function   

        Args:
            intervention (str): name of dataframe's column with set of interventions
            space (str): name of dataframe's column with information on regions/locations
            time (str): name of dataframe's column with information on time/years
            all_time (list, optional): list of intervention vehicles that are active during all periods (e.g., cube, oil). Defaults to None.
            all_space (list, optional): list of intervention vehicles that are targeted at a country-wide level (e.g., cube, oil). Defaults to None.
            time_subset (list, optional): list with subset of periods. Defaults to None.
            space_subset (list, optional):list with subset of regions/locations. Defaults to None.
            strict (bool, optional): whether to look for specific intervention names (using DataFrame.isin) or whether to look for a regex (using DataFrame.str.contains). Defaults to False.

        """

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
        """This function conducts the optimization procedure 

        Args:
            **kwargs: Other parameters for optimization procedure using `mip.optimize' (max_seconds, max_nodes, max_solutions)
        """

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

    def process_results(self, benefit_col:str, cost_col:str, intervention_col:str, space_col:str, sol_num:int = None)->pd.DataFrame:
        """This function creates a dataframe with information on benefits and costs for the optimal interventions

        Args:
            benefit_col (str): name of dataframe's column with benefits
            cost_col (str): name of dataframe's column with costs
            intervention_col (str): name of dataframe's column with set of interventions
            space_col (str): name of dataframe's column with information on regions/locations
            sol_num (int, optional): index of solution. Defaults to None.

        Returns:
            pd.DataFrame: dataframe with optimal interventions
        """

        
        if isinstance(sol_num, int):
            opt_df = self._df.copy(deep=True).assign(opt_vals=lambda df: df["mip_vars"].apply(lambda y: y.xi(sol_num)))
        else:
            opt_df = self._df.copy(deep=True).assign(
                opt_vals=lambda df: df["mip_vars"].apply(lambda y: y.x))

        opt_df = (opt_df.assign(
            opt_benefit=lambda df: df[benefit_col] * df["opt_vals"],
            opt_costs=lambda df: df[cost_col] * df["opt_vals"],
            opt_costs_discounted=lambda df: df["discounted_costs"] * df["opt_vals"],
            opt_benefit_discounted=lambda df: df["discounted_benefits"]* df["opt_vals"])
                  .infer_objects()
                  .assign(
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
        ])
    

        return opt_df

    def write(self, filename:str="model.lp"):
        """Thi function saves model to file

        Args:
            filename (str, optional): name of file. Defaults to "model.lp".
        """
        self.model.write(filename)

    def get_model_results(self)->list:
        """This function returns a list with additional results of the optimization procedure

        Returns:
            list: model's results
        """

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

