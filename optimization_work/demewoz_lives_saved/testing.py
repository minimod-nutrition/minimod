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
# # Folic Acid Effective Coverage MINIMOD Simulations
# 
# -  This uses Folate Eff. Coverage and 6-59 mos. children population data

# %%
import pandas as pd
import geopandas as gpd
import minimod
import matplotlib.pyplot as plt
from ipywidgets import fixed, interact, IntSlider

data_folder = 'optimization_work/demewoz_lives_saved/data_files/'

effective_coverage_folder = data_folder + 'effective_coverage/'
cost_folder = data_folder + 'new_cost_benefits/'


# %%
# First load in cost data
costs = pd.read_excel(cost_folder + 'lives_saved_costs.xlsx', sheet_name='costs')


# Get intervention names to change
folate_eff_cov = (
pd.read_excel(effective_coverage_folder + 'folate_results.xlsx', sheet_name = 'Number_effective_wra_covered')
)

long_intervention_names = folate_eff_cov['note'].unique().tolist()
short_intervention_names =     ['fcubefflour',
    'fflour33',
    'fflour',
    'fcube'
    ]
intervention_rename_list = {k:v for k,v in zip(long_intervention_names, short_intervention_names)}


# %%
df_benefits_mean = (
folate_eff_cov
.loc[lambda df: df['zoneName']!='Overall']
.assign(intervention = lambda df: df['note'].replace(intervention_rename_list))
.rename({'zoneName' : 'region'}, axis=1)
.drop(columns = ['nutrient','note', 'zone', 'Assumptions'])
.set_index(['intervention', 'region'])
.rename({year: str(num + 1) for year, num in zip(range(2020, 2030,1), range(10))}, axis=1)
.drop(columns = range(2030,2036,1))
.stack()
.reset_index()
.rename({'level_2' : 'time',
0 : 'eff_cov_mean'}, axis=1)
.assign(time = lambda df: df['time'].astype(int))
)
df_benefits_mean


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
df = df_benefits_mean.merge(df_costs, on = ['intervention', 'region', 'time'], how= 'left', indicator=True)


# %%
df._merge.value_counts()
df = df.drop(columns = ['_merge'])


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
int1 = "fcube",
int2 = 0,
time_to_replace = [1,2,3])
)

# %% [markdown]
# ## Summary Tables

# %%

s = minimod.utils.summary.PreOptimizationDataSummary(
    data = df_adjusted.reset_index(),
    benefit_col= 'eff_cov_mean',
    cost_col= 'costs',
    intervention_col='intervention',
    space_col= 'region',
    time_col='time',
    benefit_title='WRA Effectively Covered (Folate)',
    intervention_subset=['fflour', 'fcube', 'fcubefflour'],
    intervention_subset_titles={'fflour' : 'Flour with Folic Acid (100%)',
    'fcube' : 'Cube with Folic Acid (100%)',
    'fcubefflour' : 'Flour + Cube with Folic Acid',
    'fflour33' : 'BAU: Folic Acid Flour (33%)'},
    bau_intervention = 'fflour33'
)

s.summary_table(variables_of_interest= {'Cost per Child ($)' : 'cost_per_benefit'}, grouping = 'over_space', style = 'markdown')


# %%
m = minimod.Minimod(solver_type = 'costmin',
data = df_adjusted,
benefit_col = 'eff_cov_mean',
cost_col = 'costs',
space_col = 'region',
all_space = ['fcube', 'fflour'],
all_time = ['fcube', 'fflour'],
time_subset = [1,2,3],
benefit_title = 'WRA Effectively Covered (Folate)',
minimum_benefit = 'fflour33',
drop_bau=True
)


# %%
m.fit()


# %%
m.report()


# %%
m.model.get_equation('base_constraint')

