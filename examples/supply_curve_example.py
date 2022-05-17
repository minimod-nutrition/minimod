# %% [markdown]

# # An Example of using `minimod`

# For this notebook, we will first create the data needs to be used for the program. Then we will instantiate the class and make a report of the results using the `report` method

# %%
#!%load_ext autoreload
# %%
#!%autoreload 2
import enum
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import minimod as mm

# %% 

# Data

# This is how the data was processed, assuming we use the Katie_VA_Benefits_and_Costs_1_8_2019.xlsx file.
excel_file = "data/processed/supply_curve_example.xlsx"

# %%

benefits_vars = ['effective_coverage', 'costs', 'above_ul']

df_dict = (
      pd.read_excel(excel_file, sheet_name=None)
)

df = (
      df_dict['ec']
      .merge(df_dict['pop']
             .set_index('region')
             .stack()
             .to_frame()
             .reset_index()
             .rename({'level_1' : 'time', 0 : 'pop'}, axis=1),
       on=['region'])
      .assign(effective_coverage = lambda df: df['effective_coverage']*df['pop'],
              costs = lambda df: df['costs']*df['pop'],
              above_ul = lambda df: df['above_ul']*df['pop'])
      .set_index(['intervention', 'region', 'time'])
      .sort_index()

)

full_population = df_dict['pop'].set_index('region').sum(axis=1).sum()


# %%

# Create copy of data

ratio_to_constraint = lambda ratio: ratio*full_population

df_supply = df.copy(deep=True)

model_dict = {}

for i, benefit_constraint in enumerate(np.arange(.1,1,.1)):
      
      c = mm.Minimod(solver_type = 'costmin', 
                  minimum_benefit = ratio_to_constraint(benefit_constraint),
                  data = df, 
                  benefit_col = 'effective_coverage',
                  cost_col = 'costs',
                  intervention_col = 'intervention',
                  space_col = 'region',
                  time_col = 'time',
                  all_space = ['Cube', 'Oil', 'current'], 
                  all_time = ['Cube', 'Oil', 'current'],
                  time_subset = [1,2,3])


      opt = c.fit()
      
      model_dict[benefit_constraint] = opt
      

# %%

results_dict = {'opt_benefits' : [],
                'opt_costs' : [],
                'opt_interventions' : [],
                'opt_above_ul' : []}

for benefit_constraint, model in model_dict.items():
      
      if benefit_constraint > 0.8:
            continue
      model.report(quiet=True)
      results_dict['opt_benefits'].append(model.opt_df.opt_benefit_discounted.sum())
      results_dict['opt_costs'].append(model.opt_df.opt_costs_discounted.sum())
      results_dict['opt_interventions'].append(model.optimal_interventions)
      
      above_ul = (
            df['above_ul']
               .reset_index()
               .assign(intervention = lambda df: df['intervention'].str.lower())
               .set_index(['intervention', 'region', 'time'])
               )
      
      opt_above_ul = (model.opt_df['opt_vals'] * above_ul['above_ul']).sum()
      
      results_dict['opt_above_ul'].append(opt_above_ul)
      
      
      

# %%

results_df = pd.DataFrame(results_dict, index=[.1,.2,.3,.4,.5,.6,.7,.8])

with plt.style.context('seaborn-darkgrid'):
      fig, ax = plt.subplots()
      
      ax2 = ax.twinx()
            
      markers = [r"$\alpha$", r"$\beta$", r"$\gamma$", r"$\delta$", r"$\epsilon$", r"$\pi$", r"$\rho$", r"$\zeta$"]
      
      results_df['opt_costs'].plot(ax=ax)

      ax.set_xlim([0,1])
      ax.set_xlabel('Effective Coverage')

      ax.set_xticks( [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1])
      ax.set_xticklabels([f"{x*100:.0f}%" for x in [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]])
      ax.ticklabel_format(axis='y', useMathText=True)
      
      ax.yaxis.set_major_formatter(tick.FuncFormatter(lambda y, _: f"{y/1_000_000_000:,.0f}"))
      
      ax.set_ylabel('Total Cost (x 1,000,000,000)')
      
      # Now get above_ul
      results_df['opt_above_ul'].plot(ax=ax2, color='tab:red')
      ax2.yaxis.set_major_formatter(tick.FuncFormatter(lambda y, _: f"{y/1_000:,.0f}"))
      ax2.set_ylabel('Population Above UL (x 1,000)')
      
      popped_markers = markers.copy()
      
      results_df.apply(lambda df: ax.text(df.name+.01, df['opt_costs'],
                                          s=popped_markers.pop(), color='black'), axis=1)
      
      intervention_with_marker = []

      for m,i in zip(list(reversed(markers)), [', '.join(i) for i in results_df['opt_interventions'].values.tolist()]):
            intervention_with_marker.append(m + ': ' + i)
      
      fig_text_start = f"""Note: Letters markers describe interventions as:"""
      
      fig.text(0,-.3, s=fig_text_start+'\n' + '\n'.join(intervention_with_marker))
      
      fig.legend(labels=['Costs', 'Above UL'])
      
      plt.tight_layout()
      plt.savefig("supply_curve_example_v2.png", dpi=300, bbox_inches='tight')

# %%
