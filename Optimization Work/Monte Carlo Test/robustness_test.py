# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Optimization Work/Monte Carlo Test'))
	print(os.getcwd())
except:
	pass
# %%
from IPython import get_ipython

# %% [markdown]
# # Testing Python MINIMOD against GAMS MINIMOD using Cameroon Data
# 
# GAMS code comes from [Cameroon_maxvarobust2.gms](robustness_data/Cameroon_maxvarobust2.gms)

# %%


# %%
import pandas as pd
import os

from minimod import MonteCarloMinimod, Minimod

# %% [markdown]
# ## Getting the Data Ready

# %%
data = "/home/lordflaron/Documents/GAMS-Python/Monte Carlo/robustness_data/"


df_costs = (
    pd.read_csv(data + 'cost_data.csv')
    .set_index(['intervention', 'region', 'time'])
    )

df_eff_coverage = (
    pd.read_csv(data +"data_in_gms_code/processed_data/benefits_8_13_2018_maxdata.csv")
    .drop(['Unnamed: 0'], axis=1)
    .replace(to_replace={'north' : 'North', 'south' : 'South', 'cities' : 'Cities'})
    .set_index(['intervention', 'region'])
    )

df_pop = (
    pd.read_csv(data + "data_in_gms_code/processed_data/Age-group_pop_2015data.csv")
    .rename({'0' : 'population'}, axis=1)
    .replace(to_replace={'north' : 'North', 'south' : 'South', 'cities' : 'Cities'})
    .set_index(['region', 'time'])    
)


# %%
# put benefits together with population

df_benefits = (
    df_eff_coverage
    .merge(df_pop, left_index = True, right_index = True)
    .assign(benefit_mean = lambda df: df['mean']*df['population'],
            benefit_sd = lambda df: df['sd']*df['population']
            )
    .reset_index()
    .set_index(['intervention', 'region', 'time'])
)


# %%

def data_revision(ben_data, 
                  intervention_to_replace,
                  intervention_new,
                  time_to_replace,
                  region_to_replace,
                  eff_cov_data = df_eff_coverage, 
                  pop_data = df_pop):
    
    # Merge population data and benefits data at specified 
    # intervention and time period
    revised_values = (
        eff_cov_data
        .loc[(intervention_new, region_to_replace), :]
        .merge(pop_data
               .loc[(region_to_replace, time_to_replace), :], 
               left_index = True, 
               right_index = True)
        .assign(new_ben_mean = lambda df: df['mean']*df['population'],
                new_ben_sd = lambda df: df['sd']*df['population'])
        [['new_ben_mean', 'new_ben_sd']]
        .reset_index()
        .set_index(['intervention', 'region', 'time'])
        .sort_index()
        .values
        )
    
    df = ben_data.copy(deep=True)
    
    # Now get data that will be replaced    
    df.loc[(intervention_to_replace, 
                  region_to_replace, 
                  time_to_replace), ['benefit_mean', 'benefit_sd']] = revised_values
    
    print(f"Done with {intervention_to_replace}")

    return df

def observation_revision(ben_data, 
                         values_to_replace,
                         intervention_to_replace,
                         region_to_replace,
                         time_to_replace,
                         pop_data = df_pop
                         ):
    
    df = ben_data.copy(deep=True)
    
    df.loc[(intervention_to_replace, region_to_replace, time_to_replace), 
           ['benefit_mean', 'benefit_sd']] = \
               values_to_replace*pop_data.loc[(region_to_replace, time_to_replace)].values
    
    print(f"Changed {intervention_to_replace} to {values_to_replace} in {region_to_replace}")
    
    return df
    
    
    


# %%
## Now we make all the changes that were in the GAMS file.

new_benefits_df = (
    df_benefits
    .pipe(data_revision, 
          intervention_to_replace = 'fortoil',
          intervention_new = 'dwoil',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'capoil',
          intervention_new = 'capdwoil',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'oilcube',
          intervention_new = 'capdwoil',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'capoilcube',
          intervention_new = 'capdwoilcube',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'capoilmaize',
          intervention_new = 'capdwoilmaize',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'oilmaize',
          intervention_new = 'dwoilmaize',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'oilcubemaize',
          intervention_new = 'dwoilcubemaize',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(data_revision,
          intervention_to_replace = 'capoilcubemaize',
          intervention_new = 'capdwoilcubemaize',
          time_to_replace = 1,
          region_to_replace = slice(None))
    .pipe(observation_revision,
        values_to_replace = [0.188647039,0.056720184],
        intervention_to_replace = 'fortoil',
        region_to_replace = 'South',
        time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.184657986,0.051138841],
          intervention_to_replace = 'fortoil',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.361048462,0.052177091],
          intervention_to_replace = 'fortoil',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.271910918,0.03636394],
          intervention_to_replace = 'capoil',
          region_to_replace = 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.552711992,0.043181427],
          intervention_to_replace = 'capoil',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.429750048,0.027707883],
          intervention_to_replace = 'capoil',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.317578384,0.041965529],
          intervention_to_replace = 'oilcube',
          region_to_replace = 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.452445346,0.062957324],
          intervention_to_replace = 'oilcube',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.460061855,0.034025083],
          intervention_to_replace = 'oilcube',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.335812702,0.335812702],
          intervention_to_replace = 'capoilcube',
          region_to_replace = 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.66038935,0.66038935],
          intervention_to_replace = 'capoilcube',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.481598393,0.481598393],
          intervention_to_replace = 'capoilcube',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.281736205,0.281736205],
          intervention_to_replace = 'capoilmaize',
          region_to_replace = 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.449118915,0.449118915],
          intervention_to_replace = 'capoilmaize',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.381499444,0.381499444],
          intervention_to_replace = 'capoilmaize',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.193206296,0.039506241],
          intervention_to_replace = 'oilmaize',
          region_to_replace = 'South',
          time_to_replace = 2
          )
    .pipe(observation_revision,
          values_to_replace = [0.298684737,0.044670404],
          intervention_to_replace = 'oilmaize',
          region_to_replace = 'North',
          time_to_replace = 2
          )
    .pipe(observation_revision,
          values_to_replace = [0.314661303,0.031472923],
          intervention_to_replace = 'oilmaize',
          region_to_replace = 'Cities',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.281736205,0.038565253],
          intervention_to_replace = 'oilcubemaize',
          region_to_replace = 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace= [0.449118915,0.046413903],
          intervention_to_replace = 'oilcubemaize',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.381499444,0.033349636],
          intervention_to_replace = 'oilcubemaize',
          region_to_replace = 'Cities',
          time_to_replace=2)
    .pipe(observation_revision,
          values_to_replace= [0.331342794,0.032749485],
          intervention_to_replace= 'capoilcubemaize',
          region_to_replace= 'South',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.662643196,0.040875425],
          intervention_to_replace = 'capoilcubemaize',
          region_to_replace = 'North',
          time_to_replace = 2)
    .pipe(observation_revision,
          values_to_replace = [0.471177607,0.02437671],
          intervention_to_replace = 'capoilcubemaize',
          region_to_replace = 'Cities',
          time_to_replace = 2)
)



# %%
# Now we put together with costs

df_ready = (
    new_benefits_df
    .merge(df_costs, left_index = True, right_index = True)
    .reset_index()
)


# %%
df_ready

# %% [markdown]
# ## Running a non-Monte Carlo Run
# 
# Since one run of the GAMS code is a non-Monte Carlo run
# 

# %%
# "First" "create" "the" "interventions" "for" "constraints"
oil = ["fortoil", "capoil",  "mnpoil", "oilcube", "oilcdti", "oilhf",
             "capmnpoil",  "capoilcube", "mnpoilcube", "oilmaizehf",
              "oilcubecdti", "oilcubehf", "capmnpoilcube",
              "oilmaize", "oilcubemaize", "capoilmaize",
              "oilmnpmaize", "capoilmnpmaize", "dwoilmnpmaize", "capoilcubemaize",
              "oilcubemnpmaize",  "oilcubemaizecdti", "oilcubemaizehf",
              "capoilcubemnpmaize", "oilbcc", "oilcubebcc", "oilmaizebcc", "oilcubemaizebcc" ]


cube = ["fortcube",  "oilcube", "cubecdti", "cubehf",
             "capcube", "dwcube", "mnpcube", "mnpdwcube", "capmnpcube", "capdwcube", "capdwmnpcube", "oilcubecdti", "oilcubehf",
              "capoilcube", "mnpoilcube", "dwoilcube", "capdwoilcube", "capmnpoilcube", "dwmnpoilcube", "capdwmnpoilcube",
               "cubemaize", "oilcubemaize", "capcubemaize", "dwcubemaize",   "cubemaizehf",
               "cubemnpmaize", "capdwcubemaize", "capcubemnpmaize", "capoilcubemaize", "oilcubemaizecdti", "oilcubemaizehf",
               "dwoilcubemaize", "dwcubemnpmaize", "oilcubemnpmaize", "capdwoilcubemaize", "capdwcubemnpmaize",
               "capoilcubemnpmaize", "dwoilcubemnpmaize", "capdwoilcubemnpmaize", "cubebcc", "oilcubebcc", "cubemaizebcc", "oilcubemaizebcc" ]

maize= ["maize", "oilmaize", "cubemaize", "capmaize", "dwmaize", "mnpmaize", "maizecdti", "oilmaizecdti", "cubemaizecdti",
               "maizehf", "oilmaizehf", "cubemaizehf", "oilcubemaize",
               "capoilmaize", "dwoilmaize", "capdwmaize", "capcubemaize", "dwcubemaize", "capmnpmaize",
               "dwmnpmaize", "oilmnpmaize", "cubemnpmaize", "oilcubemaizecdti", "oilcubemaizehf", "capdwcubemaize", "capcubemnpmaize", "capdwmnpmaize",
               "capdwoilmaize", "capoilcubemaize", "capoilmnpmaize",  "dwoilcubemaize",
               "dwoilmnpmaize", "dwcubemnpmaize", "oilcubemnpmaize", "capdwoilmnpmaize", "capdwoilcubemaize",
               "capdwcubemnpmaize", "capoilcubemnpmaize", "dwoilcubemnpmaize", "capdwoilcubemnpmaize", "maizebcc", "oilmaizebcc", "cubemaizebcc", "oilcubemaizebcc"  ]

nat = ["fortoil", "fortcube",
              "maize", "oilcube", "oilmaize", "cubemaize", "oilcubemaize"   ]

flour = ["flour", "flourcube",
             "suppflour", "mnpflour", "mnpsuppflour", "mnpflourcube", "suppflourcube", "mnpsuppflourcube"]

folateflour = ["flour", "mnpflour", "flourcube"]

ironflour = ["flour", "flourcube", "mnpflour", "mnpflourcube"]

b12flour = ["flour", "flourcube", "mnpflour"]

b12cube = ["cube", "flourcube", "mnpcube"]

zinccube = ["cube",  "flourcube",
                 "suppcube", "mnpcube", "mnpsuppcube", "mnpflourcube", "suppflourcube", "mnpsuppflourcube" ]

ironcube = ["cube",  "flourcube", "mnpcube", "mnpflourcube" ]

folatecube = ["fortcube", "flourcube" ]

mnp = ["mnp", "capmnp", "dwmnp", "mnpoil", "capdwmnp", "capmnpoil", "dwmnpoil", "mnpdwcube", "capmnpcube", "capdwmnpcube",
             "mnpoilcube", "capmnpoilcube", "dwmnpoilcube", "capdwmnpoilcube",  "mnpmaize", "capmnpmaize",
               "dwmnpmaize", "oilmnpmaize", "cubemnpmaize", "capcubemnpmaize", "capdwmnpmaize",
               "dwoilmnpmaize", "dwcubemnpmaize", "oilcubemnpmaize", "capdwoilmnpmaize",
               "capdwcubemnpmaize", "capoilcubemnpmaize", "dwoilcubemnpmaize", "capdwoilcubemnpmaize",
                 "mnpcube", "mnpsupp", "mnpflour", "mnpsuppflour", "mnpsuppcube", "mnpflourcube", "mnpsuppflourcube"  ]

cap = ["capsules", "capoil", "capcube", "capmnp", "capdw", "capmaize",
             "capdwoil", "capdwcube", "capoilcube", "capoilmaize", "capdwmnp", "capmnpoil", "capmnpcube", "capdwmaize", "capcubemaize", "capmnpmaize",
             "capdwmnpcube", "capmnpoilcube", "capdwoilcube", "capdwmnpoil", "capdwoilmaize", "capdwcubemaize", "capdwmnpmaize", "capoilcubemaize", "capoilmnpmaize", "capcubemnpmaize"
             "capdwmnpoilcube", "capdwoilmnpmaize", "capdwoilcubemaize", "capdwcubemnpmaize", "capoilcubemnpmaize",
             "capdwoilcubemnpmaize"  ]

dw = ["dwoil", "dwoilcube", "capdwoilcube", "dwcube", "capdwoil", "capdwcube", "dwmaize", "dwoilmaize", "capdwmaize", "dwcubemaize", "capdwoilmaize", "dwoilcubemaize", "capdwoilcubemaize"  ]

mnpzinc = ["mnp", "mnpcube", "mnpsupp", "mnpflour", "mnpsuppflour", "mnpsuppcube", "mnpflourcube", "mnpsuppflourcube"  ]

cdti = ["cdti", "oilcdti", "cubecdti", "maizecdti", "oilcubecdti", "oilmaizecdti", "cubemaizecdti", "oilcubemaizecdti" ]

hf = ["hf", "oilhf", "cubehf", "maizehf", "oilcubehf", "oilmaizehf", "cubemaizehf", "oilcubemaizehf" ]


# %%





# %%
# Run Montecarlo

a = MonteCarloMinimod(solver_type = 'costmin', 
                        data = df_ready, 
                        intervention_col='intervention',
                        space_col='region',
                        time_col='time',
                        benefit_mean_col = 'benefit_mean',
                        benefit_sd_col= 'benefit_sd',
                        cost_col='costs')


# %%
sim = a.fit_all_samples(N = 2,
                        all_space = ['oil', 
                                     'cube', 
                                     'maize'
                                     ],
                        all_time = [
                            'cube',
                            'maize'
                        ],
                        time_subset= [1,2,3],
                        minimum_benefit = 'capdwoil')



# %%
a.report(perc_intervention_appeared=True, 
         avg_time = True,
         avg_space = True)


# %%

a.plot_opt_hist(save = "sim_results.png")



# %%
a.plot_sim_trajectories(save = 'sim_traj.png')


# %%

a.plot_intervention_stacked(intervention_group=['cube', 'maize', 'cap'])
