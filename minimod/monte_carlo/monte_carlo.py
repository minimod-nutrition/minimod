from minimod.solvers import Minimod
from minimod.utils.plotting import Plotter
from minimod.utils.summary import OptimizationSummary

from numpy.random import normal, uniform

import pandas as pd
from progressbar import progressbar

import matplotlib.pyplot as plt

from functools import reduce

class MonteCarloMinimod:
    
    def __init__(self, 
                solver_type = None,
                data = None,
                intervention_col = None,
                time_col = None,
                space_col = None,
                benefit_mean_col = None,
                benefit_sd_col = None,
                cost_col = None,
                cost_uniform_perc = None,
                pop_weight_col = None,
                **kwargs):
                
        print("""Monte Carlo Simulator""")
        
        self.solver_type = solver_type
        
        self.dist = normal
    
        self.data = data.set_index([intervention_col, space_col, time_col])
        
        self.intervention_col = intervention_col
        self.space_col = space_col
        self.time_col = time_col
        
        if pop_weight_col is None:
            self.data = self.data.assign(pop_weight_col = 1)
            self.pop_weight_col = 'pop_weight_col'
        else:
            self.pop_weight_col = pop_weight_col
            
        self.benefit_mean_col = benefit_mean_col
        self.benefit_sd_col = benefit_sd_col

        if cost_uniform_perc is None:
            self.cost_uniform_perc = 0.2
        else:
            self.cost_uniform_perc = cost_uniform_perc
            
        self.cost_col = cost_col
        
        
    
    def _construct_benefit_sample(self):
        """ For normal, it doesn't require transformation, so just return mean and sd"""
        
            
        df_mean_sd = self.data[[self.benefit_mean_col, self.benefit_sd_col, self.pop_weight_col]]
        
        df = (
            df_mean_sd
            .pipe(self._drop_nan_benefits)
            .assign(weight_mean = lambda df: df[self.benefit_mean_col]*df[self.pop_weight_col],
                    weight_sd = lambda df: df[self.benefit_sd_col]*df[self.pop_weight_col],
                    benefit_random_draw = lambda df: self.dist(df['weight_mean'], df['weight_sd'])
                    )
        )
        
        return df['benefit_random_draw']
    
    
    def _construct_cost_sample(self):
        """For costs we assume uniform and deviate by some percentage."""
        
        df_costs = self.data[self.cost_col]
        df_costs_low = (1-self.cost_uniform_perc)*self.data[self.cost_col]
        df_costs_high = (1+self.cost_uniform_perc)*self.data[self.cost_col]
        
        df = (
            df_costs
            .to_frame()
            .assign(cost_random_draw = uniform(df_costs_low, df_costs_high))
        )
            
        return df['cost_random_draw']
    
    def _drop_nan_benefits(self, data):
        
        df = (
            data.dropna(subset = [self.benefit_sd_col])
        )
        
        return df
    
    def _merge_samples(self):
        
        benefit_sample = self._construct_benefit_sample()
        cost_sample = self._construct_cost_sample()
        
        return benefit_sample.to_frame().merge(cost_sample, 
                                    left_index = True, 
                                    right_index = True)
        
        
    
    def fit_all_samples(self,
                        N = None,
                        all_space = None,
                        all_time = None,
                        space_subset = None,
                        time_subset = None,
                        strict = False,
                        show_progress = True,
                        **kwargs):
        if N is None:
            N = 10
            
        sim_dict = {}
        
        if show_progress:
            sample_range = progressbar(range(N))
        else:
            sample_range = range(N)
            
        print(f"""Running with {N} Samples""")
        
        for i in sample_range:
                        
            df = self._merge_samples()
            
            self.minimod = Minimod(solver_type = self.solver_type,
                                   data=df,
                            intervention_col=self.intervention_col,
                            space_col=self.space_col,
                            time_col=self.time_col,
                            benefit_col='benefit_random_draw',
                            cost_col="cost_random_draw",
                            all_space=all_space,
                            all_time=all_time,
                            space_subset=space_subset,
                            time_subset=time_subset,
                            show_output = False,
                            strict = strict,
                            benefit_title = 'Effective Coverage',
                            **kwargs)
            
            self.minimod.fit()
            
            iteration_dict = {'status' : self.minimod.status,
                              'opt_objective' : self.minimod.objective_value,
                              'opt_constraint' : self.minimod.opt_df['opt_benefit'].sum(),
                              'num_vars' : self.minimod.num_cols,
                              'constraints' : self.minimod.num_rows,
                              'solutions' : self.minimod.num_solutions,
                              'num_int' : self.minimod.num_int,
                              'num_nz' : self.minimod.num_nz,
                              'opt_df' : self.minimod.opt_df}
            
            sim_dict[i] = iteration_dict
            
            self.N = N
        
        print("Done.")
            
        self.sim_results = pd.DataFrame(sim_dict).T
        
        return pd.DataFrame(sim_dict).T
    
    def report(self, 
               avg_time = False, 
               avg_space = False, 
               perc_intervention_appeared = False, 
               show_percint_full = False,
               intervention_group = None):
        
        perc_opt = self.sim_results['status'].value_counts(normalize=True)[0]*100
        avg = self.sim_results.mean()
        
        s = OptimizationSummary(self)
        
        header = [
            ('MiniMod Solver Results', ""),
            ("Method:" , str(self.minimod.sense)),
            ("Solver:", str(self.minimod.solver_name)),
            ("Percentage Optimized:", perc_opt),
            ("Average Number Solutions Found:", avg['solutions'])
        ]
        
        features = [
            ("No. of Variables:", avg['num_vars']),
            ("No. of Integer Variables:", avg['num_int']),
            ("No. of Constraints", avg['constraints']),
            ("No. of Non-zeros in Constr.", avg['num_nz'])
        ]
        
        results_benefits = [
            ('Minimum Benefit', self.minimod.minimum_benefit)
        ]
        
        
        stats = [
            ('Statistics for Benefits and Costs', ""),
        ]
        
        s.print_generic(header, features, results_benefits, stats)
        
        stats_df = (
            self.sim_results[['opt_objective', 'opt_constraint']]
            .astype(float)
            .describe()
            .round(4)
            .to_markdown()
        )
        print(stats_df)
        
        ## Create append opt_df dataset from sim_results
        opt_df_list = [self.sim_results # Get results
             .stack() # stack so columns become index
             .loc[(slice(None), 'opt_df')][i] # Get only opt_df
             .assign(iteration = i) # Create variable for iteration \
                 for i in range(self.N)] # Do it for every simulation
        
        all_opt_df = reduce(lambda i, j: i.append(j), opt_df_list)
        
        if perc_intervention_appeared:
            
            perc_int = (
                (all_opt_df
                .groupby([self.intervention_col, 
                          'iteration'])
                .sum()
                .assign(val_appeared = \
                    lambda df: (df['opt_vals']>0)
                    .astype(int))
                ['val_appeared']
                .groupby(self.intervention_col)
                .sum()/self.N)*100
                )
            
            s.print_generic([('Percentage Appeared in Simulations', '')])            
            
            if show_percint_full:
                print(perc_int.to_markdown())
            
            if intervention_group is not None:
                if isinstance(intervention_group, str):
                    intervention_group = [intervention_group]
                
                s.print_generic([(f"% Appearance of:", '')])

                for i in intervention_group:
                    int_group = perc_int.loc[lambda df: df.index.str.contains(i)].sum()/perc_int.sum()
                    s.print_generic([(f"{i}", f'{int_group}')])

            
            
            
        if avg_time:
            
            time_df= (
                all_opt_df
                .groupby([self.time_col, 
                          'iteration'])
                .sum()
                .groupby(self.time_col)
                .mean()
                [['opt_benefit', 'opt_costs']]
                )
            
            s.print_generic([('Mean Benefits and Costs across time', '')])            
            print(time_df.to_markdown())
            
        if avg_space:
            
            space_df= (
                all_opt_df
                .groupby([self.space_col, 
                          'iteration'])
                .sum()
                .groupby(self.space_col)
                .mean()
                [['opt_benefit', 'opt_costs']]
                )
            
            s.print_generic([('Mean Benefits and Costs across Regions', '')])            
            print(space_df.to_markdown())
            
        
    
    def plot_opt_hist(self, save = None):
        
        p = Plotter(self)
        
        costs = 'Optimal Costs'
        benefits = self.minimod.benefit_title
        
        if self.solver_type == 'costmin':
            
            objective_title = costs
            constraint_title = benefits
        
        elif self.solver_type == 'benmax':
            
            objective_title = benefits
            constraint_title = costs
                
        fig, (benefit_plot, cost_plot) = p._plot_sim_hist(data = self.sim_results,
                                benefit_col='opt_constraint',
                                cost_col = 'opt_objective',
                                cost_title=objective_title,
                                benefit_title=constraint_title,
                                save = save)
        
        benefit_xlims = benefit_plot.get_xlim()
        benefit_ylims = benefit_plot.get_ylim()
        
        # Put text at midpoint of y
        text_y = (benefit_ylims[1] - benefit_ylims[0])/2
        
        # offset by 10% of length of x-axis 
        text_x = self.minimod.minimum_benefit + (benefit_xlims[1] - benefit_xlims[0])*.1
        
        benefit_plot.axvline(self.minimod.minimum_benefit, color='red')
        benefit_plot.text(text_x, text_y, 'Minimum\nBenefit\nConstraint')
        
        return fig, (benefit_plot, cost_plot)
    
    def plot_sim_trajectories(self, 
                               data_of_interest = 'benefits',
                               save = None
                               ):
        
        fig, ax  = plt.subplots()
        
        if data_of_interest == 'benefits':
            col_of_interest = 'opt_benefit'
        elif data_of_interest == 'costs':
            col_of_interest = 'opt_costs'
        
        df_all = pd.DataFrame()
        
        # All trajectories
        for i in range(self.N):
            
            iter_df = (
                self.sim_results
                .loc[i]['opt_df'][col_of_interest]
                .groupby(self.minimod.time_col)
                .sum()
            )
            
            iter_df.plot(ax = ax, color = 'red', alpha=0.09)
            
            df_all = df_all.append(iter_df)
            
        # Now get mean trajectory
        
        df_all.mean().plot(ax=ax, color = 'red')    
        
        plt.figtext(0,0,"Bold line represents mean trajectory.")
        ax.set_title("Trajectories of all Simulations")
        
        if save is not None:
            plt.savefig(save, dpi = 160)
        

        
        

        
    
    
    
        
        
    
    
    
        
        

        
        
        
        
    
    
        
        