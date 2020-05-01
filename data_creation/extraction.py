"""This script creates the data that is used by the `Cameroon_maxvarobust2.gms` file. 

Used for Monte carlo simulations
"""

import pandas as pd
import numpy as np
import glob
from pathlib import Path
from xlrd import open_workbook
import re

# First import all the data in the robustness_data/data_gms_code folder
import os

# Get directory to file directory
benefit_cost_files = Path("robustness_data", "data_in_gms_code").glob(r"*.xlsx")
# Get its length for later
bc_f_length = len(list(Path("robustness_data", "data_in_gms_code").glob(r"*.xlsx")))

# The data files are a bit peculiar (although not if you use GAMS)
# There's an "index" sheet with the name of where the actual data is.
# So here's the directions:
# - use `xlrd` to inspect the files
# - find index sheet (using `re`)
# - look and find what the data sheet is called
# - open and create data from data sheet
#   - Process the data from data sheet (as it seems like there might be issues like there being extraneous numbers somewhere)

# Import the data and store it in a dict

data_dict = {}

for f in benefit_cost_files:

    # First open workbook and get list of sheets
    wb = open_workbook(f)

    # Get sheet names
    sheet_names = [s.name for s in wb.sheets()]

    # Get name of index sheet
    index_match_name = [re.findall(r"([Ii]ndex[a-zA-z]+)", s) for s in sheet_names]
    
    for found in index_match_name:
        if found:
            index_match_name = found[0]
    
    index_sheet = wb.sheet_by_name(index_match_name)
    # In the case where sheets are more than 2, we load up the index_sheet and find the name of the data sheet
    print(f"""
          Starting with {f.stem}
          """)
    
    cols_to_use = []
    where_col_names_are = []

    for i in range(index_sheet.nrows):
        for j in range(index_sheet.ncols):
            
            print(f"Printing cell [{i}, {j}]")
            value = index_sheet.cell(i,j).value
            
            if isinstance(value, str):

                searcher = re.compile(r'([A-Za-z0-9-]+)!([A-Z]+)([0-9]+):([A-Z]+)[0-9]+')
                
                print(value)
                try:
                    data_sheet = searcher.match(value).group(1)
                    where_to_start = searcher.match(value).group(3)
                    col_name_start = (searcher.match(value).group(2), searcher.match(value).group(4)) 
                    data_range = ':'.join(col_name_start)
                    print(col_name_start)
                    print(data_sheet)
                    print(col_name_start)
                    where_col_names_are.append(col_name_start)
                except AttributeError:
                    print("found nothing, continuing...")
                                    
    # Now we can finally get the remaining data
    data_dict[f.stem] = pd.read_excel(f, 
                                      sheet_name = data_sheet, 
                                      header = int(where_to_start) - 1 -1 , 
                                      usecols = data_range)
                
# Okay... small sanity check, we should see if the number of keys in the data_dict equals the number of paths in the list
if not bc_f_length == len(data_dict):
    print(f"We got {len(list(benefit_cost_files))} files and...")
    print(f"We got {len(data_dict)} in the data_dict")
    raise Exception("Noooooooo!!! Something went wrong during the loop!")

# Now that we have the files let's process them:

for key in data_dict:
    
    data_dict[key] = data_dict[key].dropna(subset = [data_dict[key].columns[1]]).reset_index()
    # Check if a time column exists
    if any(data_dict[key].columns.isin(['Unnamed: 1'])):
        
        data_dict[key].columns = data_dict[key].loc[0].tolist()

        data_dict[key] = data_dict[key].loc[1:].reset_index()
    
    if data_dict[key].loc[0].isin(['Intervention']).any():
        data_dict[key].columns = data_dict[key].loc[0]
        data_dict[key] = data_dict[key].loc[1:].reset_index()

    # If time is column, then check that there are 10 observations
    if data_dict[key].columns.isin(['Time', 'time']).any():
        if not len(data_dict[key]) >= 10:
            raise Exception("Time observations aren't Ten")

                    
    # check that each intervention has 3 occurrences, to make sure we didn't throw away data
    if data_dict[key].columns.isin(['Intervention', 'intervention']).any():
        if not len(set(data_dict[key]['Intervention'].value_counts().tolist()))== 1:
            raise Exception("Might have some data loss")
        
## Now let's clean the data up a bit

for key in data_dict:
    
    if 'Unnamed: 3' in data_dict[key].columns:
        
        if data_dict[key].loc[0].isin(['North', 'north']).any():
            
            data_dict[key].columns = data_dict[key].loc[0].tolist()
            data_dict[key] = data_dict[key].loc[1:].reset_index()
    
    # Let's check if any of the column names are nan
    if data_dict[key].columns.isna().any():
        if data_dict[key].columns.isna().sum() > 1:
            data_dict[key] = data_dict[key].dropna(axis=1, how = 'all')
            
        if data_dict[key][np.nan].isin(['cube', 'flour', 'oil', 'capsules']).any():
            data_dict[key] = data_dict[key].rename({np.nan : 'intervention' }, axis = 'columns')
        elif data_dict[key][np.nan].isin(['North', 'north']).any():
            data_dict[key] = data_dict[key].rename({np.nan : 'region' }, axis = 'columns')
        else:
            raise Exception("Some other kind of nan")             
    
    if 'index' in data_dict[key].columns:
        data_dict[key] = data_dict[key].drop(['index'], axis=1)   
    if 0 in data_dict[key].columns:
        data_dict[key] = data_dict[key].drop([0], axis=1)  
    
    
# Now do lowercase to all columns
for key in data_dict:
    
    data_dict[key].columns = data_dict[key].columns.str.lower().str.rstrip().str.lstrip()
    
    if 'region' in data_dict[key].columns:
        data_dict[key]['region'] = data_dict[key]['region'].str.lower()
    
# Now stack the data if region is wide
for key in data_dict:
    if 'north' in data_dict[key].columns:
        data_dict[key].columns.name = 'region'
        
        if 'time' in data_dict[key].columns:
            indexer = 'time'
        elif 'intervention' in data_dict[key].columns:
            indexer = 'intervention'
            
        data_dict[key] = data_dict[key].set_index(indexer).stack()
            
        

# Save each to a csv
for key in data_dict:
    
    data_dict[key].to_csv(f"robustness_data/data_in_gms_code/processed_data/{key}.csv")
    
