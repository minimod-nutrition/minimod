# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd()))
	print(os.getcwd())
except:
	pass
# %% [markdown]
# # Cameroon Vitamin A Effective Coverage MINIMOD Simulations
# 
# -  This uses Vitamin A Eff. Coverage and 6-59 mos. children population data

# %%
import pandas as pd
import geopandas as gpd
import minimod
import matplotlib.pyplot as plt
from ipywidgets import fixed, interact, IntSlider

data_folder = 'Optimization Work/demewoz_lives_saved/data_files/'

effective_coverage_folder = data_folder + 'effective_coverage/'
cost_folder = data_folder + 'new_cost_benefits/'


# %%
# Get intervention names to change
va_eff_cov = (
pd.read_excel(effective_coverage_folder + 'April28_Vitamin A_Effective_ coverage.xlsx')
)

long_intervention_names = va_eff_cov['Vitamin A intervention'].unique().tolist()
short_intervention_names = ['cube',
'oilvas',
'maxoil',
'maxoilcube',
'oil',
'maxoilcubevas',
'oilcube',
'oilcubevas',
'maxoilvas',
'vas',
'cubevas',
'clinic',
'maxoilclinic',
'maxoilclinic',
'oilclinic',
'oilclinic',
'cubeclinic',
'oilcubeclinic',
'oilcubeclinic',
'maxoilcubeclinic'
]
intervention_rename_list = {k:v for k,v in zip(long_intervention_names, short_intervention_names)}

# %% [markdown]
# ## Data Processing

# %%
# First load in cost data
costs = pd.read_excel(cost_folder + 'lives_saved_costs.xlsx', sheet_name='costs')

# Then VA Effective Coverage
va_eff_cov = (
pd.read_excel(effective_coverage_folder + 'April28_Vitamin A_Effective_ coverage.xlsx')
.assign(intervention = lambda df: df['Vitamin A intervention'].replace(intervention_rename_list),
region = lambda df: df['Zone'].str.strip())
)

# 6-59 Mos. Children
pop = (
pd.read_excel(effective_coverage_folder + 'Cameroon Population age6-59 months.xlsx', skiprows=1)
.replace({'Region' : {'Urban' : 'Cities'}})
.loc[:, ['Region'] + [f"Sum of {year}" for year in range(2020, 2030,1)]]
.rename({'Region' : 'region'}, axis=1)
)
## Using 2020 - 2029 -> 1-10


# %%
def year_func(year, col = 'effective_coverage'):
    return lambda df: (df[col]/100)*df[f'Sum of {year}']

df_benefits_mean = (
va_eff_cov
.merge(pop, on = 'region')
.assign(**{str(num + 1) : year_func(year) for num, year in enumerate(range(2020, 2030,1))})
[['intervention', 'region'] + [str(x) for x in range(1,11,1)]]
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({'level_2' : 'time',
0 : 'eff_cov_mean'}, axis=1)
.assign(time = lambda df: df['time'].astype(int))
)

df_benefits_sd = (
va_eff_cov
.merge(pop, on = 'region')
.assign(
**{str(num + 1) : year_func(year, 'effective_coverage_SE') for num, year in enumerate(range(2020, 2030,1))})
[['intervention', 'region'] + [str(x) for x in range(1,11,1)]]
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({'level_2' : 'time', 0 : 'eff_cov_sd'}, axis=1)
.assign(time = lambda df: df['time'].astype(int))
)

df_benefits = df_benefits_mean.merge(df_benefits_sd, on  = ['intervention', 'region', 'time'])


# %%
# Create costs
df_costs = (
costs
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({'level_2' : 'time', 0 : 'costs'}, axis=1)
)


# %%
df = df_benefits.merge(df_costs, on = ['intervention', 'region', 'time'], how = 'outer', indicator=True)


# %%
df._merge.value_counts()


# %%
df = df.loc[df._merge== 'both'].drop(columns = '_merge')


# %%
# Create function to make data adjustments
def observation_adjustment(data, int1, int2, time_to_replace, space_to_replace = slice(None)):
    
    df = data.copy(deep = True)

    if isinstance(int2, str):
        df_int2 = df.loc[(int2, space_to_replace, time_to_replace)]
        df.loc[(int1, space_to_replace, time_to_replace), :] = df_int2.values
    elif int2 == 0:
        df.loc[(int1, space_to_replace, time_to_replace), :] = 0

    print(f"Changed {int1} to {int2}")

    return df


# %%
df_adjusted = (df.set_index(['intervention', 'region', 'time'])
.pipe(observation_adjustment,
int1 = "cube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcube",
int2 = "maxoil",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcube",
int2 = "oil",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubevas",
int2 = "oilvas",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubevas",
int2 = "maxoilvas",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubevas",
int2 = "vas",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubeclinic",
int2 = "clinic",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubeclinic",
int2 = "maxoilclinic",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubeclinic",
int2 = "oilclinic",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoil",
int2 = "oil",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcube",
int2 = "oilcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilvas",
int2 = "oilvas",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubevas",
int2 = "oilcubevas",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilclinic",
int2 = "oilclinic",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubeclinic",
int2 = "oilcubeclinic",
time_to_replace = [1,2])
)

# %% [markdown]
# ## Summary Tables

# %%
df_adjusted.index.get_level_values(level=0).unique()


# %%

s = minimod.utils.summary.PreOptimizationDataSummary(
    data = df_adjusted.reset_index(),
    benefit_col= 'eff_cov_mean',
    cost_col= 'costs',
    intervention_col='intervention',
    space_col= 'region',
    time_col='time',
    benefit_title='Children Effectively Covered',
    intervention_subset=['clinic', 'vas', 'cube', 'oil', 'maxoil', 'vasoil'],
    intervention_subset_titles={'clinic' : 'VAS Clinic Day', 
    'vas' : 'Vitamin A Supp.', 
    'cube' : 'Boullion Cube',
    'oil' : 'Oil (75%)',
    'maxoil' : 'Oil (100%)',
    'oilvas' : 'BAU: Vitamin A Supp. + Oil (75%)'},
    bau_intervention = 'oilvas'
)

s.summary_table(variables_of_interest= {'Cost per Child ($)' : 'cost_per_benefit'}, grouping = 'over_space', style = 'markdown')

# %% [markdown]
# ## Simulations
# 
# 

# %%
m = minimod.Minimod(solver_type = 'costmin',
data = df_adjusted,
benefit_col = 'eff_cov_mean',
cost_col = 'costs',
space_col = 'region',
all_space = ['cube', '(?=.*(?<![max])oil)', 'maxoil'],
all_time = ['cube', '(?=.*(?<![max])oil)', 'maxoil'],
time_subset = [1,2,3],
benefit_title = 'Children Effectively Covered (VA)',
minimum_benefit = 'oilvas',
)


# %%
m.fit()


# %%
m.report()


# %%
m.plot_time()


# %%
fig, (ax1, ax2) = plt.subplots(1,2,  figsize = (8,5))
m.plot_bau_time(ax=ax1)
m.plot_bau_time(opt_variable = 'c', ax=ax2)
plt.savefig("low_bau.png", dpi=600)


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
m.plot_map_benchmark( 
time = 5, 
optimum_interest = 'cb', 
bench_intervention = 'oilvas',
map_df = agg_geo_df,
merge_key = 'space',
intervention_bubbles= True,
intervention_bubble_names = ['oil', 'cube', 'vas']
)

