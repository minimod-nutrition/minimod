# %%
#!%load_ext autoreload
# %%
#!%autoreload 2
import sys
import pandas as pd
import geopandas as gpd
import os
import minimod as mm

# %%
mean_sd_excel = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/Monte Carlo/New2/benefits_8_13_2018_maxdata.xlsx"

pop_excel = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/Monte Carlo/New2/Age-group_pop_final.xlsx"

benefits_excel_file = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/GAMS_R Project/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"


# %%

discount_costs = 1/(1 + 0.03)


vasoilold_constraint = 15958219.409955183


# %%

# Import means and standard deviations

# TODO As constructing costs and benefits are more complicated than I originally thought, I'm going to make fake data from the cameroon data.

# df_mean_sd = (
#     pd.read_excel(
#     mean_sd_excel,
#     sheet_name="Datacoverage",
#     header=1,
#     nrows = 66)[['Intervention', 'Region', 'mean', 'sd']]
#     .set_index(['Region'])
#     )

# # import population data

# df_pop = (
#     pd.read_excel(pop_excel, 
#                        header= 2,
#                        sheet_name = '6-59mos',
#                        nrows = 26)[['Year', 'South', 'Cities', 'North']]
#     .set_index(['Year'])
#     .stack()
#     .reset_index()
#     .rename({
#         'level_1' : 'Region',
#         0 : 'pop'
#     }, axis = 'columns')
#     .pivot(index = 'Region', columns = 'Year', values = 'pop')
#     )

# df = (
#     df_mean_sd
#     .merge(df_pop, left_index = True, right_index = True)
#     .reset_index()

#     .set_index(['Intervention', 'Region'])
#     .sort_index()
#     [['mean', 'sd', 2011]] ## Leaving 2011 as pop_weight
#     )
import os; print(os.getcwd())
df = (
    pd.read_csv("examples/data/processed/example1.csv")
    .assign(benefit_sd = lambda df: df['benefit']/2,
            costs_sd = lambda df: df['costs']/2)
    )

# %%
a = mm.MonteCarloMinimod(solver_type = 'costmin', 
                        data = df, 
                        intervention_col='intervention',
                        space_col='space',
                        time_col='time',
                        benefit_mean_col = 'benefit',
                        benefit_sd_col= 'benefit_sd',
                        cost_col='costs',
                        minimum_benefit = vasoilold_constraint)

sim = a.fit_all_samples(N = 100)


# %%
a.plot_opt_hist(save = "sim_results.png")

# %%
a.report(perc_intervention_appeared=True)


# %%
a.plot_sim_trajectories(save = 'sim_traj.png')