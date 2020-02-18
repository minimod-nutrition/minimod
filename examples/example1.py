# %%
import sys
import pandas as pd

import minimod as mm

# %%
## First we load the data and get it into the form we need:

excel_file = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/GAMS_R Project/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

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


# %%

## Now we get data into the form we want

df = (df_benefit
      .merge(df_cost, left_index=True, right_index=True)
      
)

# %%
#df.to_csv("./data/example1.csv")

df = pd.read_csv("./data/example1.csv")
# %%

## First minimum benefit

## Now we start up the engines!

# default_values = {
#     'minimum_benefit' : 15958220 ,
#     'data' : df,
#     'intervention_col' : 'intervention',
#     'space_col' : 'space',
#     'time_col' : 'time',
#     'benefit_col' : 'benefit',
#     'cost_col' : 'costs',
#     'interest_rate_cost' :  0, 
#     'interest_rate_benefit' : 0.03,
#     'va_weight' : 1        
# }

# %%
c = mm.CostSolver(data = df)

# %%

opt = c.fit()
c.report()

# %%
