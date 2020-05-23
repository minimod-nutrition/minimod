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
excel_file = "examples/data/raw/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

## Get "vasoilold" and get discounted benefits for constraint
# %%
discount_costs = 1/(1 + 0.03)


vasoilold_df  = (
    pd.read_excel(excel_file,
                  sheet_name = 'Benefits',
                  header = 2)
    .loc[lambda df : df['intervention'] == 'vasoilold']
    .set_index(['intervention', 'space'])
    .stack()
    .to_frame()
    .reset_index()
    .rename({
        'level_2' : 'time',
        0 : 'benefit'
    }, axis= 'columns')
    .assign(
        time_rank = lambda df: (df['time'].rank(numeric_only=True, method= 'dense') -1).astype(int) ,
        time_discount_costs = lambda df: discount_costs**df['time_rank'],
        discounted_benefits = lambda df: df['time_discount_costs']*df['benefit']
    )
)

vasoilold_constraint = vasoilold_df['discounted_benefits'].sum()
# %%

# df_benefit = (pd.read_excel(excel_file,
#                            sheet_name = 'Benefits',
#                            header = 2)
#               .loc[lambda df: df['intervention'] != 'vasoilold']
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
#            .loc[lambda df: df['intervention'] != 'vasoilold']
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
# `df.to_csv("./data/example1.csv")``


# %%
df = pd.read_csv("examples/data/processed/example1.csv")
# %% [markdown]

# ## Running the model

# Now we instantiate the model, and then run `fit` and get the report.

# %%
c = mm.Minimod(solver_type = 'costmin', 
            minimum_benefit = vasoilold_constraint,
            data = df, 
            benefit_col = 'benefit',
            cost_col = 'costs',
            intervention_col = 'intervention',
            space_col = 'space',
            time_col = 'time',
            all_space = ['cube', 'oil', 'maize'], 
            all_time = ['maize', 'cube'],
            time_subset = [1,2,3])

# %%

opt = c.fit()
# %%

c.report()


# %%
c.write("model.lp")

# %%
c.plot_opt_val_hist(save = "hello.png")

c.plot_time(save = "hello2.png")

# %% [markdown]
# ## Plotting a Map

# Now let's create a chloropleth map of the optimal values from the optimization

# %%

# Load data
geo_df = gpd.read_file("examples/data/maps/cameroon/CAM.shp")

# Now we create the boundaries for North, South and Cities
# Based on "Measuring Costs of Vitamin A..., Table 2"
north = r"Adamaoua|Nord|Extreme-Nord"
south = r"Centre|Est|Nord-Ouest|Ouest|Sud|Sud-Ouest"
cities= r"Littoral" # Duala
# Yaounde is in Mfoundi
geo_df.loc[lambda df: df['ADM1'].str.contains(north), 'space'] = 'North'
geo_df.loc[lambda df: df['ADM1'].str.contains(south), 'space'] = 'South'
geo_df.loc[lambda df: df['ADM1'].str.contains(cities), 'space'] = 'Cities'
geo_df.loc[lambda df: df['ADM2'].str.contains(r"Mfoundi"), 'space'] = 'Cities'

# Now we aggregate the data to the `space` variable
agg_geo_df = geo_df.dissolve(by = 'space')

# %%

c.plot_chloropleth(intervention='vasoil',
                   time = [5],
                   optimum_interest='c',
                   map_df = agg_geo_df,
                   merge_key= 'space',
                   save = "map.png")

# %%
c.plot_chloropleth(intervention = 'vasoil',
                   optimum_interest='c',
                   map_df = agg_geo_df,
                   merge_key= 'space',
                   save = "map2.png")


# %%

c.plot_map_benchmark(intervention = 'vasoil',
                           time = [5],
                           optimum_interest = 'b',
                           data_bench = vasoilold_df,
                           bench_col = 'discounted_benefits',
                           bench_merge_key = 'space',
                           bench_intervention = 'vasoilold',
                           map_df = agg_geo_df,
                           merge_key = 'space',
                           save = "benchmark_map.png")




# %%
c.plot_grouped_interventions(save = 'grouped_int.png')

# %%
