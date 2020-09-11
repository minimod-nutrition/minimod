# %%
#!%load_ext autoreload

# %%
#!%autoreload 2
import pandas as pd
from functools import reduce

# %%

data_path = 'optimization_work/demewoz_lives_saved/data_files/benefits_zincVAfolate_demwoaz_6_16_2020.xlsx'

deathsaverted = (
    pd.read_excel(data_path, 
                              sheet_name='deathsaverted',
                              header=2,
                              usecols='A:L')
    .rename({'Unnamed: 0' : 'intervention', 'Unnamed: 1' : 'region'}, axis=1)
    .set_index(['intervention', 'region'])
    .stack()
    .to_frame()
    .reset_index()
    .rename({'level_2' : 'time', 0 : 'value'}, axis=1)
    .assign(region = lambda df: df['region'].str.strip(),
            intervention = lambda df: df['intervention'].str.replace('cliniccube', 'cubeclinic')
            )
                 )

deathsaverted_high = (
    pd.read_excel(data_path, 
                sheet_name='deathsavertedhigh',
                header=2,
                usecols='A:L')
    .rename({'Unnamed: 0' : 'intervention', 'Unnamed: 1' : 'region'}, axis=1)
    .set_index(['intervention', 'region'])
    .stack()
    .to_frame()
    .reset_index()
    .rename({'level_2' : 'time', 0 : 'value'}, axis=1)
    .assign(region = lambda df: df['region'].str.strip(),
            intervention = lambda df: df['intervention'].str.replace('cliniccube', 'cubeclinic')
            )
    )

costs = (
    pd.read_excel(data_path, 
                    sheet_name='deathsavertedcost',
                    header=2,
                    usecols='A:L')
    .rename({'Unnamed: 0' : 'intervention', 'Unnamed: 1' : 'region'}, axis=1)
    .set_index(['intervention', 'region'])
    .stack()
    .to_frame()
    .reset_index()
    .rename({'level_2' : 'time', 0 : 'value'}, axis=1)
    .assign(region = lambda df: df['region'].str.strip(),
            intervention = lambda df: df['intervention'].str.replace('cliniccube', 'cubeclinic')
            )
    )

# %%

fcube_interventions = [
    'fcube', 
    'cube',
    'zcube',
    'cubezcube',
    'cubefcube',
    'zcubefcube',
    'cubezcubefcube'
    ]

fflour_interventions = ['fflour', 'zflour', 'zflourfflour']

fcubefflour_interventions = ['fcube',
                             'zflour', 
                             'zflourfflour', 
                             'fflour', 
                             'fcubefflour']

def cost_intervention_creator(data: pd.DataFrame, 
                         new_intervention : str,
                         int_exclude : list) -> pd.DataFrame:
    """Creates new costs for interventions where we subtract the cost of 
    ``intervention_subtractor`` and add the cost of ``new_intervention``, 
    excluding interventions in ``int_exclude``

    :param data: A pandas dataframe with cost data
    :type data: pandas.DataFrame
    :param intervention_subtractor: name of intervention to use for subtracting costs
    :type intervention_subtractor: str
    :param new_intervention: name of intervention whose costs add and use in creating new interventions
    :type new_intervention: str
    :param int_exclude: A list of interventions not to use for creating new ones
    :type int_exclude: list
    :return: new data with new interventions
    :rtype: pandas.DataFrame
    """    
    
    if new_intervention == 'fcube':
        new_intervention_list = fcube_interventions
    elif new_intervention == 'fflour':
        new_intervention_list = fflour_interventions
    elif new_intervention == 'fcubefflour':
        new_intervention_list = fcubefflour_interventions
        
    intervention_subtractor_df = (
    data
    .loc[lambda df: df['intervention'].isin(new_intervention_list)]
    .set_index(['region', 'time', 'intervention'])
    .unstack()
    )
    
    intervention_subtractor_df.columns = intervention_subtractor_df.columns.map(lambda x: x[1])
    
    intervention_subtractor_df.reset_index(inplace = True)
    
    intervention_stub_df = (
        data
        .loc[lambda df: ~df['intervention'].isin(int_exclude)]
    )
    
    # Merge the two
    df = (
        intervention_stub_df
        .merge(intervention_subtractor_df, 
               on = ['region', 'time'])
    )
    
    if new_intervention == 'fflour' :
        
        df['contains_int'] = (df['intervention'].str.contains('zflour')).astype(int)
    
        final_df = df.assign(new_value = lambda df: df['value'] +\
            df['contains_int']*(df['zflourfflour'] - df['zflour']) +\
                (1-df['contains_int'])*df['fflour'],
                intervention = lambda df: df['intervention'] + new_intervention
                             )
        
    elif new_intervention == 'fcube':
        
        df['contains_cube'] = (df['intervention'].str.contains(r'^(?=.*cube)(?!.*zcube).*')).astype(int)
        df['contains_zcube'] = (df['intervention'].str.contains(r'zcube') & ~df['intervention'].str.contains(r'(?<!z)cube')).astype(int)
        df['contains_cubezcube'] = (df['intervention'].str.contains(r'cubezcube')).astype(int)
        
        final_df = df.assign(new_value = lambda df: df['value'] +\
            df['contains_cube']*(df['cubefcube'] - df['cube']) +\
                df['contains_zcube']*(df['zcubefcube'] - df['zcube']) +\
                    df['contains_cubezcube']*(df['cubezcubefcube'] - df['cubezcube']) +\
                        (1- df['contains_cube'] - df['contains_zcube'] - df['contains_cubezcube'])*(df['fcube']),
                intervention = lambda df: df['intervention'] + new_intervention
                             )
    
    elif new_intervention == 'fcubefflour':
        
        df['contains_int'] = (df['intervention'].str.contains('zflour')).astype(int)
    
        final_df = df.assign(new_value = lambda df: df['value'] +\
            df['contains_int']*(df['zflourfflour'] - df['zflour']) +\
                (1-df['contains_int'])*df['fflour'],
                intervention = lambda df: df['intervention'] + new_intervention
                             )       
    
    return final_df.rename({'value':'old_value', 'new_value' : 'value'}, axis=1)[['intervention', 'region', 'time', 'value']].loc[lambda df: ~df['intervention'].isin(int_exclude)]


def benefit_intervention_creator(data,
                                 new_intervention,
                                 int_exclude):
    
    intervention_adder_df = (
        data
        .loc[lambda df: df['intervention'].isin([new_intervention])]
        .rename({'value' : 'value_adder'}, axis=1)
    )
    
    intervention_stub_df = (
        data
        .loc[lambda df: ~df['intervention'].isin(int_exclude)]
    )
    
    # Merge the two
    df = (
        intervention_stub_df
        .merge(intervention_adder_df[['region', 'time', 'value_adder']],
               on = ['region', 'time'])
        .assign(
            new_value = lambda df: df['value'] + df['value_adder'],
            intervention = lambda df: df['intervention'] + new_intervention
            )
        .rename({'value':'old_value', 'new_value' : 'value'}, axis=1)
        .loc[lambda df: ~df['intervention'].isin(int_exclude)]

    )
    
    return df[['intervention', 'region', 'time', 'value']]

# %%


# Costs



int_out = [
'fflour',
'fflour33',
'fcube',
'fcubefflour',
'zflourfflour',
'cubefcube',
'zcubefcube',
'cubezcubefcube',
'zflourfflour33',   
'oilvaszflourfflour33'
]

## zflour
# Okay this is how this is going to work:
# - Get all zflour interventions
# - drop zflour itself from that list, but keep the cost
# - subtract zflour costs from those interventions
# - get rid of 'zflour' in the name
# - create new interventions with fflour, zflourfflour

fflour = cost_intervention_creator(costs, 'fflour',  int_exclude=int_out)

# %%
## fcube

# - Basically the same as flour, except:
#   - Since having zcube in the interventions makes 
#       things wonky, we only use the subset of cube 
#       interventions that don't have zcube in them


fcube = cost_intervention_creator(costs, 'fcube', int_exclude=int_out)

# fcubefflour

fcubefflour = cost_intervention_creator(costs, 'fcubefflour', int_exclude=int_out)


costs_final = reduce(lambda x,y: x.append(y, ignore_index=True), [costs,
                                                                  fcube,
                                                                  fflour,
                                                                  fcubefflour])

# %%

# Benefits

## fflour

fflour_ben = benefit_intervention_creator(deathsaverted, 'fflour', int_exclude=int_out)

fflour_ben_high = benefit_intervention_creator(deathsaverted_high, 'fflour', int_exclude=int_out)

# fcube
fcube_ben = benefit_intervention_creator(deathsaverted, 'fcube', int_exclude=int_out)

fcube_ben_high = benefit_intervention_creator(deathsaverted_high, 'fcube', int_exclude=int_out)

# fcubefflour
fcubefflour_ben = benefit_intervention_creator(deathsaverted, 'fcubefflour', int_exclude=int_out)

fcubefflour_ben_high = benefit_intervention_creator(deathsaverted_high, 'fcubefflour', int_exclude=int_out)

# %%

# No we append everything and make the final adjustment for 
# fcubefflour

deathsaverted_all = reduce(lambda x,y: x.append(y, ignore_index=True), [deathsaverted,
                                                                        fflour_ben,
                                                                        fcube_ben, 
                                                                        fcubefflour_ben])


deathsaverted_high_all = reduce(lambda x,y: x.append(y, ignore_index=True), [deathsaverted_high,
                                                                             fflour_ben_high,
                                                                             fcube_ben_high, 
                                                                             fcubefflour_ben_high])

# %%

# Merge costs and benefits to make sure they're all the same
all_data = deathsaverted_all.merge(costs_final,
                                     on = ['intervention', 'region', 'time'],
                                     indicator = True,
                                     how= 'outer')

# %%
all_data_high = deathsaverted_high_all.merge(costs_final,
                                     on = ['intervention', 'region', 'time'],
                                     indicator = True,
                                     how= 'outer')

# %%

# Keep only inner merge, unstack by time and save to excel

ordered_region = pd.CategoricalDtype(categories = ['North', 'South', 'Cities'], ordered=True)

excel_path = 'optimization_work/demewoz_lives_saved/data_files/new_cost_benefits/lives_saved_costs.xlsx'

with pd.ExcelWriter(excel_path) as writer: 

    (
        all_data
        .assign(region = lambda df: df['region'].astype(ordered_region))
        .rename({'value_x' : 'lives_saved', 
                'value_y' : 'costs'}, axis=1)
        .set_index(['intervention', 'region', 'time'])
        ['lives_saved']
        .unstack()
        .reset_index()
        .to_excel(writer, sheet_name = 'lives_saved', index = False)
        )


    (
        all_data_high
        .assign(region = lambda df: df['region'].astype(ordered_region))
        .rename({'value_x' : 'lives_saved', 
                'value_y' : 'costs'}, axis=1)
        .set_index(['intervention', 'region', 'time'])
        ['lives_saved']
        .unstack()
        .reset_index()
        .to_excel(writer, sheet_name = 'lives_saved_high', index= False)
        )

    (
        all_data
        .assign(region = lambda df: df['region'].astype(ordered_region))
        .rename({'value_x' : 'lives_saved', 
                'value_y' : 'costs'}, axis=1)
        .set_index(['intervention', 'region', 'time'])
        ['costs']
        .unstack()
        .reset_index()
        .to_excel(writer, sheet_name = 'costs', index = False)
        )

# %%
