from minimod.solvers import Minimod
from minimod.utils.plotting import Plotter
from minimod.utils.summary import Summary

from numpy.random import normal
import pandas as pd
from progressbar import progressbar

class MonteCarloMinimod:
    
    def __init__(self, 
                solver_type = None,
                data = None,
                intervention_col = None,
                time_col = None,
                space_col = None,
                benefit_mean_col = None,
                benefit_sd_col = None,
                cost_mean_col = None,
                cost_sd_col = None,
                pop_weight_col = None,
                **kwargs):
                
        print("""Monte Carlo Simulator""")
        
        self.solver_type = solver_type
        
        self.minimod = Minimod(solver_type = self.solver_type,
                               show_output = False, 
                               **kwargs)
        
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
        self.cost_mean_col = cost_mean_col
        self.cost_sd_col = cost_sd_col
        
        
    
    def _construct_benefit_sample(self):
        """ For normal, it doesn't require transformation, so just return mean and sd"""
        
            
        df_mean_sd = self.data[[self.benefit_mean_col, self.benefit_sd_col, self.pop_weight_col]]
        
        df = (
            df_mean_sd
            .assign(weight_mean = lambda df: df[self.benefit_mean_col]*df[self.pop_weight_col],
                    weight_sd = lambda df: df[self.benefit_sd_col]*df[self.pop_weight_col],
                    benefit_random_draw = lambda df: self.dist(df['weight_mean'], df['weight_sd'])
                    )
        )
                
        return df['benefit_random_draw']
    
    
    def _construct_cost_sample(self):
        
        df_mean_sd = self.data[[self.cost_mean_col, self.cost_sd_col, self.pop_weight_col]]
        
        df = (
            df_mean_sd
            .assign(weight_mean = lambda df: df[self.cost_mean_col]*df[self.pop_weight_col],
                    weight_sd = lambda df: df[self.cost_sd_col]*df[self.pop_weight_col],
                    cost_random_draw = lambda df: self.dist(df['weight_mean'], df['weight_sd'])
                    )
        )
                
        return df['cost_random_draw']
    
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
                        space_subset = slice(None),
                        time_subset = slice(None),
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
            
            self.minimod.fit(data=df,
                            intervention=self.intervention_col,
                            space=self.space_col,
                            time=self.time_col,
                            benefits='benefit_random_draw',
                            costs="cost_random_draw",
                            all_space=all_space,
                            all_time=all_time,
                            space_subset=space_subset,
                            time_subset=time_subset,
                            clear=True,
                            show_output = False,
                            **kwargs)
            
            iteration_dict = {'status' : self.minimod.status,
                              'opt_objective' : self.minimod.objective_value,
                              'opt_constraint' : self.minimod.objective_bound,
                              'num_vars' : self.minimod.num_cols,
                              'constraints' : self.minimod.num_rows,
                              'solutions' : self.minimod.num_solutions,
                              'num_int' : self.minimod.model.num_int,
                              'num_nz' : self.minimod.num_nz,
                              'opt_df' : self.minimod.opt_df}
            
            sim_dict[i] = iteration_dict
            
            self.N = N
        
        print("Done.")
            
        self.sim_results = pd.DataFrame(sim_dict).T
        
        return pd.DataFrame(sim_dict).T
    
    def report(self, avg_time = False, avg_space = False, perc_intervention_appeared = False):
        
        perc_opt = self.sim_results['status'].value_counts(normalize=True)[0]*100
        avg = self.sim_results.mean()
        
        s = Summary(self)

        
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
                    
        if perc_intervention_appeared:
            
            df_int = pd.DataFrame()
            
            for i in range(self.N):
                
                df = (
                    self.sim_results['opt_df']
                    .loc[i]['opt_vals']
                    .groupby('intervention')
                    .sum()
                    .to_frame()
                    .assign(val_appeared = lambda df: (df['opt_vals'] > 0).astype(int))['val_appeared']
                    .to_frame()
                    .T
                    )
                df_int = df_int.append(df)
                
            perc_int = (df_int.sum()/self.N)*100
            
            s.print_generic([('Percentage Appeared in Simulations', '')])            
            print(perc_int.to_markdown())
        
    
    def plot_opt_hist(self, save = None, vline_mean = False, vline_min_ben = False):
        
        p = Plotter(self)
        
        costs = 'Optimal Costs'
        benefits = 'Effective Coverage'
        
        if self.solver_type == 'costmin':
            
            objective_title = costs
            constraint_title = benefits
        
        elif self.solver_type == 'benmax':
            
            objective_title = benefits
            constraint_title = costs
                
        plot = p._plot_sim_hist(data = self.sim_results,
                                benefit_col='opt_constraint',
                                cost_col = 'opt_objective',
                                objective_title=objective_title,
                                constraint_title=constraint_title,
                                save = save)
        fig, ax = plot
        
        ax[0].axvline(self.minimod.minimum_benefit)
        
        
        return plot
        
            
    
        

        
    
    
    
        
        
    
    
    
        
        

        
        
        
        
    
    
        
        