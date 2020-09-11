from minimod.solvers import Minimod
from minimod.utils.plotting import Plotter
from minimod.utils.summary import OptimizationSummary

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
        solver_type=None,
        data=None,
        intervention_col=None,
        time_col=None,
        space_col=None,
        benefit_mean_col=None,
        benefit_sd_col=None,
        cost_col=None,
        cost_uniform_perc=None,
        pop_weight_col=None,
        **kwargs,
    ):

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

    def _construct_benefit_sample(self, seed):
        """ For normal, it doesn't require transformation, so just return mean and sd"""

        random = np.random.default_rng(seed=seed)
        
        df_mean_sd = self.data[
            [self.benefit_mean_col, self.benefit_sd_col, self.pop_weight_col]
        ]

        df = df_mean_sd.pipe(self._drop_nan_benefits).assign(
            weight_mean=lambda df: df[self.benefit_mean_col] * df[self.pop_weight_col],
            weight_sd=lambda df: df[self.benefit_sd_col] * df[self.pop_weight_col],
            benefit_random_draw=lambda df: random.normal(
                df["weight_mean"], df["weight_sd"]
            ),
        )

        return df["benefit_random_draw"]

    def _construct_cost_sample(self,seed):
        """For costs we assume uniform and deviate by some percentage."""

        random= np.random.default_rng(seed=seed)

        df_costs = self.data[self.cost_col]
        df_costs_low = (1 - self.cost_uniform_perc) * self.data[self.cost_col]
        df_costs_high = (1 + self.cost_uniform_perc) * self.data[self.cost_col]

        df = df_costs.to_frame().assign(
            cost_random_draw=random.uniform(df_costs_low, df_costs_high)
        )

        return df["cost_random_draw"]

    def _drop_nan_benefits(self, data):

        df = data.dropna(subset=[self.benefit_sd_col])

        return df

    def _merge_samples(self, seed):

        benefit_sample = self._construct_benefit_sample(seed=seed)
        cost_sample = self._construct_cost_sample(seed=seed)

        return benefit_sample.to_frame().merge(
            cost_sample, left_index=True, right_index=True
        )
        
    def fit_one_sample(self, 
                       seed,
                       all_space,
                       all_time,
                       space_subset,
                       time_subset,
                       strict,
                       **kwargs):
        df = self._merge_samples(seed=seed) # Needs to be inside loop to get different draw each time

        minimod = Minimod(
            solver_type=self.solver_type,
            data=df,
            intervention_col=self.intervention_col,
            space_col=self.space_col,
            time_col=self.time_col,
            benefit_col="benefit_random_draw",
            cost_col="cost_random_draw",
            all_space=all_space,
            all_time=all_time,
            space_subset=space_subset,
            time_subset=time_subset,
            show_output=False,
            strict=strict,
            benefit_title="Effective Coverage",
            **kwargs,
        )

        minimod.fit()

        iteration_dict = {
            "status": minimod.status,
            "opt_objective": minimod.opt_df['opt_costs'].sum(),
            "opt_constraint": minimod.opt_df["opt_benefit"].sum(),
            "num_vars": minimod.num_cols,
            "constraints": minimod.num_rows,
            "solutions": minimod.num_solutions,
            "num_int": minimod.num_int,
            "num_nz": minimod.num_nz,
            "opt_df": minimod.opt_df,
            "sense" : minimod.sense,
            "solver_name" : minimod.solver_name,
            "minimum_benefit" : minimod.minimum_benefit,
            "benefit_title" : minimod.benefit_title,
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
        # show_progress=True,
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
                                     **kwargs)
        
        sim_dict = pqdm(range(N), partial_fit_sample, n_jobs=n_jobs)
            
        self.N = N

        self.sim_results = pd.DataFrame(sim_dict)

        return pd.DataFrame(sim_dict)

    def _all_opt_df(self):
        """Appends the dataframe from all simulation iterations together
        """

        opt_df_list = [
            self.sim_results.stack()  # Get results  # stack so columns become index
            .loc[(slice(None), "opt_df")][i]  # Get only opt_df
            .assign(iteration=i)  # Create variable for iteration
            for i in range(self.N)
        ]

        all_opt_df = reduce(lambda i, j: i.append(j), opt_df_list)

        return all_opt_df

    def _perc_int_df(self, data, grouper_col = None):
        """Creates a dataframe of intervention appearances in simulations
        """
        
        if grouper_col is None:
            grouper_col = self.intervention_col
        else:
            if isinstance(grouper_col, str):
                grouper_col = [self.intervention_col] + [grouper_col]
            else:
                grouper_col = [self.intervention_col] + grouper_col

        perc_int = (
            data
            .assign(val_appeared=lambda df: (df["opt_vals"] > 0).astype(int))[
                "val_appeared"
            ]
            .groupby(grouper_col)
            .sum()
        ) 

        return perc_int

    def _get_intervention_group(self, perc_int, intervention):
        

        int_group = (
            perc_int
            .loc[lambda df: df.index.
                 get_level_values(level= self.intervention_col)
                 .str.contains(intervention)]
        )

        return int_group

    def report(
        self,
        avg_time=False,
        avg_space=False,
        perc_intervention_appeared=False,
        show_percint_full=False,
        intervention_group=None,
    ):

        perc_opt = self.sim_results["status"].value_counts(normalize=True)[0] * 100
        avg = self.sim_results.convert_dtypes().mean()

        s = OptimizationSummary(self)

        header = [
            ("MiniMod Solver Results", ""),
            ("Method:", str(self.sim_results['sense'].min())),
            ("Solver:", str(self.sim_results['solver_name'].min())),
            ("Percentage Optimized:", perc_opt),
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

        all_opt_df = self._all_opt_df()
        
        grouped_all_opt_df = (
            all_opt_df
            .groupby([self.intervention_col, "iteration"])
            .sum()
            )

        if perc_intervention_appeared:

            perc_int = (self._perc_int_df(grouped_all_opt_df)/self.N)*100

            s.print_generic([("Percentage Appeared in Simulations", "")])

            if show_percint_full:
                print(perc_int.to_markdown())

            if intervention_group is not None:

                s.print_generic([(f"% Appearance of:", "")])

                for i in intervention_group:

                    int_group = self._get_intervention_group(perc_int, i).sum()/perc_int.sum()

                    s.print_generic([(f"{i}", f"{int_group}")])

        if avg_time:

            time_df = (
                all_opt_df.groupby([self.time_col, "iteration"])
                .sum()
                .groupby(self.time_col)
                .mean()[["opt_benefit", "opt_costs"]]
            )

            s.print_generic([("Mean Benefits and Costs across time", "")])
            print(time_df.to_markdown())

        if avg_space:

            space_df = (
                all_opt_df.groupby([self.space_col, "iteration"])
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

        fig, (benefit_plot, cost_plot) = p._plot_sim_hist(
            data=self.sim_results,
            benefit_col="opt_constraint",
            cost_col="opt_objective",
            cost_title=objective_title,
            benefit_title=constraint_title,
            save=save,
        )

        benefit_plot.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
        cost_plot.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))


        benefit_xlims = benefit_plot.get_xlim()
        benefit_ylims = benefit_plot.get_ylim()

        # Put text at midpoint of y
        text_y = (benefit_ylims[1] - benefit_ylims[0]) / 2

        # offset by 10% of length of x-axis
        text_x = (
            self.sim_results['minimum_benefit'].mean() + (benefit_xlims[1] - benefit_xlims[0]) * 0.1
        )

        benefit_plot.axvline(self.sim_results['minimum_benefit'].mean(), color="red")
        benefit_plot.text(text_x, text_y, "Mean\nMinimum\nBenefit\nConstraint")

        return fig, (benefit_plot, cost_plot)

    def plot_sim_trajectories(self, data_of_interest="benefits", save=None):

        fig, ax = plt.subplots()

        if data_of_interest == "benefits":
            col_of_interest = "opt_benefit"
        elif data_of_interest == "costs":
            col_of_interest = "opt_costs"

        df_all = pd.DataFrame()

        # All trajectories
        for i in range(self.N):

            iter_df = (
                self.sim_results.loc[i]["opt_df"][col_of_interest]
                .groupby(self.time_col)
                .sum()
            )

            iter_df.plot(ax=ax, color="red", alpha=0.09)

            df_all = df_all.append(iter_df)

        # Now get mean trajectory

        df_all.mean().plot(ax=ax, color="black")

        plt.figtext(0, 0, "Bold line represents mean trajectory.")
        ax.set_title("Trajectories of all Simulations")
        
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

        if save is not None:
            plt.savefig(save, dpi=160)

        return ax

    def plot_intervention_stacked(self, intervention_group=None):
        
        fig, ax = plt.subplots()

        all_opt_df = (
            self._all_opt_df()
            .groupby([self.intervention_col, self.time_col])
            .sum()
            )

        perc_int = self._perc_int_df(all_opt_df, 
                                     grouper_col=self.time_col)

        int_groups = {
            name: self._get_intervention_group(perc_int, name).groupby(self.time_col).sum()
            for name in intervention_group
        }
        
        int_groups_df = pd.DataFrame(int_groups)
                
        (
            int_groups_df
            .apply(lambda x: x/int_groups_df.sum(axis=1))
            .plot.bar(ax = ax, stacked = True)
            )
        
        ax.legend(loc = 'lower left', bbox_to_anchor=(1.0, 0.5))
        ax.set_ylabel("% of Occurrences")
        ax.set_xlabel("Time")
        
        return ax
        