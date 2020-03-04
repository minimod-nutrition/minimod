---
title: 'Minimod: A Mixed Integer Solver for Spatio-Temporal Optimal Nutrition Intervention'
author: 'Aleksandr Michuda'
output: pdf_document
fontsize: 12pt
geometry: margin=1in
linestretch: 2
---  

`minimod` is a solver written in python that solves the optimal nutrition intervention over space and time. It uses `mip` a mixed integer solver that uses the `CBC` solver, a fast, extensible and open-source linear solver. `minimod` comes with some constraints baked in and the underlying `mip` model is exposed and can be used for adding custom constraints if needed.

The problem that `minimod` solves initially can be written like so:

$$
\begin{array}{c}{\operatorname{Max} \sum_{k} \sum_{t} Y_{k, t} \sum_{j} \frac{E f C v g_{k j, t}}{(1+r)^{t}}} \\ +\sum_{k} \sum_{j} \sum_{t} X_{k, j, t} \frac{E f C v g_{k, j, t}}{(1+r)^{t}} \\ s.t. \\ \begin{array}{l}{\sum_{k} \sum_{t} Y_{k, t} \sum_{j} \frac{\mathrm{TC}_{k, j, t}}{(1+i)^{t}}} \\ {+\sum_{k} \sum_{j} \sum_{t} X_{k, j, t} \frac{\mathrm{TC}_{k, j, t}}{(1+i)^{t}} \leq \mathrm{TF}}\end{array} \end{array}
$$

which essentially maximizes discounted coverage given a budget constraint. This problem can give solutions that are both time and space specific. The dual problem minimizes discounted costs given a minimum coverage constraint.

## Quickstart

In order to run the model, we need to first import `minimod` and `pandas` in order to later load in our data:

```{.python .cb.nb jupyter_kernel=python}

import minimod as mm
import pandas as pd
```


Now we load in data and instantiate the model we want (`BenefitSolver` or `CostSolver`).

The solvers take several arguments:

- data -> a pandas dataframe of benefits and cost data. This data needs to be of a certain form, mainly a long form of data.
    - Default: None

|k     | j   |t   | benefits   | costs |
|------|-----|----|------------|-------|
|maize |north|0   | 100        | 10    |
|maize |south|0   | 50         | 20    |
|maize |east |0   | 30         |30     |
|maize |west |0   | 20         |40     |

- `intervention_col` -> the name of the intervention variable
    - Default: 'intervention'
- `space_col` -> the name of the spatial variable
    - Default: 'space'
- `time_col` -> the name of the time variable
    - Default: 'time'
- `benefit_col` -> the name of the benefit variable
    - Default: 'benefit'
- `cost_col` -> the name of the cost variable
    - Default: 'costs'
- `interest_rate_cost` -> the interest rate on costs
    - Default: 0.0
-`interest_rate_benefit` -> the interest rate on benefits
    - Default: 0.03
- `va_weight` -> The weight to give the benefits during intervention
    - Default: 1.0

For `BenefitSolver`, we also have:

- total_funds -> Maximum Budget
    - Default: 35821703

And for `CostSolver`:

- minimum_benefit -> The Minimum benefit constraint
    - Default: 15958220

Now we load the data and instantiate the solver:

```{.python .cb.nb}

df = pd.read_csv('../../examples/data/processed/example1.csv')

c = mm.CostSolver(data = df)

```

We then fit the model:

```{.python .cb.nb}

c.fit()

```

The optimal interventions are stored in an attribute available after fitting:

```{.python .cb.nb}

opt_df = c.opt_df
```

We can graph the costs and benefits through time from this:

```{.python .cb.nb}

%matplotlib inline

import matplotlib.pyplot as plt

opt_df.groupby('time').sum()[['opt_benefit', 'opt_costs']].plot()
```

Then we can generate a report 

```{.python .cb.nb}

c.report()

```
