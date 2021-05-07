import pandas as pd
import numpy as np

increment= np.linspace(0,10,100)

# create benefits data
func_benefits = lambda x, L, k, x0: L/(1 + np.exp(-k*(x - x0)))

func_costs = lambda x, m, b: m*x + b

np.random.seed(1729)
noise = 0.2 * np.random.normal(size=increment.size)

benefits = func_benefits(increment, 5, .1, 2) + noise

costs = func_costs(increment, 5, 1000) + noise



df = pd.DataFrame({'increment' : increment,
                    'benefits' : benefits,
                    'costs' : costs,
                    'vehicle' : 'Bouillon'})

## Add wheat flour

df = df.append(pd.DataFrame({'increment' : increment + .2,
                    'benefits' : benefits*.9,
                    'costs' : costs*1.2,
                    'vehicle' : 'Maize Flour'}))