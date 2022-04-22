# %% [markdown]

# # An Example of using `minimod`

# For this notebook, we will first create the data needs to be used for the program. Then we will instantiate the class and make a report of the results using the `report` method

# %%
#!%load_ext autoreload
# %%
#!%autoreload 2
import sys
import pandas as pd
import geopandas as gpd

import minimod as mm

# %% 

# Data

# This is how the data was processed, assuming we use the Katie_VA_Benefits_and_Costs_1_8_2019.xlsx file.
excel_file = "data/raw/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

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
# df.to_csv("examples/data/processed/example1.csv")


# %%
# df = pd.read_csv("examples/data/processed/example1.csv")
# %% [markdown]

# ## Running the model

# Now we instantiate the model, and then run `fit` and get the report.

cube = ["cube", "vascube", "oilcube", "cubemaize", "vascubemaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
oil = ["oil", "vasoil", "oilcube", "oilmaize", "vasoilmaize", "vasoilcube", "oilcubemaize", "vasoilcubemaize"]
maize = ["maize", "vasmaize", "oilmaize", "cubemaize", "vascubemaize", "vasoilmaize", "oilcubemaize", "vasoilcubemaize" ]

# %%

# Create copy of data

df_supply = df.copy(deep=True)

model_dict = {}

for i, benefit_constraint in enumerate([1, 1.5, 2, 2.5, 3]):
      
      df_loop = df_supply
      
      df_loop.loc[('vasoilold', slice(None), slice(None))] = \
            benefit_constraint*df_loop.loc[('vasoilold', slice(None), slice(None))].values
      
      c = mm.Minimod(solver_type = 'costmin', 
                  minimum_benefit = 'vasoilold',
                  data = df_loop, 
                  benefit_col = 'benefit',
                  cost_col = 'costs',
                  intervention_col = 'intervention',
                  space_col = 'space',
                  time_col = 'time',
                  all_space = cube + oil + maize, 
                  all_time = maize + cube,
                  time_subset = [1,2,3],
                  strict = False,
                  drop_bau = True)


      opt = c.fit()
      
      model_dict[benefit_constraint] = opt
      

# %%
for benefit_constraint, value in model_dict.items():
      print(benefit_constraint)
      value.report()

# %%

c.report()






