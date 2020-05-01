# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Optimization Work'))
	print(os.getcwd())
except:
	pass
# %% [markdown]
# # Lives Saved Estimates with Python MINIMOD

# %%
import pandas as pd
import minimod
from glob import glob
from pathlib import Path


# %%
# Folder with data
data_folder = Path('demewoz_lives_saved', 'data_files')

# %% [markdown]
# ## Processing Data

# %%
# get all .xlsx files folder
data_files = data_folder.glob("*.xlsx")


# %%
# Read in data
for d in data_files:
    df = pd.read_excel(d)
    print(df)

# %% [markdown]
# ## Summary Statistics

# %%


# %% [markdown]
# 
