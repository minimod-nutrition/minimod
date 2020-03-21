import matplotlib.pyplot as plt
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
        
        if fig is None or ax is None:
            figure, axis = plt.subplots()
        else:
            figure, axis = fig, ax
        
        return figure, axis
            
    def _plot_process(self, figure, axis):
        
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
                    save = None):
        
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
        
        
    