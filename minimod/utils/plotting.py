import matplotlib.pyplot as plt
import numpy as np
from minimod.utils.exceptions import MissingOptimizationMethod

class Plotter:
    """This class is in charge of plotting the results of the `minimod`. 
    """        
    
    def __init__(self, model):
        
        self.model = model
        
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
            
    def _plot_process(self, figure = None, axis = None):
        
        self._check_if_optimization()
        
        fig, ax = self._define_axis_object(fig = figure, ax=axis)
        
        return fig, ax
            
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
            .groupby([self.model._time])
            .sum()
            .plot(title = title, 
                fig = fig, 
                ax=ax
                )
            )
            
        if twin:
            ax.plot(self.model.opt_df[to_plot[0]].groupby([self.model._time])
                    .sum(), 
                    color='red')
            
            ax2 = ax.twinx()
            ax2.plot(self.model.opt_df[to_plot[1]].groupby([self.model._time])
                     .sum(), 
                     color = 'blue')
            
            ax2.set_ylabel(twin_ylabel)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend(legend, loc = 'upper left')
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save, dpi=600)
        
        if twin:
            return fig, ax, ax2
        if not twin:
            return fig, ax
        
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
            .groupby([self.model._time])
            .sum()
            .plot
            .bar(fig = fig, ax = ax, grid = True, width = 1)
         )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save, dpi=600)
        
        return fig, ax
    
    def _merge_shape_file(self, 
                          map_df = None, 
                          merge_key = None):
        
        self._check_if_optimization()
        
        # Merge with `opt_df`
        
        df = (
            map_df
            .merge(
                self.model.opt_df
                .reset_index(),
                left_on = [merge_key],
                right_on = [self.model._space]
            )
            .set_index([self.model._intervention,
                        self.model._space,
                        self.model._time
                        ])
        )
        
        return df
          
    
    def _plot_chloropleth(self, 
                          intervention = slice(None),
                          time = None,
                          optimum_interest = None,
                          map_df = None, 
                          merge_key = None, 
                          ax = None,
                          title = None, 
                          save = None):
        
        
        fig, ax = self._plot_process(axis = ax)

        
        df = (self._merge_shape_file(map_df=map_df,merge_key=merge_key)
              .loc[(intervention, slice(None), time ), :]
              )
        
        
                
    
        df.plot(column = optimum_interest, ax = ax, legend = True)
        ax.set_title(title)
        plt.axis('off')

        plt.tight_layout()
        
        if save is not None:
            plt.savefig(save, dpi=600)
            
        return ax

            
    def _plot_multi_chloropleth(self, 
                                t = None, 
                                intervention = None,
                                optimum_interest = None,
                                map_df = None,
                                merge_key = None,
                                save = None):
        
        if t is None:
            t = (self.model.opt_df
                 .index
                 .get_level_values(level = self.model._time)
                 .unique()
                 .values
                 )
        
        mod = len(t) % 2
                
        fig, axs = plt.subplots(nrows = int(len(t)/2) + mod , 
                                ncols=2,
                                figsize = (10,20))
        
        
        for ax, plot in zip(np.array(axs).flatten(), t):
            
            self._plot_chloropleth(intervention = intervention,
                                   time = plot,
                                   optimum_interest = optimum_interest,
                                   map_df = map_df, 
                                   merge_key = merge_key, 
                                   ax = ax,
                                   title = f"T = {plot}")
            ax.set_xticklabels([])
            ax.set_xticks([])
            ax.set_yticklabels([])
            ax.set_yticks([])
            
        plt.tight_layout()
        plt.savefig(save)
        
        return fig, axs
        
        
            
        
        
        
    