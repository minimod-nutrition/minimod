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
        interest_rate_cost=0.0,  # Discount factor for costs
        interest_rate_benefit=0.03,  # Discount factor for benefits 
        va_weight=1.0,  # VA Weight
        sense=None,  # MIP optimization type (maximization or minimization)
        solver_name=mip.CBC,  # Solver for MIP to use
        show_output = True,
        benefit_title = "Benefits",
    ):       
                
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
                                    all_time=None, 
                                    all_space=None, 
                                    time_subset = None, 
                                    space_subset = None)
        

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

        eq = mip.xsum(
            self._df["mip_vars"].loc[k, j, t] * data[k, j, t]
            for (k, j, t) in self._df.index.values
        )

        return eq

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
                discounted_benefits=lambda df: df["time_discount_benefits"]*df[benefits],
            )
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

        if self.show_output:
            print("[Note]: Optimizing...")

        self.model.optimize(**kwargs)  
        
        self.opt_df = self.model.process_results(self.benefit_col, self.cost_col)
        
        (self.objective_value, 
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
    
    def plot_time(self, 
                  fig = None, 
                  ax = None,
                  save = None):
        
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
        