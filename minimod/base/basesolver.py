# Imports for local packages
#from types import NoneType
import matplotlib
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
import geopandas as gpd
import numpy as np
import mip
import re

import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec

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
                benefit_col (str, optional):benefit data column. Defaults to 'benefits'.
                cost_col (str, optional): cost data column. Defaults to 'costs'.
                intervention_col (str, optional): intervention data column. Defaults to 'intervention'.
                space_col (str, optional): space/region data column. Defaults to 'space'.
                time_col (str, optional): time period data column. Defaults to 'time'.
                interest_rate_cost (float, optional): interest rate of costs. Defaults to 0.0.
                benefit_title (str, optional): title for benefits to put in plots and reports. Defaults to "Benefits".
        
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
    

    def _discounted_sum_all(self, col_name:str) -> mip.LinExpr:
       
        """Multiply each ``mip_var`` in the data by benefits or costs (``data``) and then create a ``mip`` expression from it.

        Args:
            col_name (str): name of column with benefits or costs data

        Returns:
            mip.LinExpr: ``mip`` Expression
        """    
        
        eq = (self._df['mip_vars'] * self._df[col_name]).agg(mip.xsum)

        return eq

    def _discounted_sum_over(self, col_name: str, over: str) -> pd.DataFrame :
        """Abstract function used for constructing the objective function and main constraint of the model

        Args:
            col_name (str): name of column with benefits or costs data
            over (str): attribute used to group data by (e.g. time)

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
            data (pd.DataFrame, optional): data. Defaults to None.
            intervention (str, optional):intervention column. Defaults to "intervention".
            space (str, optional): space/region column. Defaults to "space".
            time (str, optional): time period column. Defaults to "time".
            benefits (str, optional): benefits column. Defaults to "benefits".
            costs (str, optional): cost column. Defaults to "costs".
        
        Returns:
            (): dataframe ready to be used in the problem

        
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
            sol_num (None, optional): _description_. Defaults to None.
        """
        
        self.opt_df = self.model.process_results(self.benefit_col, 
                                            self.cost_col, 
                                            self.intervention_col,
                                            self.space_col,
                                            sol_num=sol_num)


    def report(self, sol_num:int=None, quiet:bool=False) -> str:
        """Prints out a report of optimal model parameters and useful statistics.

        Args:
            sol_num (int, optional): _description_. Defaults to None.
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
                  fig: matplotlib.figure = None, 
                  ax: matplotlib.axis= None,
                  save: str = None,
                  cumulative: bool = False,
                  cumulative_discount: bool = False) -> matplotlib.figure:
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
                      fig: matplotlib.figure = None,
                      ax: matplotlib.axis = None,
                      save: str = None):
        """Plots benefits and costs of optimal and benchark interventions across time 

        Args:
            opt_variable (str, optional): _description_. Defaults to 'b'.
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
                          fig: matplotlib.figure = None, 
                          ax: matplotlib.axis = None, 
                          save: str = None) -> matplotlib.figure:
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
            intervention (str, optional): interventions to use. Defaults to None.
            time (Union[int,list], optional): time periods to plot. Defaults to None.
            optimum_interest (str, optional): optimal variable to use (Options include: 'b' for optimal benefits, 'c' for optimal costs, and 'v' for optimal variable). Defaults to 'b'.
            map_df (geopandas.GeoDataFrame, optional): geopandas dataframe with geometry information. Defaults to None.
            merge_key (Union[str,list], optional): _description_. Defaults to None.
            intervention_bubbles (bool, optional): _description_. Defaults to False.
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
        
        fig = plt.figure()
        
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
            
                    