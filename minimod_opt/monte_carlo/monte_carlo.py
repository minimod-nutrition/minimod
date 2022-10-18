from typing import Any, Callable, Dict, List, Union
from minimod_opt.solvers import Minimod
from minimod_opt.utils.plotting import Plotter
from minimod_opt.utils.summary import OptimizationSummary
from mip import OptimizationStatus

import numpy as np
import pandas as pd
from tqdm import tqdm
from pqdm.processes import pqdm

import matplotlib.pyplot as plt

from functools import reduce
from multiprocessing import Pool
from functools import partial
import matplotlib.ticker as mtick


class MonteCarloMinimod:
    def __init__(
        self,
        solver_type: str=None,
        data: pd.DataFrame=None,
        intervention_col: str=None,
        time_col: str=None,
        space_col:str=None,
        benefit_mean_col: str=None,
        benefit_sd_col: str=None,
        cost_col: str=None,
        cost_uniform_perc: float=None,
        pop_weight_col: str=None,
        **kwargs,
    ):
        """MonteCarloMinimod uses the `Minimod` optimization classes and conducts Monte Carlo simulations of benefits and cost data through distribution assumptions on the data. Currently the simulations assume a normal distribution about benefits and a uniform distribution around costs.
        
        

        Args:
            solver_type (str, optional): Whether to minimize costs or maximize benfits. Currently only the former is implemented. Defaults to None.
            data (pd.DataFrame, optional): The input data. Defaults to None.
            intervention_col (str, optional): the name of the intervention variable. Defaults to None.
            time_col (str, optional): the name of the time variable. Defaults to None.
            space_col (str, optional): the name of region/spatial variable. Defaults to None.
            benefit_mean_col (str, optional): the name of the variable that gives the mean of benefits for the intervention. Usually just the name of the benefits variable. Defaults to None.
            benefit_sd_col (str, optional): The name of the variable for the standard deviation of benefits. Defaults to None.
            cost_col (str, optional): The name of the cost variable. Defaults to None.
            cost_uniform_perc (float, optional): If using the default of a uniform distribution for costs, the amount of the endpoint of the uniform distribution ([cost*(1+cost_uniform_perc), cost*(1- cost_uniform_perc)]). Defaults to None.
            pop_weight_col (str, optional): The name name of the variable that specific population weights. Defaults to None.
            
        Examples:
        
            Below is an example of how you would run the simulations as well as the visualizations.
            
            >>> import os; print(os.getcwd())
            >>> df = (
            ...     pd.read_csv("data/processed/example1.csv")
            ...     .assign(benefit_sd = lambda df: df['benefit']/2,
            ...             costs_sd = lambda df: df['costs']/2)
            ...     )

            >>> cube = ["cube", "vascube", "oilcube", "cubemaize", "vascubemaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
            >>> oil = ["oil", "vasoil", "oilcube", "oilmaize", "vasoilmaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
            >>> maize = ["maize", "vasmaize", "oilmaize", "cubemaize", "vascubemaize", "vasoilmaize", "oilcubemaize", "vasoilcubemaize" ]

            >>> a = mm.MonteCarloMinimod(solver_type = 'costmin', 
            ...                        data = df, 
            ...                        intervention_col='intervention',
            ...                        space_col='space',
            ...                        time_col='time',
            ...                        benefit_mean_col = 'benefit',
            ...                        benefit_sd_col= 'benefit_sd',
            ...                        cost_col='costs')

            >>> def benefit_no_change(seed, benefit_col, data):
            ...    return data[benefit_col]
            
            >>> sim = a.fit_all_samples(N = 100, 
            ...                         all_space=oil, 
            ...                         all_time=cube, 
            ...                         time_subset=[1,2,3], 
            ...                         minimum_benefit='vasoilold', 
            ...                         benefit_callable=benefit_no_change, 
            ...                         benefit_kwargs={'benefit_col' : 'benefit'}
            ...                         )
            
            >>> a.plot_opt_hist(save = "sim_results.png")

            >>> a.report(perc_intervention_appeared=True)

            >>> a.plot_sim_trajectories(save = 'sim_traj.png')
        
        """        
     

        print("""Monte Carlo Simulator""")

        self.solver_type = solver_type

        self.data = data.set_index([intervention_col, space_col, time_col])

        self.intervention_col = intervention_col
        self.space_col = space_col
        self.time_col = time_col

        if pop_weight_col is None:
            self.data = self.data.assign(pop_weight_col=1)
            self.pop_weight_col = "pop_weight_col"
        else:
            self.pop_weight_col = pop_weight_col

        self.benefit_mean_col = benefit_mean_col
        self.benefit_sd_col = benefit_sd_col

        if cost_uniform_perc is None:
            self.cost_uniform_perc = 0.2
        else:
            self.cost_uniform_perc = cost_uniform_perc

        self.cost_col = cost_col


    def _construct_benefit_sample(self, seed: int, data: pd.DataFrame=None, benefit_col: str = 'benefit_random_draw') -> pd.Series:
        """Draw of a sample of benefits assuming normality

        Args:
            seed (int): The random seed
            data (pd.DataFrame, optional): The input data. Defaults to None.
            benefit_col (str, optional): the name of the resulting benefits variable. Defaults to 'benefit_random_draw'.

        Returns:
            pd.Series: A series of benefits
        """        

        random = np.random.default_rng(seed=seed)
        
        df_mean_sd = data[
            [self.benefit_mean_col, self.benefit_sd_col, self.pop_weight_col]
        ]

        df = df_mean_sd.pipe(self._drop_nan_benefits).assign(
            weight_mean=lambda df: df[self.benefit_mean_col] * df[self.pop_weight_col],
            weight_sd=lambda df: df[self.benefit_sd_col] * df[self.pop_weight_col],
            benefit_random_draw=lambda df: random.normal(
                df["weight_mean"], df["weight_sd"]
            ),
        )

        return df[benefit_col]

    def _construct_cost_sample(self, seed: str, data: pd.DataFrame=None, cost_col: str='cost_random_draw') -> pd.Series:
        """Draw a sample costs assuming a uniform distribution

        Args:
            seed (str): The randome
            data (pd.DataFrame, optional): The input data. Defaults to None.
            cost_col (str, optional): The name of the cost variable. Defaults to 'cost_random_draw'.

        Returns:
            pd.Series: The cost draw
        """        

        random= np.random.default_rng(seed=seed)

        df_costs = data[self.cost_col]
        df_costs_low = (1 - self.cost_uniform_perc) * data[self.cost_col]
        df_costs_high = (1 + self.cost_uniform_perc) * data[self.cost_col]

        df = df_costs.to_frame().assign(
            cost_random_draw=random.uniform(df_costs_low, df_costs_high)
        )

        return df[cost_col]

    def _drop_nan_benefits(self, data):

        df = data.dropna(subset=[self.benefit_sd_col])

        return df

    def _merge_samples(self, benefit_callable: Callable, cost_callable: Callable,  
                       cost_kwargs: dict, benefit_kwargs: dict) -> pd.DataFrame:
        """Transforms the cost and benefit data and merges them together.

        Args:
            benefit_callable (Callable): The function for transforming benefits
            cost_callable (Callable): The function for transforming costs
            cost_kwargs (dict): extra arguments for `cost_callable`
            benefit_kwargs (dict): extra arguments for `benefit_callable`

        Returns:
            pd.DataFrame: The merged dataset of benefits and costs
        """        
        

        benefit_sample = benefit_callable(**benefit_kwargs)
        cost_sample = cost_callable(**cost_kwargs)

        return benefit_sample.to_frame().merge(
            cost_sample, left_index=True, right_index=True
        )
        
    def fit_one_sample(self, 
                       seed: int,
                       all_space: Union[List, None],
                       all_time: Union[List, None],
                       space_subset: List[str],
                       time_subset: List[int],
                       strict: bool,
                       benefit_callable:Union[Callable, None],
                       cost_callable:Union[Callable, None],
                       cost_kwargs:dict,
                       benefit_kwargs:dict,
                       **kwargs) -> dict:
        """Draw one MonteCarlo sample and optimize. To be used with `fit_all_samples`. 
        
        `benefit_callable` and `cost_callable` must be functions with arguments `(seed, benefit_col, data)`. `cost_kwargs` and `benefit_kwargs` can be input to override defaults, such as if you want to use a different seed or change the name of a column.
        
        Note: `benefit_col` and `cost_col` for these callables denote the name of the resulting columns of the draw, not the original variable names.

        Args:
            seed (int): random seed
            all_space (Union[List, None]): spatial constraints (as in `Minimod`)
            all_time (Union[List, None]): time constraints (as in `Minimod`)
            space_subset (List[str]): subset for space constraints (as in `Minimod`)
            time_subset (List[int]): subset for time constraints (as in `Minimod`)
            strict (bool): whether to treat list of intervention names input *strictly* or using regex
            benefit_callable (Union[Callable, None]): The function for benefits transformation
            cost_callable (Union[Callable, None]): The function for cost transformation
            cost_kwargs (dict): extra arguments for the cost_callabe
            benefit_kwargs (dict): extra arguments for benefits callable

        Returns:
            dict: A dictionary of fitted results
        """    
        
        if benefit_callable is None:
            benefit_callable = self._construct_benefit_sample
        if cost_callable is None:
            cost_callable = self._construct_cost_sample

        cost_kwargs_default = {'seed' : seed, 'cost_col' : 'cost_random_draw', 'data' : self.data}
        benefit_kwargs_default = {'seed' : seed, 'benefit_col' : 'benefit_random_draw', 'data' : self.data}
        
        if cost_kwargs is not None:
            cost_kwargs_default.update(cost_kwargs)
        if benefit_kwargs is not None:
            benefit_kwargs_default.update(benefit_kwargs)

                       
        df = self._merge_samples(benefit_callable=benefit_callable,
                                 cost_callable=cost_callable,
                                 benefit_kwargs=benefit_kwargs_default,
                                 cost_kwargs=cost_kwargs_default) 

        minimod = Minimod(solver_type=self.solver_type)(
            data=df,
            intervention_col=self.intervention_col,
            space_col=self.space_col,
            time_col=self.time_col,
            benefit_col=benefit_kwargs_default.get('benefit_col'),
            cost_col=cost_kwargs_default.get('cost_col'),
            all_space=all_space,
            all_time=all_time,
            space_subset=space_subset,
            time_subset=time_subset,
            show_output=False,
            strict=strict,
            benefit_title="Effective Coverage",
            **kwargs,
        )

        minimod_opt.fit()
        
        # Run `minimod_opt.report` to get opt_df for iteration
        # Also save the opt_chosen dataframes in case there are multiple solutions
        
        opt_df_list = []
        
        for i in range(minimod_opt.num_solutions):
            minimod_opt.report(sol_num=i, quiet=True)
            opt_df_list.append(minimod_opt.opt_df)
            
        #TODO: add lowest cost per life saved index into iteration dict
            
        iteration_dict = {
            "status": minimod_opt.status,
            "opt_objective": [df['opt_costs_discounted'].sum() for df in opt_df_list],
            "opt_constraint": [df["opt_benefit_discounted"].sum() for df in opt_df_list],
            "num_vars": minimod_opt.num_cols,
            "constraints": minimod_opt.num_rows,
            "solutions": minimod_opt.num_solutions,
            "num_int": minimod_opt.num_int,
            "num_nz": minimod_opt.num_nz,
            "opt_df": opt_df_list,
            "sense" : minimod_opt.sense,
            "solver_name" : minimod_opt.solver_name,
            "minimum_benefit" : minimod_opt.minimum_benefit,
            "benefit_title" : minimod_opt.benefit_title,
            "bau_draw" : minimod_opt.bau_df
        }
        
        return iteration_dict

    def fit_all_samples(
        self,
        n_jobs = 5,
        N=None,
        all_space=None,
        all_time=None,
        space_subset=None,
        time_subset=None,
        strict=False,
        exception_behavior = 'immediate',
        only_optimal=False,
        benefit_callable=None,
        cost_callable=None,
        benefit_kwargs=None,
        cost_kwargs=None,
        random_seeds = None,
        **kwargs
    ):
        
        if N is None:
            N = 10

        sim_dict = {}


        print(f"""Running with {N} Samples""")
        
        partial_fit_sample = partial(self.fit_one_sample, 
                                     all_space=all_space,
                                     all_time=all_time,
                                     space_subset=space_subset,
                                     time_subset = time_subset,
                                     strict=strict,
                                     benefit_callable=benefit_callable,
                                     cost_callable=cost_callable,
                                     benefit_kwargs=benefit_kwargs,
                                     cost_kwargs=cost_kwargs,
                                     **kwargs)
        
        if random_seeds is None:
            random_seeds = range(N)
                
        sim_dict = pqdm(random_seeds, partial_fit_sample, n_jobs=n_jobs, exception_behaviour=exception_behavior)
        
        sim_df = pd.DataFrame(sim_dict)
        
        self.perc_opt = sim_df["status"].value_counts(normalize=True)[0] * 100

        if only_optimal:
            self.sim_results = sim_df.loc[lambda df: df['status'] == OptimizationStatus.OPTIMAL]
        else:
            self.sim_results = sim_df

        self.N = self.sim_results.shape[0]

        return self.sim_results

    def _all_opt_df(self, sol_filter=None):
        """Appends the dataframe from all simulation iterations together
        """
        #TODO: #28 Allow for concatenation of a combination of solutions, or all
        
        # First get sim_results so that `opt_df` is a series of dataframes
        # Turn list into numpy since it has a `take` method
        
        if sol_filter=='min_cb':
            # Find the solution with the highest benefit/cost ratio
            sol_num_all_opt_df = self.sim_results.assign(best_solution  = lambda df: df.apply(lambda df: (np.array(df['opt_objective'])/np.array(df['opt_constraint'])).argmin(), axis=1),
                                       new_opt_df = lambda df: df.apply(lambda x: x['opt_df'][x['best_solution']], axis=1))
        else:
            sol_num_all_opt_df = self.sim_results.assign(new_opt_df = lambda df: df['opt_df'].apply(lambda x: pd.concat(x)))
        
        all_opt_df = pd.concat(sol_num_all_opt_df.apply(lambda x: x['new_opt_df'].assign(iteration = x.name), axis=1).tolist())

        return all_opt_df

    def _get_intervention_group(self, data, intervention, strict=False):

        
        if strict:
            
            int_group = (
                data
                .loc[lambda df: df.index.
                    get_level_values(level= self.intervention_col)
                    .isin(intervention)]
            )
        
        else:
            int_group = (
                data
                .loc[lambda df: df.index.
                    get_level_values(level= self.intervention_col)
                    .str.contains(intervention)]
            )

        return int_group
    
    def _get_indicator_if_in_intervention(self, name, indicator_spec = None, strict=False):
        
        if indicator_spec is None:
            indicator_spec = 1
        
        return (self._get_intervention_group(self._all_opt_df(), name, strict=strict)
                .reset_index()
                [['opt_vals', 'iteration', self.intervention_col, self.space_col, self.time_col]]
                .groupby('iteration')
                .agg(lambda x: 1 if x.sum() > indicator_spec else 0)
                )

    def report(
        self,
        avg_time=False,
        avg_space=False,
        intervention_group=None,
        indicator_spec = None,
        strict=False
    ):

        avg = self.sim_results.convert_dtypes().mean()

        s = OptimizationSummary(self)

        header = [
            ("MiniMod Solver Results", ""),
            ("Method:", str(self.sim_results['sense'].min())),
            ("Solver:", str(self.sim_results['solver_name'].min())),
            ("Percentage Optimized:", self.perc_opt),
            ("Average Number Solutions Found:", avg["solutions"]),
        ]

        features = [
            ("No. of Variables:", avg["num_vars"]),
            ("No. of Integer Variables:", avg["num_int"]),
            ("No. of Constraints", avg["constraints"]),
            ("No. of Non-zeros in Constr.", avg["num_nz"]),
        ]

        results_benefits = [("Minimum Benefit", self.sim_results.minimum_benefit.mean())]

        stats = [
            ("Statistics for Benefits and Costs", ""),
        ]

        s.print_generic(header, features, results_benefits, stats)

        stats_df = (
            self.sim_results[["opt_objective", "opt_constraint"]]
            .astype(float)
            .describe()
            .round(4)
            .to_markdown()
        )
        print(stats_df)

        if intervention_group is not None:

            s.print_generic([(f"% Appearance of:", "")])

            for i in intervention_group:

                int_group = (self._get_indicator_if_in_intervention(i, 
                                                                    indicator_spec=indicator_spec,
                                                                    strict=strict).sum()/self.N*100)['opt_vals']

                s.print_generic([(f"{i}", f"{int_group}")])

        if avg_time:

            time_df = (
                self._all_opt_df().groupby([self.time_col, "iteration"])
                .sum()
                .groupby(self.time_col)
                .mean()[["opt_benefit", "opt_costs"]]
            )

            s.print_generic([("Mean Benefits and Costs across time", "")])
            print(time_df.to_markdown())

        if avg_space:

            space_df = (
                self._all_opt_df().groupby([self.space_col, "iteration"])
                .sum()
                .groupby(self.space_col)
                .mean()[["opt_benefit", "opt_costs"]]
            )

            s.print_generic([("Mean Benefits and Costs across Regions", "")])
            print(space_df.to_markdown())

    def plot_opt_hist(self, save=None):

        p = Plotter(self)

        costs = "Optimal Costs"
        benefits = self.sim_results['benefit_title'].min()

        if self.solver_type == "costmin":

            objective_title = costs
            constraint_title = benefits

        elif self.solver_type == "benmax":

            objective_title = benefits
            constraint_title = costs


        self.sim_results['opt_constraint2']=self.sim_results['opt_constraint'].apply(lambda x: x[0]/1000)
        self.sim_results['opt_objective2']=self.sim_results['opt_objective'].apply(lambda x: x[0]/1000)

        fig, (benefit_plot, cost_plot) = p._plot_sim_hist(
            data=self.sim_results,
            benefit_col="opt_constraint2",
            cost_col="opt_objective2",
            #benefit_col="opt_constraint",
            #cost_col="opt_objective",
            cost_title=objective_title,
            benefit_title=constraint_title,
            save=save,
        )

        benefit_plot.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
        cost_plot.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    
        benefit_plot.set_xlabel("Thousands of Individuals")
        cost_plot.set_xlabel("Thousands of 2019 USD")

        benefit_xlims = benefit_plot.get_xlim()
        benefit_ylims = benefit_plot.get_ylim()

        # Put text at midpoint of y
        text_y = (benefit_ylims[1] - benefit_ylims[0]) / 2

        # offset by 10% of length of x-axis
        text_x = (
            self.sim_results['minimum_benefit'].mean()/1000 + (benefit_xlims[1] - benefit_xlims[0]) * 0.1
        )

        benefit_plot.axvline(self.sim_results['minimum_benefit'].mean()/1000, color="red")
        benefit_plot.text(text_x, text_y, "Mean\nMinimum\nBenefit\nConstraint")
        
        # Get total cost for a draw 
        cost_xlims = cost_plot.get_xlim()
        cost_ylims = cost_plot.get_ylim()

        # Put text at midpoint of y
        cost_plot.axvline(self.sim_results['bau_draw'].apply(lambda x: x['discounted_costs'].sum()).mean()/1000, color='red')

        text_y2 = (cost_ylims[1] - cost_ylims[0]) / 2

        # offset by 10% of length of x-axis
        text_x2 = (
            self.sim_results['bau_draw'].apply(lambda x: x['discounted_costs'].sum()).mean()/1000 + (cost_xlims[1] - cost_xlims[0]) * 0.1
        )
        cost_plot.text(text_x2, text_y2, "Mean\nBAU\nCost")

        return fig, (benefit_plot, cost_plot)

    def plot_sim_trajectories(self, data_of_interest="benefits", save=None):

        fig, ax = plt.subplots()

        if data_of_interest == "benefits":
            col_of_interest = "opt_benefit"
            ylabel_interest = "Individuals"
        elif data_of_interest == "costs":
            col_of_interest = "opt_costs"
            ylabel_interest = "2019 USD"
        
        df_all = self.sim_results['opt_df'].apply(lambda x: x[col_of_interest].groupby(self.time_col).sum()).T

        # Now get mean trajectory

        df_all.plot(color='red', alpha=0.09, ax=ax, legend=False)
        df_all.mean(axis=1).plot(ax=ax, color="black")

        # plt.figtext(0, 0, "Bold line represents mean trajectory.")
        ax.set_title("Trajectories of all Simulations")
        
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
        ax.set_ylabel(ylabel_interest)

        if save is not None:
            plt.savefig(save, dpi=160)

        return ax

    def plot_intervention_stacked(self, intervention_group=None, intervention_names = None, indicator_spec=3):
        
        fig, ax = plt.subplots()

        all_opt_df = (self._all_opt_df()
                      .groupby(['intervention', 'time', 'iteration'])
                      ['opt_vals']
                      .sum()
                      .to_frame()
                      .assign(opt_vals = lambda df: (df['opt_vals']>indicator_spec).astype(int))
                      )
        
        int_group = (
            all_opt_df[all_opt_df['opt_vals']>indicator_spec]
            .reset_index(level=self.intervention_col)
            [self.intervention_col]
            .str.extractall('|'.join([f"(?P<{j}>{i})" for i, j in zip(intervention_group, intervention_names)]))
         )             
        
        int_group.groupby(self.time_col).count().apply(lambda x: x/x.sum(), axis=1).plot.bar(stacked=True, ax=ax)
                   
        
        ax.legend(loc = 'lower left', bbox_to_anchor=(1.0, 0.5))
        ax.set_ylabel("% of Occurrences")
        ax.set_xlabel("Time")
        
        return ax

    