# %% [markdown]

# # An Example of using `minimod`

# For this notebook, we will first create the data needs to be used for the program. Then we will instantiate the class and make a report of the results using the `report` method


# %%
import sys
import pandas as pd

import minimod as mm


# %% [markdown]
# ## Data

# This is how the data was processed, assuming we use the Katie_VA_Benefits_and_Costs_1_8_2019.xlsx file.
# ```python
# excel_file = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/GAMS_R Project/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

# df_benefit = (pd.read_excel(excel_file, 
#                            sheet_name = 'Benefits',
#                            header = 2)
#               .set_index(['intervention', 'space'])
#               .stack()
#               .to_frame()
#               .reset_index()
#               .rename({'level_2' : 'time',
#                        0 : 'benefit'}, axis=1)
#               .set_index(['intervention', 'space', 'time'])
#               )

# df_cost = (pd.read_excel(excel_file, 
#                            sheet_name = 'Costs',
#                            header = 2)
#               .set_index(['intervention', 'space'])
#               .stack()
#               .to_frame()
#               .reset_index()
#               .rename({'level_2' : 'time',
#                        0 : 'costs'}, axis=1)
#               .set_index(['intervention', 'space', 'time'])
#               )
# ```


# %% [markdown]
# Then we merge the cost and benefit data together.
# ```python
# df = (df_benefit
#       .merge(df_cost, left_index=True, right_index=True)
      
# )
#```

# Then we save the data. The finished data can be found in the `/examples/data` folder.
# `df.to_csv("./data/example1.csv")`


# %%

df = pd.read_csv("examples/data/example1.csv")
# %% [markdown]

# ## Running the model

# Now we instantiate the model, and then run `fit` and get the report.

# %%
c = mm.CostSolver(data = df)

# %%

opt = c.fit()
# %%

c.report()


