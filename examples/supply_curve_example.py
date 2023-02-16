# %% [markdown]

# # An Example of using `minimod`

# For this notebook, we will first create the data needs to be used for the program. Then we will instantiate the class and make a report of the results using the `report` method

# %%
#!%load_ext autoreload
# %%
#!%autoreload 2
import pandas as pd
import minimod_opt as mm
import numpy as np
import joblib

# %% 

# Data

# This is how the data was processed, assuming we use the Katie_VA_Benefits_and_Costs_1_8_2019.xlsx file.
excel_file = "examples/data/processed/supply_curve_example.xlsx"

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
              above_ul = lambda df: df['above_ul']*df['pop'],
              intervention = lambda df: df['intervention'].str.lower())
      .set_index(['intervention', 'region', 'time'])
      .sort_index()

)

full_population = df_dict['pop'].set_index('region').sum(axis=1).sum()


# %%


# supply_curve = mm.Minimod('costmin').supply_curve(
#       df, 
#       full_population,
#       bau = 'current fortification',
#       all_space=  ['Cube', 'Oil', 'current'],
#       all_time =  ['Cube', 'Oil', 'current'],
#       time_subset = [1,2,3],
#       cost_col='costs',
#       space_col='region',
#       ec_range=np.linspace(.01,.99,20),
#       above_ul = True,
#       show_output=False
# )

# joblib.dump(supply_curve, "supply_curve.joblib")

# %%

supply_curve = joblib.load("supply_curve.joblib")


# %%
#!%config InlineBackend.print_figure_kwargs = {'bbox_inches': 'tight'}

ax = mm.Minimod('costmin').plot_supply_curve(supply_curve, 
                                    ec_thousands = 1_000_000_000,
                                    ul_thousands = 1_000,
                                    above_ul=True,
                                    splitter=' + ',
                                    save='supply_curve.png')


# %%

# Two point here worth mentioning:
#     - There need not be a consistent increase in some interventions
#     - Adding these interventions like this makes it seem like there a decrease in interventions, 
#           but it really might be to due to the fact that more expensive interventions are being used for longer