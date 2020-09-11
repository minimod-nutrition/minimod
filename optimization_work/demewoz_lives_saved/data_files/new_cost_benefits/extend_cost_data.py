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

def cost_intervention_creator(data: pd.DataFrame, 
                         intervention_subtractor : str,
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
    
    intervention_adder_df = (
        data
        .loc[lambda df: df['intervention'].isin([new_intervention])]
        .rename({'value' : 'value_adder'}, axis=1)
    )
    
    intervention_subtractor_df = (
        data
        .loc[lambda df: df['intervention'].isin([intervention_subtractor])]
        .rename({'value' : 'value_subtractor'}, axis=1)
        .loc[lambda df: ~df['intervention'].isin(int_exclude)]
    )
    
    intervention_stub_df = (
        data
        .loc[lambda df: \
            (df['intervention']
             .str
             .contains(intervention_subtractor))\
                 & (df['intervention'] != intervention_subtractor)]
        .loc[lambda df: ~df['intervention'].isin(int_exclude)]

    )
    
    # Merge the two
    df = (
        intervention_stub_df
        .merge(intervention_subtractor_df[['region', 'time', 'value_subtractor']], 
               on = ['region', 'time'])
        .merge(intervention_adder_df[['region', 'time', 'value_adder']],
               on = ['region', 'time'])
        .assign(
            new_value = lambda df: df['value'] - df['value_subtractor'] + df['value_adder'],
            intervention = lambda df: df['intervention'].str.replace(intervention_subtractor, '') + new_intervention
            )
        .rename({'value':'old_value', 'new_value' : 'value'}, axis=1)
    )
    
    return df[['intervention', 'region', 'time', 'value']]


def benefit_intervention_creator(data : pd.DataFrame,
                                 intervention_out : str,
                                 new_intervention : str,
                                 int_exclude : list,
                                 soft = False,
                                 no_name_replace = False,
                                 adjust = False) -> pd.DataFrame:
    
    # Get benefits with intervention we want
  
    
    if soft: 
        intervention_adder_df = (
            data
            .loc[lambda df: df['intervention'].str.contains(new_intervention)]
            .rename({'value' : 'value_adder'}, axis=1)
        ) 
    else:
        intervention_adder_df = (
            data
            .loc[lambda df: df['intervention'].isin([new_intervention])]
            .rename({'value' : 'value_adder'}, axis=1)
        )
    # Get all benefits with intervention out and get rid of the name
    # Then see how many exist
    if adjust:
        
        intervention_without_new = (
            data
            .sort_values(by = 'intervention')
            .loc[lambda df: ~df['intervention'].isin(int_exclude)]
            .loc[lambda df: \
                (df['intervention']
                .str
                .contains(intervention_out))\
                    & (df['intervention'] != intervention_out)]
            .assign(intervention_old = lambda df: df['intervention'],
                    intervention = lambda df: df['intervention'].str.replace(r'fflour|fcube', ''))
            .rename({'value' : 'value_old'}, axis=1)
        )
        
    else:
        intervention_without_new = (
            data
            .loc[lambda df: ~df['intervention'].isin(int_exclude)]
            .loc[lambda df: \
                (df['intervention']
                .str
                .contains(intervention_out))\
                    & (df['intervention'] != intervention_out)]
            .assign(intervention_old = lambda df: df['intervention'],
                    intervention = lambda df: df['intervention'].str.replace(intervention_out, ''))
            .rename({'value' : 'value_old'}, axis=1)
        )
        
    if no_name_replace:
        new_intervention = ''
            
    intervention_creation_df = (
        data
        # .loc[lambda df: ~df['intervention'].isin(int_exclude)]
        .merge(intervention_without_new, 
               on = ['intervention', 'region', 'time'])
        .merge(intervention_adder_df[['region', 'time', 'value_adder']],
               on = ['region', 'time'])
        .assign(new_value = lambda df: df['value'] + df['value_adder'])
    )
    
    if adjust:
        intervention_creation_df = (
            intervention_creation_df
            .assign(intervention = lambda df: df['intervention_old'])
            )
        
    else:
        intervention_creation_df = (
            intervention_creation_df
            .assign(intervention = lambda df: df['intervention'] + new_intervention)
            )
    
    
    return intervention_creation_df[['intervention','region', 'time', 'new_value']].rename({'new_value': 'value'}, axis=1)

# %%


# Costs

## zflour
# Okay this is how this is going to work:
# - Get all zflour interventions
# - drop zflour itself from that list, but keep the cost
# - subtract zflour costs from those interventions
# - get rid of 'zflour' in the name
# - create new interventions with fflour, zflourfflour

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

fflour = cost_intervention_creator(costs, 'zflour', 'fflour', int_exclude=int_out)
zflourfflour = cost_intervention_creator(costs, 'zflour', 'zflourfflour', int_exclude=int_out)

costs_with_fflour = (
    costs
    .append(fflour, ignore_index = True)
    .append(zflourfflour, ignore_index = True)
)
# %%
## fcube

# - Basically the same as flour, except:
#   - Since having zcube in the interventions makes 
#       things wonky, we only use the subset of cube 
#       interventions that don't have zcube in them

# Add the zcube interventions here to exclude
zcube_int = (
    costs_with_fflour
    .loc[lambda df: \
        df['intervention']
        .str
        .contains('zcube')]['intervention']
    .unique()
    .tolist()
    )

int_out_zcube = int_out + zcube_int

fcube = cost_intervention_creator(costs_with_fflour, 'cube', 'fcube', int_exclude=int_out_zcube)
cubefcube = cost_intervention_creator(costs_with_fflour, 'cube', 'cubefcube', int_exclude=int_out_zcube)
zcubefcube = cost_intervention_creator(costs_with_fflour, 'cube', 'zcubefcube', int_exclude=int_out_zcube)
cubezcubefcube = cost_intervention_creator(costs_with_fflour, 'cube', 'cubezcubefcube', int_exclude=int_out_zcube)

costs_final = reduce(lambda x,y: x.append(y, ignore_index=True), [costs_with_fflour,
                                                                  fcube,
                                                                  cubefcube,
                                                                  zcubefcube,
                                                                  cubezcubefcube])

# %%

# Benefits

## fflour

fflour_ben = benefit_intervention_creator(deathsaverted, 'zflour', 'fflour', int_exclude=int_out)

fflour_ben_high = benefit_intervention_creator(deathsaverted_high, 'zflour', 'fflour', int_exclude=int_out)


# fcube
fcube_ben = benefit_intervention_creator(deathsaverted, 'cube', 'fcube', int_exclude=int_out)

fcube_ben_high = benefit_intervention_creator(deathsaverted_high, 'cube', 'fcube', int_exclude=int_out)

# fflourfcube
fcubefflour_ben = benefit_intervention_creator(deathsaverted, 'cube', 'fcubefflour', int_exclude=int_out)

fcubefflour_ben_high = benefit_intervention_creator(deathsaverted_high, 'cube', 'fcubefflour', int_exclude=int_out)


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
        .loc[lambda df: df._merge == 'both']
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
        .loc[lambda df: df._merge == 'both']
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
        .loc[lambda df: df._merge == 'both']
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
