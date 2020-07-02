# %%

# %%
#!%load_ext autoreload
# %%
#!%autoreload 2
import sys
import pandas as pd
import geopandas as gpd

import minimod as mm
import matplotlib.pyplot as plt
import numpy as np

# %% 

# Data

# This is how the data was processed, assuming we use the Katie_VA_Benefits_and_Costs_1_8_2019.xlsx file.
excel_file = "examples/data/raw/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

# %%

df_benefit = (pd.read_excel(excel_file,
                           sheet_name = 'Benefits',
                           header = 2)
              .set_index(['intervention', 'space'])
              .stack()
              .to_frame()
              .reset_index()
              .rename({'level_2' : 'time',
                       0 : 'benefit'}, axis=1)
              .set_index(['intervention', 'space', 'time'])
              )

df_cost = (pd.read_excel(excel_file,
                           sheet_name = 'Costs',
                           header = 2)
              .set_index(['intervention', 'space'])
              .stack()
              .to_frame()
              .reset_index()
              .rename({'level_2' : 'time',
                       0 : 'costs'}, axis=1)
              .set_index(['intervention', 'space', 'time'])
              )



# %% [markdown]
# Then we merge the cost and benefit data together.
df = (df_benefit
      .merge(df_cost, left_index=True, right_index=True)

)

# Then we save the data. The finished data can be found in the `/examples/data` folder.
df.to_csv("examples/data/processed/example1.csv")


# %%
df = pd.read_csv("examples/data/processed/example1.csv")
# %% [markdown]

# ## Running the model

# Now we instantiate the model, and then run `fit` and get the report.

cube = ["cube", "vascube", "oilcube", "cubemaize", "vascubemaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
oil = ["oil", "vasoil", "oilcube", "oilmaize", "vasoilmaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
maize = ["maize", "vasmaize", "oilmaize", "cubemaize", "vascubemaize", "vasoilmaize", "oilcubemaize", "vasoilcubemaize" ]

# %%
c = mm.Minimod(solver_type = 'costmin', 
            minimum_benefit = 'vasoilold',
            data = df, 
            benefit_col = 'benefit',
            cost_col = 'costs',
            intervention_col = 'intervention',
            space_col = 'space',
            time_col = 'time',
            all_space = [cube, oil, maize], 
            all_time = [maize, cube],
            time_subset = [1,2,3],
            strict = True,
            drop_bau = True)

# %%

opt = c.fit()

# %%

a = c.opt_df.loc[lambda df: df['opt_vals']>0].index.get_level_values(level='intervention').unique()


# %%
b = c.opt_df.loc[lambda df: df.index.get_level_values(level='intervention').isin(a)]['opt_vals']

# %%

dy  =0.3

d = (
    c.assign(cube = lambda df: df['intervention'].str.contains('cube').astype(int)*1,
         vas = lambda df: df['intervention'].str.contains('vas').astype(int)*2,
         oil = lambda df: df['intervention'].str.contains('oil').astype(int)*3)
    # .groupby(['space', 'time'])
    # .sum()
    # [['cube', 'vas', 'oil']]
 )

d.loc[lambda df: df['space']== 'Cities', 'oil'] = 2.8
d.loc[lambda df: df['space']== 'Cities', 'vas'] = 1.8

d.loc[lambda df: df['space']== 'South', 'oil'] = 3.2
d.loc[lambda df: df['space']== 'South', 'vas'] = 2.2


# %%

f = d[d['opt_vals']==1].sort_values(by=['space', 'time'])[['space', 'time', 'vas', 'oil']]
# %%

fig, ax = plt.subplots()

f.loc[lambda df: df['space']=='North'].set_index(['time', 'space']).unstack().plot(ax=ax, color='red')

f.loc[lambda df: df['space']=='Cities'].set_index(['time', 'space']).unstack().plot(ax=ax, color='blue')

f.loc[lambda df: df['space']=='South'].set_index(['time', 'space']).unstack().plot(ax=ax, color='green')

ax.set_yticklabels()
# %%
