import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from minimod.utils.exceptions import MissingOptimizationMethod
import functools
import geopandas as gpd
from matplotlib.patches import Ellipse

def plot_context(func):
    
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):   
        with mpl.rc_context(self.mpl_theme_dict):
            plot = func(self, *args, **kwargs)  
            return plot
    return wrapper

class Plotter:
    """This class is in charge of plotting the results of the `minimod`. 
    """     
               
    
    def __init__(self, model, dpi = 600):
        
        self.model = model
        self.dpi = dpi
        
        self.mpl_theme_dict = {
            'font.family' : 'serif',
            # 'yaxis.formatter' : mpl.ticker.FuncFormatter(lambda x, pos: "{:,}".format(x/1000) + 'K'),
            'savefig.dpi' : self.dpi
        }

        
    def _check_if_optimization(self):
        
        try:
            self.model.opt_df
        except NameError:
            raise MissingOptimizationMethod("Optimization Results have not been created. Please run the `fit` method.")
    
    def _define_axis_object(self, fig = None, ax = None):
        
        if ax is None:
            figure, axis = plt.subplots()
        else:
            figure, axis = fig, ax
        
        return figure, axis
    
    @plot_context         
    def _plot_process(self, figure = None, axis = None):
        
        self._check_if_optimization()
        
        fig, ax = self._define_axis_object(fig = figure, ax=axis)
        
        return fig, ax
    
    @plot_context       
    def _plot_lines(self, 
                    to_plot = None,
                    title = None,
                    xlabel = None,
                    ylabel = None,
                    figure = None, 
                    axis = None,
                    twin = False,
                    twin_ylabel = None,
                    save = None,
                    legend = None):
        
        fig, ax = self._plot_process(figure= figure, axis = axis)
        
        if not twin:
            
            (self.model.opt_df[to_plot]
            .groupby([self.model.time_col])
            .sum()
            .plot(title = title, 
                fig = fig, 
                ax=ax
                )
            )
            
        if twin:
            ax.plot(self.model.opt_df[to_plot[0]].groupby([self.model.time_col])
                    .sum(), 
                    color='red')
            
            ax2 = ax.twinx()
            ax2.plot(self.model.opt_df[to_plot[1]].groupby([self.model.time_col])
                     .sum(), 
                     color = 'blue')
            
            ax2.set_ylabel(twin_ylabel)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if twin:
            ax.legend(['Optimal Benefits'], loc= 'upper left')
            ax2.legend(['Optimal Costs'], loc = 'lower left')
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save)
        
        if twin:
            return fig, ax, ax2
        if not twin:
            return fig, ax
    
    @plot_context    
    def _plot_hist(self,
                   to_plot = None,
                   title = None,
                   xlabel = None,
                   ylabel = None,
                   figure = None,
                   axis = None, 
                   save = None):
        
        fig, ax = self._plot_process(figure =figure, axis = axis)
        
        (
            self.model.opt_df[to_plot]
            .groupby([self.model.time_col])
            .sum()
            .plot
            .bar(fig = fig, ax = ax, grid = True, width = 1)
         )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save)
        
        return fig, ax
    
    def _merge_shape_file(self, 
                          data = None,
                          map_df = None, 
                          merge_key = None):
        
        self._check_if_optimization()
        
        # Merge with `opt_df`
        
        df = (
            map_df
            .merge(
                data
                .reset_index(),
                left_on = [merge_key],
                right_on = [self.model.space_col]
            )
            # .set_index([self.model.intervention_col,
            #             self.model.space_col,
            #             self.model.time_col
            #             ])
        )
        
        return df
    
    def _shape_file_loc(self,
                        data = None,
                        intervention = None,
                        time = None):
        
        df = (data
              .loc[(intervention, slice(None), time ), :]
              )
        
        return df
    
    def _dissolve_interventions(self, 
                                data = None, 
                                aggfunc = None):
                
        return data.dissolve(by = [self.model.space_col, self.model.time_col], aggfunc = aggfunc)
        
    @plot_context
    def _plot_chloropleth(self, 
                          data = None,
                          intervention = None,
                          time = None,
                          optimum_interest = None,
                          map_df = None,
                          merge_key = None,
                          aggfunc = None,
                          title = None, 
                          ax = None,
                          save = None,
                          show_legend = True,
                          intervention_bubbles = False,
                          intervention_bubble_names = None,
                          **kwargs):
        
        if ax is None:
            fig, ax = plt.subplots()
                    
        df = (
            data
            .pipe(self._shape_file_loc, intervention = intervention, time = time)
            .groupby(self.model.space_col)
            .sum()
            .pipe(self._merge_shape_file, map_df = map_df, merge_key = merge_key)
        )
        
        
        df.plot(column = optimum_interest, 
                ax = ax, 
                legend = show_legend,
                **kwargs)
        
        if intervention_bubbles:
            
            if isinstance(intervention_bubbles, bool):
            
                df_bubble = (
                    df
                    .merge(self.model._intervention_list_space_time
                        .loc[(slice(None), time)], on = self.model.space_col)
                    .assign(centroid = lambda df: df['geometry'].centroid)

                )         
            
            elif intervention_bubbles == 'bau':
                df_bubble = (
                    df
                    .merge(self.model.bau_list
                        .loc[(slice(None), time)], on = self.model.space_col)
                    .assign(centroid = lambda df: df['geometry'].centroid)

                ) 
                
            df_bubble_final = (
                df_bubble
                .assign(**{k : df_bubble['int_appeared']
                        .str.extract(f'(?P<{k}>{k})') \
                            for k in intervention_bubble_names})
                .assign(bubble_name = lambda df: df[intervention_bubble_names]
                        .fillna('')
                        .apply(lambda row: '\n'.join(row), axis=1))
            )
            
            df_bubble_final.apply(lambda x: ax.annotate(text = x.bubble_name,
                                                        xy = x.centroid.coords[0],
                                                        size = 7,
                                                        color ='red'), 
                                  axis=1)
      
        ax.set_title(title)
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticklabels([])
        ax.set_yticks([])
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save)
            
        return ax        

    @plot_context        
    def _plot_multi_chloropleth(self, 
                                data = None,
                                time = None, 
                                intervention = None,
                                optimum_interest = None,
                                map_df = None,
                                merge_key = None,
                                aggfunc = None,
                                title = None,
                                axs = None,
                                save = None,
                                **kwargs):
        
        if time is None:
            time = (self.model.opt_df
                 .index
                 .get_level_values(level = self.model.time_col)
                 .unique()
                 .values
                 )
        
        mod = len(time) % 2
        
        if axs is None:
            fig, axs = plt.subplots(nrows = int(len(time)/2) + mod , 
                                    ncols=2,
                                    figsize = (10,20))
        
        
        for ax, plot in zip(np.array(axs).flatten(), time):
            
            ax = self._plot_chloropleth(data = data,
                                   intervention = intervention,
                                   time = plot,
                                   optimum_interest = optimum_interest,
                                   map_df = map_df, 
                                   merge_key = merge_key, 
                                   aggfunc = aggfunc,
                                   ax = ax,
                                   title = f"T = {plot}", 
                                   **kwargs)
            ax.set_xticklabels([])
            ax.set_xticks([])
            ax.set_yticklabels([])
            ax.set_yticks([])
            ax.set_title(title)
            
        plt.tight_layout()
        plt.savefig(save)
        
        return axs
    
    @plot_context
    def _plot_sim_hist(self, 
                       data,
                       benefit_col = None, 
                       cost_col = None,
                       benefit_title = None,
                       cost_title = None,
                       save = None):
        
        fig, ax = plt.subplots(1,2, figsize=(12,6))
        
        data[benefit_col].hist(ax = ax[0])
        data[cost_col].hist(ax = ax[1])
        
        ax[0].set_title(benefit_title)
        ax[1].set_title(cost_title)
        fig.suptitle("Simulation Distributions")
        
        if save is not None:
            plt.savefig(save, dpi=300)
        
        return fig, ax
    
    @plot_context
    def _plot_grouped_bar(self,
                          intervention_col = None,
                          space_col = None,
                          col_of_interest = None,
                          ylabel = None,
                          intervention_subset = None,
                          save = None,
                          ):
        
        plot = (
            self.model.opt_df
            [col_of_interest]
            .to_frame()
            .loc[(intervention_subset, slice(None), slice(None)), :]
            .groupby([intervention_col, space_col])
            .sum()
            .reset_index()
            .pivot(index = space_col, columns = intervention_col, values = col_of_interest)
            .plot
            .bar(figsize = (12,6))
        )
        
        plot.legend(bbox_to_anchor = (1,1))
        
        if save is not None:
            plt.savefig(save)
    
    @plot_context
    def _plot_chloropleth_getter(self, time):
                
        _plotter = {
            'single' : self._plot_chloropleth,
            'multi' : self._plot_multi_chloropleth
        }
        
        if isinstance(time, int):
            number = 'single'
        else:
            number = 'multi'

            
        return _plotter.get(number)


    


        
        
        
        
        
        
        
        
            
        
        
        
    
