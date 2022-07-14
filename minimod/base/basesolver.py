# Imports for local packages
from minimod.utils.exceptions import (
    MissingData,
    NotPandasDataframe,
    MissingOptimizationMethod,
)

from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

from minimod.utils.summary import OptimizationSummary
from minimod.utils.plotting import Plotter
from minimod.utils.suppress_messages import suppress_stdout_stderr

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import mip
import re

import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec


class BaseSolver:

    def __init__(
        self,
        data,
        benefit_col = 'benefits',
        cost_col = 'costs',
        intervention_col = 'intervention',
        space_col = 'space',
        time_col = 'time',
        interest_rate_cost=0.0,  # Discount factor for costs
        interest_rate_benefit=0.03,  # Discount factor for benefits 
        va_weight=1.0,  # VA Weight
        sense=None,  # MIP optimization type (maximization or minimization)
        solver_name=mip.CBC,  # Solver for MIP to use
        show_output = True,
        benefit_title = "Benefits",
    ):       
        """The base solver for the Optimization. This sets up the basic setup of the model, which includes:
        - data handling
        - BAU constraint creation
        - base model constraint creation

        :param data: dataframe with benefits and cost data
        :type data: pandas.DataFrame
        :param benefit_col: benefit data column, defaults to 'benefits'
        :type benefit_col: str, optional
        :param cost_col: cost data column, defaults to 'costs'
        :type cost_col: str, optional
        :param intervention_col: intervention data column, defaults to 'intervention'
        :type intervention_col: str, optional
        :param space_col: space/region data column, defaults to 'space'
        :type space_col: str, optional
        :param time_col: time period data column, defaults to 'time'
        :type time_col: str, optional
        :param all_time: Whether to treat some interventions as being constrained in time. Coupled with ``time_subset`` to constrain some time periods to all time periods, defaults to None
        :type all_time: list or iterable, optional
        :param all_space: whether to treat some interventions as being constraint over space. Coupled with ``space_subset`` to constrain some regions to all regions, defaults to None
        :type all_space: list or iterable, optional
        :param time_subset: a subset of time periods in the ``data.time_col`` that are constrained to all other time periods.
        For example, if ``time_subset = [1,2,3]``, you cannot choose time periods 4-10, without also choosing 1-3. defaults to None, which constrains all time periods to each other.
        :type time_subset: list or iterable, optional
        :param space_subset: a subset of regions in ``data.space_col`` that constrain to all other regions, defaults to None which constrains all regions to each other (national intervention).
        :type space_subset: list or iterable, optional
        :param strict: Whether to use strict string matching for time and space subsets or whether ``time_subset`` or ``space_subset`` should be treated as a string stub that an intervention should contain. 
        :type strict: bool, optional
        :param interest_rate_cost: interest rate of costs, defaults to 0.0
        :type interest_rate_cost: float, optional
        :param benefit_title: title for benefits to put in plots and reports, defaults to "Benefits"
        :type benefit_title: str, optional
        
        ``BaseSolver`` is inherited by ``CostSolver`` and ``BenefitSolver`` to then run optimizations.
        """        
                
        self.interest_rate_cost = interest_rate_cost
        self.interest_rate_benefit = interest_rate_benefit
        self.va_weight = va_weight
        self.discount_costs = 1 / (1 + self.interest_rate_cost)
        self.discount_benefits = 1 / (1 + self.interest_rate_benefit)
        self.benefit_title = benefit_title
        
        if sense is not None:
            self.sense = sense
        else:
            raise Exception("No Optimization Method was specified")
        
        self.solver_name = solver_name
        self.show_output = show_output
        
        # Process Data
        
        if self.show_output:
            print("[Note]: Processing Data...")

        self._df = self._process_data(
            data=data,
            intervention=intervention_col,
            space=space_col,
            time=time_col,
            benefits=benefit_col,
            costs=cost_col,
        )
        
        
        self.benefit_col = benefit_col
        self.cost_col = cost_col
        self.intervention_col = intervention_col
        self.space_col = space_col
        self.time_col = time_col
        
        if self.show_output:
            print("[Note]: Creating Base Model with constraints")
            
        
        self.minimum_benefit = None
        self.total_funds = None
        
        if self.show_output:
            print(
                f"""
                MiniMod Nutrition Intervention Tool
                Optimization Method: {str(self.sense)}
                Version: {__version__}
                Solver: {str(self.solver_name)},
                Show Output: {self.show_output}
                
                """
            )
        
    def _discounted_sum_all(self, col_name):
        """Multiply each ``mip_var`` in the data by benefits or costs (``data``) and then create a ``mip`` expression from it.

        :param data: dataset of benefits and costs
        :type data: pandas.DataFrame
        :return: ``mip`` Expression
        :rtype: ``mip.LinExpr``
        """        
        
        eq = (self._df['mip_vars'] * self._df[col_name]).agg(mip.xsum)

        return eq

    def _discounted_sum_over(self, col_name, over):
        
        # Merge data with self._df
        
        eq = (self._df['mip_vars'] * self._df[col_name]).groupby(over).agg(mip.xsum)
        
        return eq.to_frame().rename({0 : col_name + '_vars'}, axis=1)

    def _is_dataframe(self, data):
        """Checks if input dataset if a ``pandas.DataFrame``

        :param data: input data
        :type data: anything
        :raises NotPandasDataframe: Exception if not a ``pandas.DataFrame``
        """        

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
        """Processes the input data by creating discounted benefits and costs.

        :param data: data, defaults to None
        :type data: pandas.DataFrame, optional
        :param intervention: intervention column, defaults to "intervention"
        :type intervention: str, optional
        :param space: space/region column, defaults to "space"
        :type space: str, optional
        :param time: time period column, defaults to "time"
        :type time: str, optional
        :param benefits: benefits column, defaults to "benefits"
        :type benefits: str, optional
        :param costs: cost column, defaults to "costs"
        :type costs: str, optional
        
        This method processes the data and gets it ready to be used in the problem

        |k     | j   |t   | benefits   | costs |
        |------|-----|----|------------|-------|
        |maize |north|0   | 100        | 10    |
        |maize |south|0   | 50         | 20    |
        |maize |east |0   | 30         |30     |
        |maize |west |0   | 20         |40     |
        
        """

        ## First do some sanity checks
        if data is None:
            raise MissingData("No data specified.")

        # Check if dataframe
        self._is_dataframe(data)

        df_aux = (
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
                discounted_benefits=lambda df: df["time_discount_benefits"]*df[benefits]
            )
        )
        
        df_aux[intervention] = df_aux[intervention].str.lower().str.lstrip().str.rstrip()
        
        df = (
            df_aux
            .set_index([intervention, space, time])
            .sort_index(level=(intervention, space, time))
        )

        return df

    def _constraint(self):
        """To be overridden by BenefitSolver and CostSolver classes.
        This defines the constraints for the mips model.
        """
        self.constraint_called = 0

    def _objective(self):
        """To be overridden by BenefitSolver and CostSolver classes.
        The objective function defines the objective function for a model.
        """
        pass

    def _fit(self, **kwargs):
        """Fits data to model. The instantiation of the class creates the base model. Uses ``mip.optimize`` to find the optimal point.
        """        

        if self.show_output:
            print("[Note]: Optimizing...")

        self.model.optimize(**kwargs)  
        
        (self.objective_value,
         self.objective_values, 
         self.objective_bound, 
         self.num_solutions, 
         self.num_cols, 
         self.num_rows, 
         self.num_int, 
         self.num_nz, 
         self.status) = self.model.get_model_results()
        
        return self
        
    def write(self, filename="model.lp"):
        
        self.model.write(filename)
        
    def process_results(self, sol_num=None):
        
        self.opt_df = self.model.process_results(self.benefit_col, 
                                            self.cost_col, 
                                            self.intervention_col,
                                            self.space_col,
                                            sol_num=sol_num)
        
    def report(self, sol_num=None, quiet=False):
        """Prints out a report of optimal model parameters and useful statistics.
        """        
        
        self.opt_df = self.model.process_results(self.benefit_col, 
                                            self.cost_col, 
                                            self.intervention_col,
                                            self.space_col,
                                            sol_num=sol_num)

        if quiet:
            return
        header = [
            ('MiniMod Solver Results', ""),
            ("Method:" , str(self.sense)),
            ("Solver:", str(self.solver_name)),
            ("Optimization Status:", str(self.status)),
            ("Number of Solutions Found:", str(self.num_solutions))

        ]
        
        features = [
            ("No. of Variables:", str(self.num_cols)),
            ("No. of Integer Variables:", str(self.num_int)),
            ("No. of Constraints", str(self.num_rows)),
            ("No. of Non-zeros in Constr.", str(self.num_nz))
        ]
        
        s = OptimizationSummary(self)

        s.print_generic(header, features)
        
        print("Interventions Chosen:")
        
    @property
    def optimal_interventions(self):
        opt_intervention = (
            self.opt_df
            .loc[lambda df: df['opt_vals']>0]
            .index
            .get_level_values(level=self.intervention_col)
            .unique()
            .tolist()
        )
        
        return opt_intervention
    
    @property
    def _intervention_list_space_time(self):
        
        df = (
            self.opt_df['opt_vals']
            .reset_index(level=self.intervention_col)
            .assign(int_appeared= lambda df: df[self.intervention_col]*df['opt_vals'].astype(int))
            .groupby([self.space_col, self.time_col])
            ['int_appeared']
            .agg(set)
            .str.join('')
        )
        
        return df
    
    @property
    def bau_list(self):
        
        df = (
            self.bau_df
            .reset_index(level=self.intervention_col)
            .rename({self.intervention_col : 'int_appeared'}, axis=1)
            ['int_appeared']
        )
        
        return df
        
    
    def plot_time(self, 
                  fig = None, 
                  ax = None,
                  save = None,
                  cumulative = False,
                  cumulative_discount = False):
        """Plots optimal benefits and costs across time after model optimization

        :param fig: matplotlib figure, defaults to None
        :type fig: matplotlib.figure, optional
        :param ax: matplotlib axis to use, defaults to None
        :type ax: matplotlib.axis, optional
        :param save: whether to save the figure, defaults to None
        :type save:  str for file path, optional
        """        
        
        p = Plotter(self)
                
        if cumulative:
            return p._plot_lines(to_plot = ['cumulative_benefits', 'cumulative_costs'],
                    title= "Optima over Time",
                    xlabel = 'Time',
                    ylabel = self.benefit_title,
                    twin =True,
                    twin_ylabel= "Currency",
                    save = save,
                    legend = ['Cumm. ' + self.benefit_title,
                            'Cumm. Costs'],
                    figure=fig,
                    axis=ax)
        elif cumulative_discount:
            return p._plot_lines(to_plot = ['cumulative_discounted_benefits', 'cumulative_discounted_costs'],
                    title= "Optima over Time",
                    xlabel = 'Time',
                    ylabel = self.benefit_title,
                    twin =True,
                    twin_ylabel= "Currency",
                    save = save,
                    legend = ['Cumm. Dis. '+ self.benefit_title,
                            'Cumm. Dis. Costs'],
                    figure=fig,
                    axis=ax)
        else:
            return p._plot_lines(to_plot = ['opt_benefit', 'opt_costs'],
                                title= "Optima over Time",
                                xlabel = 'Time',
                                ylabel = self.benefit_title,
                                twin =True,
                                twin_ylabel= "Currency",
                                save = save,
                                legend = ['Optimal ' + self.benefit_title,
                                        'Optimal Costs'],
                                figure=fig,
                                axis=ax)

    def plot_bau_time(self,
                      opt_variable = 'b',
                      fig = None,
                      ax = None,
                      save = None):
        
        if ax is None:
            fig, ax = plt.subplots()

        p = Plotter(self)
        
        if opt_variable == 'b':
            opt = 'opt_benefit'
            bau_col = self.benefit_col
            title = "Optimal " + self.benefit_title + " vs. BAU"
        elif opt_variable == 'c':
            opt = 'opt_costs'
            bau_col = self.cost_col
            title = "Optimal Costs vs. BAU"
        elif opt_variable == 'cdb':
            opt = 'cumulative_discounted_benefits'
            bau_col = 'discounted_benefits'
            title = 'Cumulative Discounted ' + self.benefit_title
        elif opt_variable == 'cdc':
            opt = 'cumulative_discounted_costs'
            bau_col = 'discounted_costs'
            title = 'Cumulative Discounted Costs'
        elif opt_variable == 'cb':
            opt = 'cumulative_benefits'
            bau_col = self.benefit_col
            title = 'Cumulative ' + self.benefit_title      
        elif opt_variable == 'cc':
            opt = 'cumulative_costs'
            bau_col = self.cost_col
            title = 'Cumulative Costs'
        else:
            raise Exception("Not one of the allowed variables for map plotting. Try again.")
        
        if opt_variable in ['cdb', 'cdc', 'cb', 'cc']:
            
            bench_df = (
                self.bau_df
                .groupby([self.time_col])
                .sum().cumsum()
                .assign(bench_col = lambda df: df[bau_col])
                )
            
        else:
            bench_df = (
                self.bau_df
                .assign(bench_col = lambda df: df[bau_col])
                .groupby([self.time_col])
                .sum()
                        )

        p._plot_lines(to_plot = opt,
                    title= title,
                    xlabel = 'Time',
                    figure=fig,
                    axis=ax)
        
        bench_df['bench_col'].plot(ax=ax)
        
        ax.legend(['Optimal', 'BAU'])
        ax.set_xlabel('Time')

        if save is not None:
            plt.savefig(save)

    def plot_opt_val_hist(self, 
                          fig = None, 
                          ax = None, 
                          save = None):
        """A histogram of the optimally chosen interventions

        :param fig: figure instance to use, defaults to None
        :type fig: matplotlib.figure, optional
        :param ax: axis instance to use, defaults to None
        :type ax: matplotlib.axis, optional
        :param save: whether to save the figure, defaults to None
        :type save: str of file path, optional
        """        
        
        p = Plotter(self)
        
        return p._plot_hist(to_plot = 'opt_vals',
                            title = "Optimal Choices",
                            xlabel = "Time",
                            ylabel= "",
                            figure = fig,
                            axis = ax,
                            save = save)
        
    def plot_chloropleth(self,
                         intervention = None,
                         time = None,
                         optimum_interest = 'b',
                         map_df = None,
                         merge_key = None,
                         intervention_bubbles = False,
                         intervention_bubble_names = None,
                         save = None):
        """Creates a chloropleth map of the specified intervention and time period for the optimal variable. 
        If more than one intervention is specified, then aggregates them. If more than one time period is specified, then creates a subplots of len(time) and show each.

        :param intervention: interventions to use, defaults to slice(None)
        :type intervention: str or list, optional
        :param time: time periods to plot, defaults to None
        :type time: int or list, optional
        :param optimum_interest: optimum variable to use. 
        Options include: 'b' for optimal benefits, 'c' for optimal costs, and 'v' for optimal variable, defaults to 'b'
        :type optimum_interest: str, optional
        :param map_df: geopandas dataframe with geometry information, defaults to None
        :type map_df: geopandas.GeoDataFrame, optional
        :param merge_key: key to merge on to geo dataframe, defaults to None
        :type merge_key: str or list, optional
        :param save: whether to save the figure, defaults to None
        :type save: str of file path, optional
        """        
        
        if intervention is None:
            intervention = self.optimal_interventions
        
        p = Plotter(self)
                
        if optimum_interest == 'b':
            opt = 'opt_benefit'
            title = self.benefit_title
        elif optimum_interest == 'c':
            opt = 'opt_costs'
            title = "Optimal Costs"
        elif optimum_interest == 'v':
            opt = 'opt_vals'
            title = "Optimal Interventions"
        elif optimum_interest == 'cdb':
            opt = 'cumulative_discounted_benefits'
            title = 'Cumulative Discounted ' + self.benefit_title
        elif optimum_interest == 'cdc':
            opt = 'cumulative_discounted_costs'
            title = 'Cumulative Discounted Costs'
        elif optimum_interest == 'cb':
            opt = 'cumulative_benefits'
            title = 'Cumulative ' + self.benefit_title      
        elif optimum_interest == 'cc':
            opt = 'cumulative_costs'
            title = 'Cumulative Costs'
        else:
            raise Exception("Not one of the allowed variables for map plotting. Try again.")
        
        
        plotter = p._plot_chloropleth_getter(time = time)
        plot = plotter(data = self.opt_df,
                                          intervention = intervention,
                                            time = time,
                                            optimum_interest=opt,
                                            map_df = map_df,
                                            merge_key=merge_key,
                                            aggfunc = 'sum',
                                            title = title,
                                            intervention_bubbles = intervention_bubbles,
                                            intervention_bubble_names = intervention_bubble_names,
                                            save = save)
        # return plot

    def plot_grouped_interventions(self, 
                                data_of_interest = 'benefits', 
                                title = None,
                                intervention_subset = slice(None),
                                save = None):
        """Shows Optimal level of benefits or costs in a grouped bar plots for every optimally chosen variable across regions.

        :param data_of_interest: variable to show, defaults to 'benefits'
        :type data_of_interest: str, optional
        :param title: title for resulting plot, defaults to None
        :type title: str, optional
        :param intervention_subset: subset of interventions to show on bar plot, defaults to slice(None)
        :type intervention_subset: str ot list, optional
        :param save: whether to save the figure, defaults to None
        :type save: str of filepath, optional
        """        
        
        p = Plotter(self)
            
        if data_of_interest == 'benefits':
            col_of_interest = 'opt_benefit'
        elif data_of_interest == 'costs':
            col_of_interest = 'opt_costs'
        
        p._plot_grouped_bar(intervention_col= self.intervention_col,
                            space_col = self.space_col,
                            col_of_interest= col_of_interest,
                            ylabel = "Optimal Level",
                            intervention_subset= intervention_subset,
                            save = save)
        
        
    def plot_map_benchmark(self,
                           intervention = None,
                           time = None,
                           optimum_interest = 'b',
                           bench_intervention = None,
                           map_df = None,
                           merge_key = None,
                           save = None,
                           intervention_in_title = True,
                           intervention_bubbles = False,
                           intervention_bubble_names = None,
                           millions = True,
                           bau_intervention_bubble_names = None,
                           ):
        """Maps the the optimal level on a map against a benchmark, optionally the BAU level chosen from ``minimum_benefit`` or ``total_funds``.

        :param intervention: interventions to map, defaults to slice(None)
        :type intervention: list, optional
        :param time: time periods to map, defaults to None
        :type time: list, optional
        :param optimum_interest: which optimal value to use. Options include 'b' (benefits), 'c' (costs), 'v' (variables), defaults to 'b'
        :type optimum_interest: str, optional
        :param data_bench: data to use for benchmark mapping, defaults to None
        :type data_bench: pandas.DataFrame, optional
        :param bench_intervention: interventions to use for benchmark, defaults to None
        :type bench_intervention: list, optional
        :param bench_col: column to use for benchmark, defaults to None
        :type bench_col: str, optional
        :param bench_merge_key: merge key for bench_df, defaults to None
        :type bench_merge_key: list, optional
        :param map_df: geo dataframe with geometry data, defaults to None
        :type map_df: geopandas.GeoDataFrame, optional
        :param merge_key: key to merge data from opt_df to geo dataframe, defaults to None
        :type merge_key: str or list, optional
        :param save: whether to save the figure, defaults to None
        :type save: str of file path, optional
        """  
        
        if intervention is None:
            intervention = self.optimal_interventions   
            
        if figsize is not None:   
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure(figsize=(10,12))
        
        gs = gridspec.GridSpec(2,2, height_ratios = [6,1])
        optimal = fig.add_subplot(gs[0,0])
        bench = fig.add_subplot(gs[0,1])
        cbar = fig.add_subplot(gs[1,:])
        
        p = Plotter(self)
        
        if optimum_interest == 'b':
            opt = 'opt_benefit'
            bench_col = self.benefit_col
            title = self.benefit_title
        elif optimum_interest == 'c':
            opt = 'opt_costs'
            bench_col = self.cost_col
            title = "Costs"
        elif optimum_interest == 'v':
            opt = 'opt_vals'
            title = "Interventions"
        elif optimum_interest == 'cdb':
            opt =  'cumulative_discounted_benefits'
            bench_col = 'discounted_benefits'
            title = 'Cumulative Discounted ' + self.benefit_title
        elif optimum_interest == 'cdc':
            opt =  'cumulative_discounted_costs'
            title = 'Cumulative Discounted Costs'
            bench_col = 'discounted_costs'
        elif optimum_interest == 'cb':
            opt =  'cumulative_benefits'
            title = 'Cumulative ' + self.benefit_title   
            bench_col = self.benefit_col   
        elif optimum_interest == 'cc':
            opt =  'cumulative_costs'
            title = 'Cumulative Costs'
            bench_col = self.cost_col
        else:
            raise Exception("Not one of the allowed variables for map plotting. Try again.")
        
        if bench_intervention is None:
            bench_intervention = self.minimum_benefit
        
        if merge_key is None:
            merge_key = self.space_col
            
        if optimum_interest in ['cdb', 'cdc', 'cb', 'cc']:
            
            bench_df = self.bau_df.assign(bench_col = lambda df: (df
                                                            .groupby([self.intervention_col, 
                                                                    self.space_col])
                                                            [bench_col]
                                                            .transform('cumsum')))
            
        else:
            bench_df = self.bau_df.assign(bench_col = lambda df: df[bench_col])
        
        y = 1.05
        
        if intervention_in_title:
            title = title + f"\nOptimal Interventions:\n{', '.join(intervention)}"
            y = y + .05
            
        fig.suptitle(title, y=y)
        plotter = p._plot_chloropleth_getter(time)
        
        # Get min and max values for color map
        opt_max = self.opt_df[opt].max()
        opt_min = self.opt_df[opt].min()
        
        bench_max = bench_df['bench_col'].max()
        bench_min = bench_df['bench_col'].min()
        
        vmax = max(opt_max, bench_max)
        vmin = min(opt_min, bench_min)
        
        if intervention_bubbles:
            bau_intervention_bubbles = 'bau'
        else:
            bau_intervention_bubbles = False
        
        
        plotter(data = self.opt_df,
                    intervention = intervention,
                    time = time,
                    optimum_interest=opt,
                    map_df = map_df,
                    merge_key=merge_key,
                    aggfunc = 'sum',
                    ax = optimal,
                    cax = cbar,
                    title = "Optimal Scenario",
                    intervention_bubbles = intervention_bubbles,
                    intervention_bubble_names = intervention_bubble_names,
                    vmin = vmin,
                    vmax = vmax,
                    legend_kwds = {'orientation' : 'horizontal'})
        
        plotter(data = bench_df,
                        intervention = bench_intervention,
                        time = time,
                        optimum_interest= 'bench_col',
                        map_df = map_df,
                        merge_key=merge_key,
                        aggfunc = 'sum',
                        ax = bench,
                        show_legend = False,
                        title = f"BAU* Scenario",
                         vmin = vmin,
                        vmax = vmax,
                        intervention_bubbles = bau_intervention_bubbles,
                        intervention_bubble_names = bau_intervention_bubble_names)
        
        plt.tight_layout()
        
        fig_text = 'Note: Colors describe ' + title
        
        if millions:
            fig_text = fig_text + ' (in millions)'
        
        # if intervention_bubble_names:
        #     fig_text = fig_text + '\nBAU* scenario made up of ' + ', '.join(intervention_bubble_names)
        
        fig.text(0.5,-.05, fig_text, ha='center')
                
        if save is not None:
            plt.savefig(save, dpi = 300, bbox_inches="tight")
            
                    