import pandas as pd

from minimod.utils.summary import PreOptimizationDataSummary

df = pd.read_csv("examples/data/processed/example1.csv")

p = PreOptimizationDataSummary(data = df, 
                benefit_col = 'benefit', 
                cost_col = 'costs', 
                intervention_col= 'intervention', 
                space_col = 'space', 
                time_col = 'time', 
                benefit_title = 'Lives Saved',
                intervention_subset = ['vas', 'vasoil'])

p.summary_table(variables_of_interest= {'Cost per Child' : 'cost_per_benefit'}, grouping = 'over_space', style = 'word')

