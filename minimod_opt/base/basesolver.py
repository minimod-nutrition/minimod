# Imports for local packages
from typing import Union, Type, List, Iterable
from time import time
import matplotlib as mpl

from minimod.utils.exceptions import (
    MissingData,
    NotPandasDataframe,
    MissingOptimizationMethod,
)
from functools import reduce
from pandas import DataFrame

from minimod.utils.summary import OptimizationSummary
from minimod.base.bau_constraint import BAUConstraintCreator
from minimod.utils.plotting import Plotter
from minimod.utils.suppress_messages import suppress_stdout_stderr
from mip.cbc import OptimizationStatus

import matplotlib.pyplot as plt

import pandas as pd
import geopandas as gpd
import numpy as np
import mip
import re

import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec
import matplotlib.ticker as tick
from dataclasses import dataclass
import textwrap
from adjustText import adjust_text



@dataclass
class SupplyCurve:
    
    supply_curve: DataFrame
    full_population: int
    bau: str
    data: DataFrame
    ec_range: Iterable



from typing import Any
from typing import Union

class BaseSolver:

    
    def __init__(
        self,
        data: pd.DataFrame,
        benefit_col: str = 'benefits',
        cost_col: str = 'costs',
        intervention_col: str = 'intervention',
        space_col: str = 'space',
        time_col: str = 'time',
        interest_rate_cost: float = 0.0,  # Discount factor for costs
        interest_rate_benefit: float = 0.03,  # Discount factor for benefits 
        va_weight: float = 1.0,  # VA Weight
        sense: str = None,  # MIP optimization type (maximization or minimization)
        solver_name: str = mip.CBC,  # Solver for MIP to use
        show_output: bool = True,
        benefit_title: str = "Benefits",
    ):       
      
        """The base solver for the Optimization. This sets up the basic setup of the model, which includes:
        - data handling
        - BAU constraint creation
        - base model constraint creation

        Args:
                data (pd.DataFrame): dataframe with benefits and cost data.
                benefit_col (str, optional): name of dataframe's column with benefit data. Defaults to 'benefits'.
                cost_col (str, optional): name of dataframe's column with cost data. Defaults to 'costs'.
                intervention_col (str, optional): name of dataframe's column with intervention data. Defaults to 'intervention'.
                space_col (str, optional): name of dataframe's column with space/region data . Defaults to 'space'.
                time_col (str, optional): name of dataframe's column with time period data . Defaults to 'time'.
                interest_rate_cost (float, optional): interest rate of costs. Defaults to 0.0.
                benefit_title (str, optional): title for benefits to use in plots and reports. Defaults to "Benefits".
        
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
        
        self.message = f"""
                MiniMod Nutrition Intervention Tool
                Optimization Method: {str(self.sense)}
                Version: {__version__}
                Solver: {str(self.solver_name)},
                Show Output: {self.show_output}
                
                """
        
        if self.show_output:
            print(self.message)
        
    

    def _discounted_sum_all(self, col_name:str) -> mip.LinExpr:
       
        """Multiply each ``mip_var`` in the data by benefits or costs (``data``) and then create a ``mip`` expression from it.

        Args:
            col_name (str): name of dataframe's column with benefits or costs data

        Returns:
            mip.LinExpr: ``mip`` Expression
        """    
        
        eq = (self._df['mip_vars'] * self._df[col_name]).agg(mip.xsum)

        return eq

    def _discounted_sum_over(self, col_name: str, over: str) -> pd.DataFrame :
        """Abstract function used for constructing the objective function and main constraint of the model

        Args:
            col_name (str): name of dataframe's column with benefits or costs data
            over (str): name of dataframe's column with attribute used to group data by (e.g. time)

        Returns:
            (pd.Dataframe): pd.Dataframe with mip variables as observations
        """
        
        # Merge data with self._df   
        eq = (self._df['mip_vars'] * self._df[col_name]).groupby(over).agg(mip.xsum)
        
        return eq.to_frame().rename({0 : col_name + '_vars'}, axis=1)

 
    def _is_dataframe(self, data: Any):
        """Checks if input dataset is a ``pandas.DataFrame``

        Args:
            data (Any): input data

        Raises:
            NotPandasDataframe: Exception if not a ``pandas.DataFrame``
        """    

        if not isinstance(data, pd.DataFrame):
            raise NotPandasDataframe(
                "[Error]: Input data is not a dataframe. Please input a dataframe."
            )


    def _process_data(
        self,
        data: pd.DataFrame = None,
        intervention: str ="intervention",
        space: str = "space",
        time: str = "time",
        benefits: str = "benefits",
        costs: str = "costs",
    ) -> pd.DataFrame :      
        """Processes the input data by creating discounted benefits and costs.

        Args:
            data (pd.DataFrame, optional): raw data to be processed. Defaults to None.
            intervention (str, optional): name of dataframe's column with intervention data. Defaults to "intervention".
            space (str, optional): name of dataframe's column with space/region data. Defaults to "space".
            time (str, optional): name of dataframe's column with time period data. Defaults to "time".
            benefits (str, optional): name of dataframe's column with benefits data. Defaults to "benefits".
            costs (str, optional): name of dataframe's column with cost data. Defaults to "costs".
        
        Returns:
            (pd.DataFrame): dataframe ready to be used in the problem

        
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
        """This function defines the constraints for the mips model.
        To be overridden by BenefitSolver and CostSolver classes.
        """
        self.constraint_called = 0

    def _objective(self):
        """This function defines the objective function for a model.
        To be overridden by BenefitSolver and CostSolver classes.
        """
        pass
        

    def _fit(self, **kwargs) -> str:
        """Fits data to model. The instantiation of the class creates the base model. Uses ``mip.optimize`` to find the optimal point.

        Args:
            *kwargs: Other parameters to send to mip.optimize

        Returns:
            str: return self
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
        
    def write(self, filename:str="model.lp"):
        """Save model to file

        Args:
            filename (str, optional):name of the file. Defaults to "model.lp".
        """
        
        self.model.write(filename)
        
    def process_results(self, sol_num:int=None):
        """Processes results of optimization to be used in visualization and reporting functions

        Args:
            sol_num (int, optional): index of solution. Defaults to None.
        """
        
        self.opt_df = self.model.process_results(self.benefit_col, 
                                            self.cost_col, 
                                            self.intervention_col,
                                            self.space_col,
                                            sol_num=sol_num)


    def report(self, sol_num:int=None, quiet:bool=False) -> str:
        """Prints out a report of optimal model parameters and useful statistics.

        Args:
            sol_num (int, optional): index of solution to be displayed. Defaults to None.
            quiet (bool, optional): whether we want the report printed out or not. Defaults to False.
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
    def optimal_interventions(self) -> list:
        opt_intervention = (
            self.opt_df
            .loc[lambda df: df['opt_vals']>0]
            .index
            .get_level_values(level=self.intervention_col)
            .unique()
            .tolist()
        )
        """Outputs the unique set of optimal interventions as a list

        Returns:
            list: The list of optimal interventions
        """
        
        return opt_intervention
    
    @property
    def _intervention_list_space_time(self) -> pd.DataFrame:
        """Returns a data frame with multindex (space_col, time_col) where each row is the optimal intervention.

        Returns:
            pd.DataFrame: A dataframe where each row is the optimal intervention for each time period and space
        """
        
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
    def bau_list(self) -> pd.DataFrame:
        """Returns a dataframe with the name of the bau intervention. Mostly done for compatibility with other methods.

        Returns:
            pd.DataFrame: dataframe with the name of the bau intervention
        """
        
        df = (
            self.bau_df
            .reset_index(level=self.intervention_col)
            .rename({self.intervention_col : 'int_appeared'}, axis=1)
            ['int_appeared']
        )
        
        return df
     
        
    def plot_time(self, 
                  fig: mpl.figure = None, 
                  ax: mpl.axis= None,
                  save: str = None,
                  cumulative: bool = False,
                  cumulative_discount: bool = False) -> mpl.figure:
        """Plots optimal benefits and costs across time after model optimization

        Args:
            fig (matplotlib.figure, optional): matplotlib figure. Defaults to None.
            ax (matplotlib.axis, optional): matplotlib axis to use. Defaults to None.
            save (str, optional): path to save the figure. Defaults to None.
            cumulative (bool, optional): whether to plot cumulative benefits or costs. Defaults to False.
            cumulative_discount (bool, optional): whether to plot cumulative benefits or costs, discounted. Defaults to False.

        Returns:
            matplotlib.figure: figure with optimal benefits and cost across time
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
                      opt_variable: str = 'b',
                      fig: mpl.figure = None,
                      ax: mpl.axis = None,
                      save: str = None):
        """Plots benefits and costs of optimal and benchark interventions across time 

        Args:
            opt_variable (str, optional): optimal variable to be plotted, where
                b = optimal benefits
                c = 'optimal costs
                cdb = cumulative discounted benefits
                cdc = cumulative discounted costs
                cb = cumulative benefits
                cc = cumulative costs
            Defaults to 'b'.
            fig (matplotlib.figure, optional): matplotlib figure. Defaults to None.
            ax (matplotlib.axis, optional):matplotlib axis to use. Defaults to None.
            save (str, optional): path to save the figure. Defaults to None.

        Raises:
            Exception: not one of the allowed variables for map plotting
        """
        
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
                          fig: mpl.figure = None, 
                          ax: mpl.axis = None, 
                          save: str = None) -> mpl.figure:
        """A histogram of the optimally chosen interventions

        Args:
            fig (matplotlib.figure, optional): figure instance to use. Defaults to None.
            ax (matplotlib.axis, optional): axis instance to use. Defaults to None.
            save (str, optional): path to save the figure. Defaults to None.

        Returns:
            matplotlib.figure: histogram figure
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
                         intervention: str = None,
                         time: Union[int,list] = None,
                         optimum_interest: str = 'b',
                         map_df: gpd.GeoDataFrame  = None,
                         merge_key: Union[str,list] = None,
                         intervention_bubbles: bool = False,
                         intervention_bubble_names: Union[str,list] = None,
                         save: str = None):
        """Creates a chloropleth map of the specified intervention and time period for the optimal variable. 
        If more than one intervention is specified, then aggregates them. If more than one time period is specified, then creates a subplots of len(time) and show each.

        Args:
            intervention (str, optional): intervention to use. Defaults to None.
            time (Union[int,list], optional): time periods to plot. Defaults to None.
            optimum_interest (str, optional): optimal variable to use (Options include: 'b' for optimal benefits, 'c' for optimal costs, and 'v' for optimal variable). Defaults to 'b'.
            map_df (geopandas.GeoDataFrame, optional): geopandas dataframe with geometry information. Defaults to None.
            merge_key (Union[str,list], optional): column to merge geo-dataframe. Defaults to None.
            intervention_bubbles (bool, optional): whether to show optimal intervention names in map. Defaults to False.
            intervention_bubble_names (Union[str,list], optional): key to merge on to geo dataframe. Defaults to None.
            save (str, optional): path to save map. Defaults to None.

        Raises:
            Exception: Not one of the allowed variables for map plotting
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
                                    data_of_interest: str = 'benefits', 
                                    title: str = None,
                                    intervention_subset: Union[str,list] = slice(None),
                                    save: str = None):
        """Shows Optimal level of benefits or costs in a grouped bar plots for every optimally chosen variable across regions.

        Args:
            data_of_interest (str, optional): variable to show. Defaults to 'benefits'.
            title (str, optional):title for resulting plot. Defaults to None.
            intervention_subset (Union[str,list], optional): subset of interventions to show on bar plot. Defaults to slice(None).
            save (str, optional): path to save the figure. Defaults to None.
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
                           intervention: list = None,
                           time: list = None,
                           optimum_interest: str = 'b',
                           bench_intervention: list = None,
                           map_df: gpd.GeoDataFrame = None,
                           merge_key: Union[str,list] = None,
                           save: str = None,
                           intervention_in_title: bool = True,
                           intervention_bubbles: bool = False,
                           intervention_bubble_names: Union[str,list] = None,
                           millions: bool = True,
                           bau_intervention_bubble_names: Union[str,list] = None
                           ):
        """Maps the optimal level on a map against a benchmark, optionally the BAU level chosen from ``minimum_benefit`` or ``total_funds``.

        Args:
            intervention (list, optional): interventions to map. Defaults to None.
            time (list, optional): time periods to map. Defaults to None.
            optimum_interest (str, optional):  optimal value to use. Options include 'b' (benefits), 'c' (costs), 'v' (variables). Defaults to 'b'.
            bench_intervention (list, optional): interventions to use for benchmark. Defaults to None.
            map_df (geopandas.GeoDataFrame, optional):  geo dataframe with geometry data. Defaults to None.
            merge_key (Union[str,list], optional): key to merge data from opt_df to geo dataframe. Defaults to None.
            save (str, optional): path to save the map. Defaults to None.
            intervention_in_title (bool, optional): True if intervention name will be included in the title of the figure. Defaults to True.
            intervention_bubbles (bool, optional): True if intervention bubbles. Defaults to False.
            intervention_bubble_names (Union[str,list], optional): names of intervention bubbles. Defaults to None.
            millions (bool, optional): True if values displayed in millions. Defaults to True.
            bau_intervention_bubble_names (Union[str,list], optional): name for bau intervention bubble. Defaults to None.

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
            plt.savefig(save, dpi = p.dpi, bbox_inches="tight")
    
    @classmethod  
    def supply_curve(cls, data, 
                    full_population,
                    bau,
                    all_space,
                    all_time,
                    time_subset,
                    benefit_col='effective_coverage',
                    cost_col='cost',
                    intervention_col='intervention',
                    space_col='space',
                    time_col='time',
                    ec_range=None,
                    above_ul = False,
                    **kwargs): 
        
        if ec_range is None:
            ec_range = np.arange(.1,1,.1)
            
        
        ratio_to_constraint = lambda ratio: ratio*full_population
        
        model_dict = {}

        for _, benefit_constraint in enumerate([bau] + list(ec_range)):
            
            if isinstance(benefit_constraint, str):
                minimum_benefit = benefit_constraint
            else:
                minimum_benefit = ratio_to_constraint(benefit_constraint)
            
            c = cls(minimum_benefit = minimum_benefit,
                        data = data, 
                        benefit_col = benefit_col,
                        cost_col = cost_col,
                        intervention_col = intervention_col,
                        space_col = space_col,
                        time_col = time_col,
                        all_space =all_space, 
                        all_time = all_time,
                        time_subset = time_subset,
                        **kwargs)

            opt = c.fit()
            
            model_dict[benefit_constraint] = opt
            
        results_dict = {'benefit' : [],
                        'opt_benefits' : [],
                        'opt_costs' : [],
                        'opt_interventions' : [],
                        'convergence' : [],
                        'vas_regions' : []}
        if above_ul:
            results_dict['opt_above_ul'] = []

        
        for benefit_constraint, model in model_dict.items():

            model.report(quiet=True)
            results_dict['benefit'].append(benefit_constraint)
            results_dict['opt_benefits'].append(model.opt_df.opt_benefit_discounted.sum())
            results_dict['opt_costs'].append(model.opt_df.opt_costs_discounted.sum())
            results_dict['opt_interventions'].append(model.optimal_interventions)
            results_dict['convergence'].append(model.status)
            results_dict['vas_regions'].append(model.opt_df
                                               .query("opt_vals > 0")
                                               .query("index.get_level_values('intervention').str.contains('vas')")
                                               .index.get_level_values('region').unique().values.tolist())
            
            if above_ul:
                above_ul_df = (
                        data['above_ul']
                        .reset_index()
                        .assign(intervention = lambda df: df[intervention_col].str.lower())
                        .set_index([intervention_col, space_col, time_col])
                        )
                
                opt_above_ul = (model.opt_df['opt_vals'] * above_ul_df['above_ul']).sum()
                
                results_dict['opt_above_ul'].append(opt_above_ul)
                
        return SupplyCurve(pd.DataFrame(results_dict, index=[results_dict['opt_benefits'][0]/full_population] + list(ec_range)) 
                           , full_population=full_population,
                           bau=bau,
                           data=data,
                           ec_range=ec_range)        
        
        
    @classmethod      
    def plot_supply_curve(cls, 
                        supply_curve: SupplyCurve = None,
                          data: DataFrame = None, 
                    full_population: Union[int, float] = None,
                    bau: str=None,
                    all_space: List[float]=None,
                    all_time=None,
                    time_subset=None,
                    benefit_col='effective_coverage',
                    cost_col='cost',
                    intervention_col='intervention',
                    space_col='space',
                    time_col='time',
                    ec_range=None,
                    above_ul = False,
                    ec_thousands = 1_000,
                    ul_thousands = 1_000,
                    save=None,
                    splitter=None,
                    **kwargs):
        
        if supply_curve is None:
            supply_curve = cls.supply_curve(
                        data=data, 
                        full_population=full_population,
                        bau=bau,
                        all_space=all_space,
                        all_time=all_time,
                        time_subset=time_subset,
                        benefit_col=benefit_col,
                        cost_col=cost_col,
                        intervention_col=intervention_col,
                        space_col=space_col,
                        time_col=time_col,
                        ec_range=ec_range,
                        above_ul = above_ul,
                        **kwargs
                        )
        
        N_ec = len(supply_curve.ec_range)
        full_population = supply_curve.full_population
        bau = supply_curve.bau
        data=supply_curve.data
        supply_curve = supply_curve.supply_curve # Now that we have all info. make `supply_curve` just the dataframe

        # make nan of infeasible solutions
        supply_curve = supply_curve.replace(0, np.nan)
        
        only_bau_opt = supply_curve.query("benefit == @bau")
        
        # # get places where interventions change
        # transitions = supply_curve[~(supply_curve['opt_interventions'] == supply_curve['opt_interventions'].shift(-1))]
        
        # Now get additions of interventions by converting to set and doing difference
        supply_curve = (
            supply_curve
            .dropna()
            .assign(opt_interventions = lambda df: df['opt_interventions'].apply(lambda x: [i.split(' + ') for i in x]))
            .assign(opt_interventions = lambda df: df['opt_interventions'].apply(lambda x: reduce(lambda y, z: y + z, x)))
            .assign(opt_interventions = lambda df: df['opt_interventions'].apply(lambda x: set(x)))
            .assign(int_transitions_lag = lambda df: df['opt_interventions'].shift(-1))
            .dropna()
            .assign(transitions_plus = lambda df: df.apply(lambda col: col['int_transitions_lag'].difference(col['opt_interventions']), axis=1).shift(1).fillna(df['opt_interventions']))
            .assign(transitions_minus = lambda df: df.apply(lambda col: col['opt_interventions'].difference(col['int_transitions_lag']), axis=1).shift(1).fillna(df['opt_interventions']))
            .query("benefit != @bau")
            .loc[lambda df: df.index >= only_bau_opt.index.values[0]]
            )
        
        if above_ul:
            subplot_col = 2
        else:
            subplot_col = 1
        
        with plt.style.context('seaborn-whitegrid'):
            fig, ax = plt.subplots(subplot_col+1, 1, figsize=(5*subplot_col,12))
            
            
            if above_ul:
                ax0 = ax[0]
                ax1 = ax[1]
                ax_region=ax[2]
            else:
                ax0 = ax
                ax_region=ax[1]
                      
            supply_curve['opt_costs'].plot(ax=ax0)
                        
            ax0.set_xlabel('Effective Coverage (%)')

            ax0.set_xticks(supply_curve.index.tolist())
            
            ax0.set_xticklabels([f"{x*100:.0f}" for x in supply_curve.index.tolist()])
            
            ax0.ticklabel_format(axis='y', useMathText=True)
            
            ax0.yaxis.set_major_formatter(tick.FuncFormatter(lambda y, _: f"{y/ec_thousands:,.0f}"))
            
            ax0.set_title(f'Total Cost (x {ec_thousands:,.0f})')
            
            if bau is not None:
                if data is None:
                    raise Exception("If `bau` is specified, `data` must also be specified")
                
                bau_ec, bau_costs = BAUConstraintCreator().bau_df(data, bau, ['effective_coverage', 'costs']).sum()

                ax0.scatter(bau_ec/full_population, bau_costs, color='tab:green', marker='s')
                ax0.annotate("BAU", (bau_ec/full_population, bau_costs), xytext=(5, 5),  
                            textcoords="offset pixels", color='black')
                        
            opt_b, opt_c = only_bau_opt[['opt_benefits', 'opt_costs']].values.tolist()[0]
            
            ax0.annotate("Optimum", (opt_b/full_population, opt_c), xytext=(5, -10),  
                        textcoords="offset pixels", color='black')
            ax0.scatter(opt_b/full_population, opt_c,  color='tab:orange', marker="s")
            
            if above_ul:
                # Now get above_ul
                supply_curve['opt_above_ul'].plot(ax=ax1, color='tab:red')
                ax1.yaxis.set_major_formatter(tick.FuncFormatter(lambda y, _: f"{y/ul_thousands:,.0f}"))
                ax1.set_title(f'Population Above UL (x {ul_thousands:,.0f})')
                ax1.set_xticks(supply_curve.index.tolist())
                ax1.set_xticklabels([f"{x*100:.0f}" for x in supply_curve.index.tolist()])
                ax1.set_xlabel('Effective Coverage (%)')
            
            def message_writer(x):
                if len(x['transitions_plus']) != 0 and len(x['transitions_minus'])!=0:
                    message= "+ " + ', '.join(x['transitions_plus']) +  " - " + ", ".join(x['transitions_minus'])
                    message = '\n'.join(textwrap.wrap(message, width=50))
                    
                    # ns_needed = len(message)//25
                    
                    # # for i in range(ns_needed):
                    # #     message = message[i*25:i+25] + r'-len\n' + message[25+1+i:]
                    
                    return message
            
            # print(supply_curve)

            
            (
                supply_curve['vas_regions']
                .explode()
                .to_frame()
                .assign(yes=lambda df: \
                    (~df['vas_regions'].isnull())
                    .astype(int))
                .set_index('vas_regions', 
                           append=True)
                .unstack()
                .drop(columns=('yes', pd.NA))
                .plot.bar(stacked=True, legend=False, 
                          ax=ax_region, cmap='tab20')
                )
            
            # ax_region.set_xticks(supply_curve.index.tolist())
            ax_region.set_xticklabels([f"{x*100:.0f}" for x in supply_curve.index.tolist()],
                                      rotation=0)
            ax_region.set_xlabel('Effective Coverage (%)')
            ax_region.set_yticklabels([])
            ax_region.set_title("VAS Regions")
            
            texts = (
                supply_curve
                .assign(message = lambda df: df.apply(lambda x: message_writer(x), axis=1))
                .apply(lambda df: ax0.text(df.name+.01, df['opt_costs'], 
                                                s=df['message'],
                                                color='black', wrap=True), axis=1) 
                .values.tolist()
                )   
            
            adjust_text(texts, arrowprops=dict(arrowstyle='->', color='green'))
            
            figtext = f"Note: BAU refers to a nutritional intervention of {bau.title()}." \
            f" Optimum solution consists of {', '.join(only_bau_opt['opt_interventions'].values[0])}." \
            " Vitamin A Supplementation taking place at various level of effective coverage in: " \
                           f"{', '.join(list(set(np.concatenate(supply_curve['vas_regions'].values))))}"
                        
            txt = fig.text(.05, -.1, s='\n'.join(textwrap.wrap(figtext, width=100)))
                             
            handles, labels = ax_region.get_legend_handles_labels()
            
            new_labels = [i.split(',')[1].replace(')', '').strip() for i in labels]
            plt.legend(handles, new_labels, ncol=4, loc='lower center', 
                       bbox_to_anchor = (.5,-.6),
                       title='Regions')                 
                               
            plt.tight_layout()
            
            if save is not None:
                plt.savefig(save, dpi=300, bbox_inches='tight')
            
        return ax
        
        
