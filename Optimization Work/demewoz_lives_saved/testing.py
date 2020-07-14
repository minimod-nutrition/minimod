# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Optimization Work/demewoz_lives_saved'))
	print(os.getcwd())
except:
	pass
# %%
from IPython import get_ipython

# %% [markdown]
# # Lives Saved Estimates with Python MINIMOD

# %%


# %%
import pandas as pd
import minimod
from glob import glob
from pathlib import Path
import re
from functools import reduce
import gams
import geopandas as gpd
import matplotlib.pyplot as plt
import os
from ipywidgets import fixed, interact, IntSlider


# %%
# Updated Costs and Lives Saved

update_folder = Path('Optimization Work', 'demewoz_lives_saved','data_files', 'updated_costs_lives_saved')


# %%
os.chdir("/home/lordflaron/Documents/minimod/")

# %% [markdown]
# ## Processing Data

# %%
df_benefits_low = (
pd.read_excel(Path(update_folder, 'lives_saved_costs.xlsx'), 
sheet_name='lives_saved', 
skiprows=2)
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({0 : 'lives_saved', 'level_2' : 'time'}, axis=1)
)

df_benefits_high = (
pd.read_excel(Path(update_folder, 'lives_saved_costs.xlsx'), 
sheet_name='lives_saved_high', 
skiprows=2)
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({0 : 'lives_saved_high', 'level_2' : 'time'}, axis=1)
)

costs = (
pd.read_excel(Path(update_folder, 'lives_saved_costs.xlsx'), 
sheet_name='costs', 
skiprows=2)
.set_index(['intervention', 'region'])
.stack()
.reset_index()
.rename({0 : 'costs', 'level_2' : 'time'}, axis=1)
)

# Nope, load in Justin's data from GAMS
df_benefits_gams = (
pd.read_csv(Path(update_folder, 'lives_saved_low.csv'))
)

df_costs_gams = (
pd.read_csv(Path(update_folder, 'costs_low.csv'))
)


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
# Create string function for going from GAMS code to python function

gams_str = """cov("cube",j,t2)=0                              ;
cov("cubezcube",j,t2)=0                         ;
cov("maxoilcube",j,t2)=cov("maxoil",j,t2) ;
cov("oilcube",j,t2)=cov("oil",j,t2)       ;
cov("oilcubevas",j,t2)=cov("oilvas",j,t2) ;
cov("maxoilcubevas",j,t2)=cov("maxoilvas",j,t2) ;
cov("cubevas",j,t2)=cov("vas",j,t2) ;
cov("cubeclinic",j,t2)=cov("clinic",j,t2) ;
cov("maxoilcubeclinic",j,t2)=cov("maxoilclinic",j,t2) ;
cov("oilcubeclinic",j,t2)=cov("oilclinic",j,t2) ;
cov("cubezflour",j,t2)=cov("zflour",j,t2) ;
cov("maxoilcubezflour",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilcubezflour",j,t2)=cov("oilzflour",j,t2) ;
cov("oilcubevaszflour",j,t2)=cov("oilvaszflour",j,t2) ;
cov("cubevaszflour",j,t2)=cov("vaszflour",j,t2) ;
cov("maxoilcubevaszflour",j,t2)=cov("maxoilvaszflour",j,t2) ;
cov("oilcubecliniczflour",j,t2)=cov("oilcliniczflour",j,t2) ;
cov("maxoilcubecliniczflour",j,t2)=cov("maxoilcliniczflour",j,t2) ;
cov("cubezflourzcube",j,t2)=cov("zflour",j,t2) ;
cov("maxoilcubezflourzcube",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilcubezflourzcube",j,t2)=cov("oilzflour",j,t2) ;
cov("oilcubevaszflourzcube",j,t2)=cov("oilvaszflour",j,t2) ;
cov("oilcubecliniczflourzcube",j,t2)=cov("oilcliniczflour",j,t2) ;
cov("maxoilcubecliniczflourzcube",j,t2)=cov("maxoilcliniczflour",j,t2) ;

cov("zcube",j,t2)=0                      ;
cov("zflourzcube",j,t2)=cov("zflour",j,t2) ;
cov("oilvaszflourzcube",j,t2)=cov("oilvaszflour",j,t2) ;
cov("maxoilcubezflourzcube",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilzflourzcube",j,t2)=cov("oilzflour",j,t2) ;

cov("oilzflourfcubefflour",j,t2)=cov("oilzflourfflour",j,t2) ;
cov("maxoil",j,t4)=cov("oil",j,t4) ;
cov("maxoilcube",j,t4)=cov("oilcube",j,t4) ;
cov("maxoilvas",j,t4)=cov("oilvas",j,t4) ;
cov("maxoilcubevas",j,t4)=cov("oilcubevas",j,t4) ;
cov("maxoilclinic",j,t4)=cov("oilclinic",j,t4) ;
cov("maxoilcubeclinic",j,t4)=cov("oilcubeclinic",j,t4) ;
cov("maxoilzflour",j,t4)=cov("oilzflour",j,t4) ;
cov("maxoilcubezflour",j,t4)=cov("oilcubezflour",j,t4) ;
cov("maxoilvaszflour",j,t4)=cov("oilvaszflour",j,t4) ;
cov("maxoilcliniczflour",j,t4)=cov("oilcliniczflour",j,t4) ;
cov("maxoilcubevaszflour",j,t4)=cov("oilcubevaszflour",j,t4) ;
cov("maxoilcubecliniczflour",j,t4)=cov("oilcubecliniczflour",j,t4) ;
cov("maxoilzflourzcube",j,t4)=cov("oilzflourzcube",j,t4) ;
cov("maxoilcubezflourzcube",j,t4)=cov("oilcubezflourzcube",j,t4) ;
cov("maxoilvaszflourzcube",j,t4)=cov("oilvaszflourzcube",j,t4) ;
cov("maxoilcliniczflourzcube",j,t4)=cov("oilcliniczflourzcube",j,t4) ;
cov("maxoilcubevaszflourzcube",j,t4)=cov("oilcubevaszflourzcube",j,t4) ;
cov("maxoilcubecliniczflourzcube",j,t4)=cov("oilcubecliniczflourzcube",j,t4) ;
cov("zflourfflour33",j,t)=0;
cov("fflour33",j,t)=0;"""


# %%
a = [x.strip() for x in gams_str.split(';')]

for i in a:

    cov_str = re.compile(r'(?<=cov\()(\"[a-z0-9]+\")')
    time_str = re.compile(r't[24]*')

    found = cov_str.findall(i)
    time_found = time_str.findall(i)
    # print(time_found)
    if time_found:
        if time_found[0] == 't2':
            time_range = '[1,2,3]'
        elif time_found[0] == 't4':
            time_range = '[1,2]'
        elif time_found[0] == 't':
            time_range = 'slice(None)'
    elif not time_found:
        print("not found time")
        continue

    if len(found) == 2:
        second_int = found[1]
    elif not found:
        print("not found")
    else:
        second_int = 0

    # print(found, time_range)
    print(f""".pipe(observation_adjustment,\nint1 = {found[0]},\nint2 = {second_int},\ntime_to_replace = {time_range})""")


# %%
df_benefits_low_adjusted = (df_benefits_low.set_index(['intervention', 'region', 'time'])
.pipe(observation_adjustment,
int1 = "cube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubezcube",
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
int1 = "cubezflour",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflour",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubezflour",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubevaszflour",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubevaszflour",
int2 = "vaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflour",
int2 = "maxoilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubecliniczflour",
int2 = "oilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflour",
int2 = "maxoilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubezflourzcube",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubezflourzcube",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubevaszflourzcube",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubecliniczflourzcube",
int2 = "oilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflourzcube",
int2 = "maxoilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "zcube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "zflourzcube",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilvaszflourzcube",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilzflourzcube",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilzflourfcubefflour",
int2 = "oilzflourfflour",
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
.pipe(observation_adjustment,
int1 = "maxoilzflour",
int2 = "oilzflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubezflour",
int2 = "oilcubezflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilvaszflour",
int2 = "oilvaszflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflour",
int2 = "oilcliniczflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflour",
int2 = "oilcubevaszflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflour",
int2 = "oilcubecliniczflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilzflourzcube",
int2 = "oilzflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "oilcubezflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilvaszflourzcube",
int2 = "oilvaszflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflourzcube",
int2 = "oilcliniczflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflourzcube",
int2 = "oilcubevaszflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflourzcube",
int2 = "oilcubecliniczflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "zflourfflour33",
int2 = 0,
time_to_replace = slice(None))
.pipe(observation_adjustment,
int1 = "fflour33",
int2 = 0,
time_to_replace = slice(None)))


# %%
df_benefits_high_adjusted = (df_benefits_high.set_index(['intervention', 'region', 'time'])
.pipe(observation_adjustment,
int1 = "cube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubezcube",
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
int1 = "cubezflour",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflour",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubezflour",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubevaszflour",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubevaszflour",
int2 = "vaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflour",
int2 = "maxoilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubecliniczflour",
int2 = "oilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflour",
int2 = "maxoilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubezflourzcube",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubezflourzcube",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubevaszflourzcube",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubecliniczflourzcube",
int2 = "oilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflourzcube",
int2 = "maxoilcliniczflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "zcube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "zflourzcube",
int2 = "zflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilvaszflourzcube",
int2 = "oilvaszflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "maxoilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilzflourzcube",
int2 = "oilzflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilzflourfcubefflour",
int2 = "oilzflourfflour",
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
.pipe(observation_adjustment,
int1 = "maxoilzflour",
int2 = "oilzflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubezflour",
int2 = "oilcubezflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilvaszflour",
int2 = "oilvaszflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflour",
int2 = "oilcliniczflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflour",
int2 = "oilcubevaszflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflour",
int2 = "oilcubecliniczflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilzflourzcube",
int2 = "oilzflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubezflourzcube",
int2 = "oilcubezflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilvaszflourzcube",
int2 = "oilvaszflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflourzcube",
int2 = "oilcliniczflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubevaszflourzcube",
int2 = "oilcubevaszflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcubecliniczflourzcube",
int2 = "oilcubecliniczflourzcube",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "zflourfflour33",
int2 = 0,
time_to_replace = slice(None))
.pipe(observation_adjustment,
int1 = "fflour33",
int2 = 0,
time_to_replace = slice(None))
.pipe(observation_adjustment,
int1 = "cubezflourzcubefcubefflour",
int2 = "zflourfflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "cubezflourfcubefflour",
int2 = "zflourfflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilzflourzcubefcubefflour",
int2 = "oilzflourfflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "fcube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "fcube",
int2 = 0,
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilfcube",
int2 = 'oil',
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "oilcubeclinicfcube",
int2 = 'oilclinic',
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilzflourfcubefflour",
int2 = 'maxoilzflourfflour',
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflourfcubefflour",
int2 = "maxoilcliniczflourfflour",
time_to_replace = [1,2,3])
.pipe(observation_adjustment,
int1 = "maxoilzflourfcubefflour",
int2 = "oilzflourfcubefflour",
time_to_replace = [1,2])
.pipe(observation_adjustment,
int1 = "maxoilcliniczflourfcubefflour",
int2 = "oilcliniczflourfcubefflour",
time_to_replace = [1,2])
)


# %%
# Merge data
df = (
df_benefits_low_adjusted
.merge(df_benefits_high_adjusted, on = ['intervention', 'region', 'time'])
.merge(costs, on = ['intervention', 'region', 'time'])
.assign(lives_saved = lambda df: df['lives_saved'].astype(int),
lives_saved_high = lambda df: df['lives_saved_high'].astype(int),
costs = lambda df: df['costs'].astype(int))
)

df_gams = (
df_benefits_gams
.merge(df_costs_gams, on = ['intervention', 'space', 'time'])
)


# %% [markdown]
# ## Summary Statistics
# 
# Now we show some summary statistics of the data
# %% [markdown]
# ### Lives Saved

# %%
s = minimod.utils.summary.PreOptimizationDataSummary(
    data = df,
    benefit_col= 'lives_saved',
    cost_col= 'costs',
    intervention_col='intervention',
    space_col= 'region',
    time_col='time',
    benefit_title='Lives Saved (Low)',
    intervention_subset=['clinic', 'vas','zflour', 'fflour', 'cube', 'fcube'],
    intervention_subset_titles={'clinic' : 'VAS Clinic Day', 
    'vas' : 'Vitamin A Supp.', 
    'zflour' : 'Zinc Flour',
    'fflour' : 'Folic Acid Flour' ,
    'cube' : 'Boullion Cube',
    'fcube' : 'Boullion Cube with Folic Acid',
    'oilvaszflourfflour33' : 'BAU: Oil/VAS/Flour with Zinc and Folic Acid (33%)'},
    bau_intervention = 'oilvaszflourfflour33'
)

s.summary_table(variables_of_interest= {'Cost per Child ($)' : 'cost_per_benefit'}, grouping = 'over_space', style = 'markdown')

# %% [markdown]
# ### Lives Saved High

# %%
s = minimod.utils.summary.PreOptimizationDataSummary(
    data = df,
    benefit_col= 'lives_saved_high',
    cost_col= 'costs',
    intervention_col='intervention',
    space_col= 'region',
    time_col='time',
    benefit_title='Lives Saved (High)',
    intervention_subset=['clinic', 'vas','zflour', 'fflour', 'cube', 'fcube'],
    intervention_subset_titles={'clinic' : 'VAS Clinic Day', 
    'vas' : 'Vitamin A Supp.', 
    'zflour' : 'Zinc Flour',
    'fflour' : 'Folic Acid Flour' ,
    'cube' : 'Boullion Cube',
    'fcube' : 'Boullion Cube with Folic Acid',
    'oilvaszflourfflour33' : 'BAU: Oil/VAS/Flour with Zinc and Folic Acid (33%)'},
    bau_intervention = 'oilvaszflourfflour33'
)

s.summary_table(variables_of_interest= {'Cost per Child ($)' : 'cost_per_benefit'}, grouping = 'over_space', style = 'markdown')

# %% [markdown]
# ## Run MINIMOD

# %%
cubek = ['cube',   'maxoilcube', 'cubezflourfflour',  'cubefcube', 'cubezcubefcube', 'maxoilcubefcube',  'oilcubefflour',
          'oilcube', 'oilcubevas', 'maxoilcubevas', 'cubevas', 'cubeclinic', 'oilcubeclinic', 'cubezflourfcube', 'maxoilcubezflourfcubefflour',
          'maxoilcubeclinic', 'cubezflour', 'maxoilcubezflour', 'oilcubezflour', 'oilcubevaszflour', 'oilcubefcube', 'maxoilcubezflourzcubefcube',
          'cubevaszflour', 'maxoilcubevaszflour', 'cubefcubefflour', 'cubezcubefcubefflour', 'cubecliniczflourzcubefcubefflour',
         'cubezflourzcube', 'maxoilcubezflourzcube', 'oilcubezflourzcube', 'oilcubevaszflourzcube',   'cubecliniczflourfcubefflour',
         'cubevaszflourzcube', 'maxoilcubevaszflourzcube',  'maxoilcubezflourfflour', 'cubecliniczflourzcubefcube', 'cubevaszflourzcubefcube',
          'oilcubezflourfflour', 'cubezflourzcubefflour', 'cubecliniczflourzcubefflour', 'cubecliniczflourfcube', 'cubevaszflourzcubefcubefflour',
          'maxoilcubefflour', 'cubeclinicfcube', 'maxoilcubezflourzcubefcubefflour', 'oilcubezflourfcubefflour', 'maxoilcubezflourfcube',
          'cubevasfcube', 'maxoilcubefcubefflour', 'cubecliniczflourfflour', 'cubevaszflourfcube', 'cubevaszflourfcubefflour', 'oilcubefcubefflour',
          'cubezflourfcubefflour', 'cubevaszflourzcubefflour', 'cubevasfcubefflour', 'cubezflourzcubefcubefflour'  ]

zcubek = ['zcube', 'zflourzcube', 'cubezcube', 'cubezflourzcube', 'oilvaszflourzcube', 'maxoilcubezflourzcube', 'zcubefcube',
           'oilzflourzcube', 'oilcubezflourzcube', 'oilcubevaszflourzcube', 'maxoilzflourzcube', 'maxoilvaszflourzcube', 'zflourzcubefcube',
           'vaszflourzcube', 'cubevaszflourzcube', 'maxoilcubevaszflourzcube', 'zflourzcubefcubefflour']

fcubek = ['fcube', 'oilfcube', 'cubezflourzcubefcubefflour', 'cubezflourzcubefcube', 'cubezflourfcubefflour', 'maxoilfcube', 'maxoilcubezflourfcube', 'maxoilfcubefflour',
           'maxoilzflourzcubefcube', 'oilzflourfcubefflour'   ]

oilk = ['oilvas', 'oil', 'oilcube', 'oilcubevas', 'oilclinic',    'oilcubeclinic', 'oilvaszflour', 'oilzflour', 'oilzflourfflour', 'oilcubecliniczflourfflour', 'oilcubezflourzcubefflour',
         'oilcliniczflour', 'oilcubezflour', 'oilcubevaszflour', 'oilcubecliniczflour', 'oilvaszflourzcube', 'oilfcube', 'oilcubezflourzcubefcube', 'oilcubezflourfcube', 'oilcubezflourfcubefflour',
         'oilzflourzcube',    'oilcliniczflourzcube', 'oilcubezflourzcube',  'oilcubevaszflourzcube', 'oilcubecliniczflourzcube', 'oilcubezflourzcubefcubefflour',
         'oilcubefcubefflour', 'oilzflourfcubefflour', 'oilcubecliniczflourzcubefcubefflour', 'oilcubeclinicfcube',  'oilzflourzcubefcubefflour', 'oilcubecliniczflourzcubefcube',
         'oilzflourzcubefcube', 'oilcubecliniczflourfcube', 'oilcubecliniczflourfcubefflour', 'oilcubecliniczflourzcubefflour', 'oilzflourfcube', 'oilfcubefflour',
         'oilcubeclinicfcubefflour', 'oilcliniczflourfcubefflour', 'oilcubevaszflourzcubefcubefflour', 'oilcubeclinicfflour', 'oilzflourzcubefflour', 'oilcubevasfcube',
         'oilcubevaszflourzcubefcube', 'oilvaszflourfcubefflour', 'oilcubevaszflourfcube', 'oilcliniczflourzcubefcube', 'oilvasfcubefflour', 'oilcubevaszflourfcubefflour',
         'oilcliniczflourfflour', 'oilcubevaszflourzcubefflour'    ]

maxoilk = ['maxoil', 'maxoilcube', 'maxoilvas', 'maxoilcubevas' ,  'maxoilclinic', 'maxoilcubeclinic' ,  'maxoilzflour', 'maxoilcubezflourzcubefcube', 'maxoilzflourfcubefflour',
            'maxoilcubezflour' ,    'maxoilvaszflour' ,    'maxoilcliniczflour', 'maxoilcubevaszflour'  ,    'maxoilcubecliniczflour', 'maxoilcubefcubefflour',
            'maxoilzflourzcube'   ,   'maxoilcubezflourzcube', 'maxoilvaszflourzcube' ,   'maxoilcubezflourzcubefcubefflour', 'maxoilcubezflourfcubefflour',
             'maxoilcliniczflourzcube'    ,    'maxoilcubevaszflourzcube', 'maxoilcubecliniczflourzcube', 'maxoilcubezflourfcube', 'maxoilcubecliniczflourzcubefcubefflour',
           'maxoilcubezflourzcubefflour', 'maxoilcubecliniczflourzcubefcube', 'maxoilcubeclinicfcube', 'maxoilzflourzcubefcubefflour', 'maxoilzflourzcubefcube',
           'maxoilcubecliniczflourfcubefflour', 'maxoilzflourfflour', 'maxoilcubecliniczflourfcube', 'maxoilzflourfcube', 'maxoilcubecliniczflourzcubefflour', 'maxoilzflourzcubefflour',
           'maxoilfcubefflour', 'maxoilcubeclinicfcubefflour', 'maxoilcliniczflourfcubefflour', 'maxoilcubeclinicfflour', 'maxoilfcube', 'maxoilcubevaszflourzcubefcubefflour',
          'maxoilcubevaszflourzcubefcube', 'maxoilcliniczflourzcubefcube', 'maxoilcliniczflourzcubefcubefflour', 'maxoilcubevasfcube', 'maxoilcubecliniczflourfflour' ]

zflourk = ['zflour', 'zflourzcube',    'cubezflour', 'oilvaszflour', 'maxoilzflour', 'maxoilcubezflour', 'oilzflour',  'zflourfcube' , 'zflourzcubefcubefflour',
           'oilcliniczflour', 'oilcubezflour', 'oilcubevaszflour' ,    'maxoilvaszflour', 'vaszflour' , 'cliniczflour', 'cliniczflourfflour', 'oilzflourfflour',
           'cubevaszflour',  'maxoilcliniczflour', 'maxoilcubevaszflour' , 'oilcubecliniczflourfflour', 'zflourfflour',  'oilzflourfcubefflour', 'oilzflourfcube',
           'cubezflourzcube',   'oilvaszflourzcube', 'maxoilzflourzcube',    'maxoilcubezflourzcube', 'oilzflourzcube',  'maxoilcubecliniczflourfflour', 'maxoilzflourfcubefflour',
           'oilcubezflourzcube' ,    'oilcubevaszflourzcube', 'maxoilvaszflourzcube', 'vaszflourzcube',  'cubevaszflourzcube'    ,    'maxoilcubevaszflourzcube',
          'maxoilzflourfflour', 'oilzflourzcubefcubefflour', 'zflourfcubefflour', 'zflourzcubefflour', 'maxoilzflourfcube', 'oilzflourzcubefcube', 'oilcliniczflourfcubefflour',
           'oilcubezflourzcubefcubefflour']

fflourk = ['fflour', 'oilzflourfflour', 'zflourfflour', 'oilfcubefflour' ]

flouronlyk = ['zflour',  'oilvaszflour', 'maxoilzflour', 'oilzflour',
           'oilcliniczflour',     'maxoilvaszflour', 'vaszflour' , 'cliniczflour',
            'maxoilcliniczflour' ]

cubeonlyk = ['cube',   'maxoilcube',
          'oilcube', 'oilcubevas', 'maxoilcubevas', 'cubevas', 'cubeclinic', 'oilcubeclinic',
          'maxoilcubeclinic']

flourcubek = ['zflourzcube',    'cubezflour', 'maxoilcubezflour',
           'oilcubezflour', 'oilcubevaszflour' ,
           'cubevaszflour', 'maxoilcubevaszflour' ,
           'cubezflourzcube',   'oilvaszflourzcube', 'maxoilzflourzcube',    'maxoilcubezflourzcube', 'oilzflourzcube', 'oilcliniczflourzcube',
           'oilcubezflourzcube' ,    'oilcubevaszflourzcube', 'maxoilvaszflourzcube', 'vaszflourzcube', 'cliniczflourzcube', 'cubevaszflourzcube',
         'maxoilcubevaszflourzcube'     ]


# %%
# Do the same for the High Lives Saved numbers
cubek_high = ['cube',   'maxoilcube', 'cubezflourfflour',  'cubefcube', 'cubezcubefcube', 'maxoilcubefcube',  'oilcubefflour',
           'oilcube', 'oilcubevas', 'maxoilcubevas', 'cubevas', 'cubeclinic', 'oilcubeclinic', 'cubezflourfcube','maxoilcubezflourfcubefflour',
           'maxoilcubeclinic', 'cubezflour', 'maxoilcubezflour', 'oilcubezflour', 'oilcubevaszflour', 'oilcubefcube', 'maxoilcubezflourzcubefcube',
           'cubevaszflour', 'maxoilcubevaszflour', 'cubefcubefflour', 'cubezcubefcubefflour', 'cubecliniczflourzcubefcubefflour',
          'cubezflourzcube', 'maxoilcubezflourzcube', 'oilcubezflourzcube', 'oilcubevaszflourzcube',   'cubecliniczflourfcubefflour',
          'cubevaszflourzcube', 'maxoilcubevaszflourzcube',  'maxoilcubezflourfflour', 'cubecliniczflourzcubefcube', 'cubevaszflourzcubefcube',
           'oilcubezflourfflour', 'cubezflourzcubefflour', 'cubecliniczflourzcubefflour', 'cubecliniczflourfcube', 'cubevaszflourzcubefcubefflour',
           'maxoilcubefflour', 'cubeclinicfcube', 'maxoilcubezflourzcubefcubefflour', 'oilcubezflourfcubefflour', 'maxoilcubezflourfcube',
           'cubevasfcube', 'maxoilcubefcubefflour', 'cubecliniczflourfflour', 'cubevaszflourfcube', 'cubevaszflourfcubefflour', 'oilcubefcubefflour',
           'cubezflourfcubefflour', 'cubevaszflourzcubefflour', 'cubevasfcubefflour', 'cubezflourzcubefcubefflour', 'oilcubezflourzcubefcubefflour',
           'oilcubezflourfcube', "maxoilcubecliniczflourfflour", "oilcubecliniczflourfcubefflour", "oilcubecliniczflourzcubefcubefflour",
           "maxoilcubecliniczflourzcubefcube", "maxoilcubeclinicfcube", "oilcubecliniczflourfflour", "maxoilcubecliniczflourfcubefflour",
           "maxoilcubecliniczflourzcubefflour", "maxoilcubeclinicfcubefflour", "oilcubeclinicfcube", "oilcubecliniczflourfcube", "oilcubeclinicfcubefflour"  ]

zcubek_high = ['zcube', 'zflourzcube', 'cubezcube', 'cubezflourzcube', 'oilvaszflourzcube', 'maxoilcubezflourzcube', 'zcubefcube',
            'oilzflourzcube', 'oilcubezflourzcube', 'oilcubevaszflourzcube', 'maxoilzflourzcube', 'maxoilvaszflourzcube', 'zflourzcubefcube',
            'vaszflourzcube', 'cubevaszflourzcube', 'maxoilcubevaszflourzcube', 'zflourzcubefcubefflour', "oilcubezflourzcubefcube", "maxoilzflourzcubefcube",
            "oilzflourzcubefflour", "cubezcubefcube", "maxoilcubecliniczflourfcube", "oilzflourzcubefcubefflour", "oilcubecliniczflourzcubefcube"]

fcubek_high = ['fcube', 'oilfcube', 'cubezflourzcubefcubefflour', 'cubezflourzcubefcube', 'cubezflourfcubefflour', 'maxoilfcube', 'maxoilcubezflourfcube', 'maxoilfcubefflour',
            'maxoilzflourzcubefcube', 'oilzflourfcubefflour' , "oilzflourfcube", "maxoilzflourzcubefcubefflour", "maxoilcliniczflourfcubefflour",
           "oilcubezflourzcubefcube", "oilfcubefflour", "cubefcubefflour", "maxoilzflourfcubefflour", "maxoilcubecliniczflourzcubefcubefflour", "oilcubezflourfcubefflour",
           "maxoilcubeclinicfcube", "maxoilcubecliniczflourzcubefcube", "cubefcube", "oilcubefcube", "oilcubeclinicfcube", "oilcubecliniczflourfcube",
           "oilcubecliniczflourzcubefcube", "oilvasfcubefflour"  ]

oilk_high = ['oilvas', 'oil', 'oilcube', 'oilcubevas', 'oilclinic',    'oilcubeclinic', 'oilvaszflour', 'oilzflour', 'oilzflourfflour', 'oilcubecliniczflourfflour', 'oilcubezflourzcubefflour',
          'oilcliniczflour', 'oilcubezflour', 'oilcubevaszflour', 'oilcubecliniczflour', 'oilvaszflourzcube', 'oilfcube', 'oilcubezflourzcubefcube', 'oilcubezflourfcube', 'oilcubezflourfcubefflour',
          'oilzflourzcube',    'oilcliniczflourzcube', 'oilcubezflourzcube',  'oilcubevaszflourzcube', 'oilcubecliniczflourzcube', 'oilcubezflourzcubefcubefflour',
          'oilcubefcubefflour', 'oilzflourfcubefflour', 'oilcubecliniczflourzcubefcubefflour', 'oilcubeclinicfcube',  'oilzflourzcubefcubefflour', 'oilcubecliniczflourzcubefcube',
          'oilzflourzcubefcube', 'oilcubecliniczflourfcube', 'oilcubecliniczflourfcubefflour', 'oilcubecliniczflourzcubefflour', 'oilzflourfcube', 'oilfcubefflour',
          'oilcubeclinicfcubefflour', 'oilcliniczflourfcubefflour', 'oilcubevaszflourzcubefcubefflour', 'oilcubeclinicfflour', 'oilzflourzcubefflour', 'oilcubevasfcube',
          'oilcubevaszflourzcubefcube', 'oilvaszflourfcubefflour', 'oilcubevaszflourfcube', 'oilcliniczflourzcubefcube', 'oilvasfcubefflour', 'oilcubevaszflourfcubefflour',
          'oilcliniczflourfflour', 'oilcubevaszflourzcubefflour', "oilcubefcube", "oilcubezflourfflour", "oilcubefflour"    ]

maxoilk_high = ['maxoil', 'maxoilcube', 'maxoilvas', 'maxoilcubevas' ,  'maxoilclinic', 'maxoilcubeclinic' ,  'maxoilzflour', 'maxoilcubezflourzcubefcube', 'maxoilzflourfcubefflour',
             'maxoilcubezflour' ,    'maxoilvaszflour' ,    'maxoilcliniczflour', 'maxoilcubevaszflour'  ,    'maxoilcubecliniczflour', 'maxoilcubefcubefflour',
             'maxoilzflourzcube'   ,   'maxoilcubezflourzcube', 'maxoilvaszflourzcube' ,   'maxoilcubezflourzcubefcubefflour', 'maxoilcubezflourfcubefflour',
              'maxoilcliniczflourzcube'    ,    'maxoilcubevaszflourzcube', 'maxoilcubecliniczflourzcube', 'maxoilcubezflourfcube', 'maxoilcubecliniczflourzcubefcubefflour',
            'maxoilcubezflourzcubefflour', 'maxoilcubecliniczflourzcubefcube', 'maxoilcubeclinicfcube', 'maxoilzflourzcubefcubefflour', 'maxoilzflourzcubefcube',
            'maxoilcubecliniczflourfcubefflour', 'maxoilzflourfflour', 'maxoilcubecliniczflourfcube', 'maxoilzflourfcube', 'maxoilcubecliniczflourzcubefflour', 'maxoilzflourzcubefflour',
            'maxoilfcubefflour', 'maxoilcubeclinicfcubefflour', 'maxoilcliniczflourfcubefflour', 'maxoilcubeclinicfflour', 'maxoilfcube', 'maxoilcubevaszflourzcubefcubefflour',
           'maxoilcubevaszflourzcubefcube', 'maxoilcliniczflourzcubefcube', 'maxoilcliniczflourzcubefcubefflour', 'maxoilcubevasfcube', 'maxoilcubecliniczflourfflour', "maxoilcubefcube" , "maxoilcubezflourfflour", "maxoilcubefflour"]

zflourk_high = ['zflour', 'zflourzcube',    'cubezflour', 'oilvaszflour', 'maxoilzflour', 'maxoilcubezflour', 'oilzflour',  'zflourfcube' , 'zflourzcubefcubefflour',
            'oilcliniczflour', 'oilcubezflour', 'oilcubevaszflour' ,    'maxoilvaszflour', 'vaszflour' , 'cliniczflour', 'cliniczflourfflour', 'oilzflourfflour',
            'cubevaszflour',  'maxoilcliniczflour', 'maxoilcubevaszflour' , 'oilcubecliniczflourfflour', 'zflourfflour',  'oilzflourfcubefflour', 'oilzflourfcube',
            'cubezflourzcube',   'oilvaszflourzcube', 'maxoilzflourzcube',    'maxoilcubezflourzcube', 'oilzflourzcube',  'maxoilcubecliniczflourfflour', 'maxoilzflourfcubefflour',
            'oilcubezflourzcube' ,    'oilcubevaszflourzcube', 'maxoilvaszflourzcube', 'vaszflourzcube',  'cubevaszflourzcube'    ,    'maxoilcubevaszflourzcube',
           'maxoilzflourfflour', 'oilzflourzcubefcubefflour', 'zflourfcubefflour', 'zflourzcubefflour', 'maxoilzflourfcube', 'oilzflourzcubefcube', 'oilcliniczflourfcubefflour',
            'oilcubezflourzcubefcubefflour', "oilcubezflourzcubefcube", "oilcliniczflourfflour", "cubezflourzcubefflour", "maxoilcliniczflourfcubefflour", "maxoilvaszflour",
           "oilcubecliniczflourzcubefcubefflour", "cubezflourfflour", "cubezflourzcubefcubefflour", "oilcubezflourfcube", "oilcubezflourfflour", "cubezflourfcubefflour",
           "oilcubecliniczflourzcubefcube", "maxoilzflourzcubefcube"]

fflourk_high = ['fflour', 'oilzflourfflour', 'zflourfflour', 'oilfcubefflour', "maxoilcubezflourzcubefflour", "oilcubezflourzcubefflour", "oilcliniczflourfflour",  "oilvasfcubefflour",
             "maxoilzflourzcubefcubefflour", "maxoilcubecliniczflourzcubefcubefflour", "oilcubefcubefflour", "oilzflourzcubefcubefflour", "oilcubecliniczflourzcubefflour" ]


# %%
m = minimod.Minimod(solver_type = 'costmin',
data = df,
benefit_col = 'lives_saved',
cost_col = 'costs',
space_col = 'region',
all_space = [cubek, zcubek, fcubek, oilk, maxoilk, zflourk, fflourk],
all_time = [oilk, maxoilk,zflourk, fflourk, cubek, zcubek, fcubek],
time_subset = [1,2,3],
strict = True,
benefit_title = 'Lives Saved',
minimum_benefit = 'oilvaszflourfflour33',
main_constraint_over = 'time'
)


# %%
m.fit()


# %%
intervention_grouper = {'oil' : 'Oil (75%)',
                        '(?=.*zflour)(?=.*fflour)' : 'Flour (100% Zinc + Folic Acid)',
                        'fcube' : 'Cube (Folic Acid Only)' }

m.report(intervention_groups = intervention_grouper)

# %% [markdown]
# ### High Lives Saved

# %%
m_high = minimod.Minimod(solver_type = 'costmin',
data = df,
benefit_col = 'lives_saved_high',
cost_col = 'costs',
space_col = 'region',
all_space = [cubek_high, zcubek_high, fcubek_high, oilk_high, maxoilk_high, zflourk_high, fflourk_high],
all_time = [oilk_high, maxoilk_high, zflourk_high, fflourk_high, cubek_high, zcubek_high, fcubek_high],
time_subset = [1,2,3],
strict = True,
benefit_title = 'Lives Saved',
minimum_benefit = 'oilvaszflourfflour33',
)


# %%
m_high.fit()


# %%
intervention_grouper_high = {'maxoil' : 'Oil (100%)',
'(?=.*zcube)(?=.*fcube)(?=.*(?<![zf])cube)': 'Cube (100% Zinc + Folic Acid + VA)',
                        '(?=.*zflour)(?=.*fflour)' : 'Flour (100% Zinc + Folic Acid)',
                        'zflourfcube' : 'Cube (Folic Acid Only)',
                        'zflour(?![zf]cube)' : 'Flour (Zinc Only)',
                            'clinic' : "Clinic"}

m_high.report(intervention_groups=intervention_grouper_high)

# %% [markdown]
# ## Visualizing the Results
# %% [markdown]
# ### Lives Saved and Costs Across Time

# %%
m.plot_time()


# %%
fig, (ax1, ax2) = plt.subplots(1,2,  figsize = (8,5))
m.plot_bau_time(ax=ax1)
m.plot_bau_time(opt_variable = 'c', ax=ax2)
plt.savefig("low_bau.png", dpi=600)


# %%
m_high.plot_time()


# %%
fig, (ax1, ax2) = plt.subplots(1,2, figsize = (8,5))
m_high.plot_bau_time(ax=ax1)
m_high.plot_bau_time(opt_variable = 'c', ax=ax2)
plt.savefig("high_bau.png", dpi=600)

# word doc with graphs and tables
# email jsting about updated costs

# %% [markdown]
# ### Mapping Lives Saved and Costs

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
interact(m.plot_map_benchmark, 
intervention = fixed('oilzflourfcubefflour'), 
time = IntSlider(min=1, max=10, step=1, value=1), 
optimum_interest = ['b', 'c', 'cdb', 'cdc', 'cb', 'cc'], 
bench_intervention = fixed('oilvaszflourfflour33'),
map_df = fixed(agg_geo_df),
merge_key = fixed('space'),
save = fixed(None))


# %%
interact(m_high.plot_map_benchmark, 
intervention = fixed(['maxoilcliniczflourfcubefflour','maxoilzflourfcubefflour']), 
time = IntSlider(min=1, max=10, step=1, value=1), 
optimum_interest = ['b', 'c', 'cdb', 'cdc', 'cb', 'cc'], 
bench_intervention = fixed('oilvaszflourfflour33'),
map_df = fixed(agg_geo_df),
merge_key = fixed('space'),
save = fixed(None))

# %% [markdown]
# ## Trying Out a Different Constraint
# 
# Now instead of having the benefit constraint be some aggregate across space and time, let's make sure that the constraint is time-specific, as in the benefits of the optimal solution have to be at least as much in every time period.

# %%


