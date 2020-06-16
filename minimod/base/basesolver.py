# Imports for local packages
from minimod.utils.exceptions import (
    MissingData,
    NotPandasDataframe,
    MissingOptimizationMethod,
)

from minimod.version import __version__

from minimod.utils.summary import OptimizationSummary
from minimod.utils.plotting import Plotter
from minimod.utils.suppress_messages import suppress_stdout_stderr

from minimod.base.bau_constraint import BAUConstraintCreator
from minimod.base.model import Model

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
        all_time=None, 
        all_space=None, 
        time_subset = None, 
        space_subset = None,
        strict = False,
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
        
        self.model = Model(data = self._df, sense = sense, solver_name=self.solver_name, show_output=self.show_output)
        
        self.benefit_col = benefit_col
        self.cost_col = cost_col
        self.intervention_col = intervention_col
        self.space_col = space_col
        self.time_col = time_col
        
        if self.show_output:
            print("[Note]: Creating Base Model with constraints")
            
        self.bau = BAUConstraintCreator()

        ## Create base model
        self.model.base_model_create(intervention_col, 
                                    space_col, 
                                    time_col, 
                                    all_time=all_time, 
                                    all_space=all_space, 
                                    time_subset = time_subset, 
                                    space_subset = space_subset,
                                    strict = strict)
        
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
        
    def _discounted_sum_all(self, data):
        """Multiply each ``mip_var`` in the data by benefits or costs (``data``) and then create a ``mip`` expression from it.

        :param data: dataset of benefits and costs
        :type data: pandas.DataFrame
        :return: ``mip`` Expression
        :rtype: ``mip.LinExpr``
        """        

        eq = mip.xsum(
            self._df["mip_vars"].loc[k, j, t] * data[k, j, t]
            for (k, j, t) in self._df.index.values
        )

        return eq

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
        
        self.opt_df = self.model.process_results(self.benefit_col, self.cost_col)
        
        (self.objective_value,
         self.objective_values, 
         self.objective_bound, 
         self.num_solutions, 
         self.num_cols, 
         self.num_rows, 
         self.num_int, 
         self.num_nz, 
         self.status) = self.model.get_model_results()
        
    def write(self, filename="model.lp"):
        
        self.model.write(filename)

    def report(self):
        """Prints out a report of optimal model parameters and useful statistics.
        """        

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
    
    def plot_time(self, 
                  fig = None, 
                  ax = None,
                  save = None):
        """Plots optimal benefits and costs across time after model optimization

        :param fig: matplotlib figure, defaults to None
        :type fig: matplotlib.figure, optional
        :param ax: matplotlib axis to use, defaults to None
        :type ax: matplotlib.axis, optional
        :param save: whether to save the figure, defaults to None
        :type save:  str for file path, optional
        """        
        
        p = Plotter(self)
        
        return p._plot_lines(to_plot = ['opt_benefit', 'opt_costs'],
                             title= "Optima over Time",
                             xlabel = 'Time',
                             ylabel = self.benefit_title,
                             twin =True,
                             twin_ylabel= "Currency",
                             save = save,
                             legend = ['Optimal Benefits',
                                       'Optimal Costs'],
                             figure=fig,
                             axis=ax)
        
    # def plot_bau_time(self,
    #                   opt_variable = None,
    #                   fig = None,
    #                   ax = None,
    #                   save = None):
        
    #     p = Plotter(self)
        
    #     if re.match(r"ben", opt_variable):
    #         bau_var = 'discounted_benefits'
        
    #     return p._plot_lines(to_plot = [opt_variable, bau_var],
    #                          title= "Optimal vs. BAU",
    #                          xlabel = 'Time',
    #                          save = save,
    #                          legend = ['Optimal ',
    #                                    'Optimal Costs'],
    #                          figure=fig,
    #                          axis=ax)
        
        

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
                         intervention = slice(None),
                         time = None,
                         optimum_interest = 'b',
                         map_df = None,
                         merge_key = None,
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
                                            save = save)
        return plot

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
                           intervention = slice(None),
                           time = None,
                           optimum_interest = 'b',
                           data_bench = None,
                           bench_intervention = None,
                           bench_col = None,
                           bench_merge_key = None,
                           map_df = None,
                           merge_key = None,
                           save = None,
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
        
        fig = plt.figure()
        
        gs = gridspec.GridSpec(2,2, height_ratios = [6,1])
        optimal = fig.add_subplot(gs[0,0])
        bench = fig.add_subplot(gs[0,1])
        cbar = fig.add_subplot(gs[1,:])
        
        p = Plotter(self)
        
        if optimum_interest == 'b':
            opt = 'opt_benefit'
            title = self.benefit_title
        elif optimum_interest == 'c':
            opt = 'opt_costs'
            title = "Costs"
        elif optimum_interest == 'v':
            opt = 'opt_vals'
            title = "Interventions"
        else:
            raise Exception("Not one of the allowed variables for map plotting. Try again.")
        
        fig.suptitle(title, y=1.05)
        plotter = p._plot_chloropleth_getter(time)
        
        # Get min and max values for color map
        opt_max = self.opt_df[opt].max()
        opt_min = self.opt_df[opt].min()
        
        bench_max = data_bench[bench_col].max()
        bench_min = data_bench[bench_col].min()
        
        vmax = max(opt_max, bench_max)
        vmin = min(opt_min, bench_min)
        
        
        optimal = plotter(data = self.opt_df,
                    intervention = intervention,
                    time = time,
                    optimum_interest=opt,
                    map_df = map_df,
                    merge_key=merge_key,
                    aggfunc = 'sum',
                    ax = optimal,
                    cax = cbar,
                    title = "Optimal Scenario",
                    vmin = vmin,
                    vmax = vmax,
                    legend_kwds = {'orientation' : 'horizontal'})
        
        bench = plotter(data = data_bench,
                        intervention = bench_intervention,
                        time = time,
                        optimum_interest= bench_col,
                        map_df = map_df,
                        merge_key=bench_merge_key,
                        aggfunc = 'sum',
                        ax = bench,
                        show_legend = False,
                        title = f"Benchmark Scenario\n(using {bench_intervention})",
                         vmin = vmin,
                        vmax = vmax)
        
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save, dpi = p.dpi)
        