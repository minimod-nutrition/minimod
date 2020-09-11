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
import geopandas as gpd
```

```{.python .cb.nb hide=all}
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('retina')
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

Now we load the data and calculate the minimum coverage constraint based on the variable `vasoilold`

```{.python .cb.nb hide=all}
discount_costs = 1/(1 + 0.03)

excel_file = "/home/lordflaron/Documents/GAMS-Python/Cameroon VA/GAMS_Working/GAMS_R Project/Katie_VA_Benefits_and_Costs_1_8_2019.xlsx"

vasoilold_constraint = (
pd.read_excel(excel_file,
                sheet_name = 'Benefits',
                header = 2)
.loc[lambda df : df['intervention'] == 'vasoilold']
.set_index(['intervention', 'space'])
.stack()
.to_frame()
.reset_index()
.rename({
    'level_2' : 'time',
    0 : 'benefit'
}, axis= 'columns')
.assign(
    time_rank = lambda df: (df['time'].rank(numeric_only=True, method= 'dense') -1).astype(int) ,
    time_discount_costs = lambda df: discount_costs**df['time_rank'],
    discounted_benefits = lambda df: df['time_discount_costs']*df['benefit']
)
['discounted_benefits'].sum()

)

```

```{.python .cb.nb }

df = pd.read_csv('../../examples/data/processed/example1.csv')

c = mm.CostSolver(minimum_benefit = vasoilold_constraint)

```

We then fit the model:

```{.python .cb.nb}

c.fit(data = df)

```

The optimal interventions are stored in an attribute available after fitting:

```{.python .cb.nb}

opt_df = c.opt_df
```

Then we can generate a report 

```{.python .cb.nb}

c.report()

```

### More Complicated Constraints

Oftentimes, it becomes necessary to add additional constraints to the model. This can include assumptions about costs, such that the cost structure of an intervention assumes start-up costs that forces an intervention to persist through time if those start-up costs are paid at some point. Or there may be assumptions about how certain interventions must be rolled out to all or part of a country (such as a national intervention). `minimod` allows for such constraints through the fit method with the `all_space` and `all_time` arguments. If interventions are dependent on start-up costs from certain periods of time, or that an intervention can be rolled out subnationally but to certain larger groups of regions, we can use `time_subset` and `space_subset`, respectively, to specify that.

Let's say that you know that the interventions "cube", "oil" and "maize" must be rolled out nationally and that "maize" and "cube" have startup costs in the first three time periods, so that if those costs are paid in those time periods, then the interventions must take place for the rest of time. 

Then we can write the fitter method like so:

```{.python .cb.nb}
opt = c.fit(data = df, 
            all_space = ['cube', 'oil', 'maize'], 
            all_time = ['maize', 'cube'],
            time_subset = [1,2,3]
            )
```

And then we can create another report:

```{.python .cb.nb}
c.report()
```

## Plotting with `minimod`

There are three basic ways `minimod` can plot results: time trends, histograms, and maps.

Once optimization has occurred, we can plot the optimal coverage, and optimal costs over time with the `plot_time` method and save it to a directory of our choice:

```{.python .cb.nb}
c.fit(data = df)
c.plot_time(save = "time.png")
```

Or we can plot the histogram of optimal interventions:

```{.python .cb.nb}

c.plot_opt_val_hist(save = "hist.png")
```

### Plotting Maps

With maps, there are several things that need to be done first: a shape file must be downloaded externally, and then a column in the resulting dataframe (using `geopandas`) must have the same values as the spatial data in the coverage and cost data. In the case of Cameroon, we downloaded a shape file and created the correct column and called it "space":

```{.python .cb.nb}

# Load data
geo_df = gpd.read_file("../../examples/data/maps/cameroon/CAM.shp")

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
```

Then we use that data as an input into our map method, `plot_chloropleth`:

```{.python .cb.nb}
c.plot_chloropleth(intervention='vasoil',
                   time = [5],
                   optimum_interest='c',
                   map_df = agg_geo_df,
                   merge_key= 'space',
                   save = "map.png")
```
`plot_chloropleth` allows us to choose a particular intervention to map (in this case "vasoil"), at a particular time period, and looking at optimal costs (`optimum_interest = 'c'`), and then save it.

If we want to see how the chloropleth changes through time, we can plot some subset of time, or if we omit the `time` parameter altogether, it will create maps for all time periods.

```{.python .cb.nb}
c.plot_chloropleth(intervention = 'vasoil',
                   optimum_interest='c',
                   map_df = agg_geo_df,
                   merge_key= 'space',
                   save = "map2.png")
```

## A Note about Constraint Choice

The `all_*` constraints described above differ in the python implementation and the GAMS implementation, because I found an inconsistency in the GAMS results that wasn't in the spirit of what I though the constraint was for. To illustrate, here is a simplified example:

In GAMS the relevant constraints are coded like so:

```
yescubeeq(j,t)..       yescube(j,t) =e= sum((cubek),x(cubek,j,t)) ;

allcubeeq(j,jj,t)..          yescube(j,t) =e= yescube(jj,t) ;
```
where j and jj are aliases for space.

So in terms of math, this is what I think the all cube constraint is saying, and let’s assume that there are just two cube interventions, $c1$ and $c2$:

$$
x_{c1, j, t} + x_{c2, j, t} = x_{c1, jj, t} + x_{c2, jj,t} \forall j \neq jj
$$

In this case, since x is binary, there are three possible options:

| Possibilities |	Sum |
|---------------|-------|
|Both 1	        |2      |
|$x_{c1,j,t}=1$ and $x_{c2,j,t}=0$ |	1 |
| $x_{c1,j,t}=0$ and $x_{c2,j,t}=1$ |	1 |
|Both 0|	0 |

If my understanding of the constraint is correct, its function is to say that “if a cube (so one of cube, vascube, oilcube, etc…) interventions is used in some region, then it must be used in all regions.” In that case, the constraint should be written:

$$
x_{c, j, t} = x_{c, jj, t} \text{for } c \in \{c1, c2\} \forall j \neq jj
$$

If that’s the case, when the variables are both 0 or both 1, that constraint works, but when one of them are 1 and the other 0, it you could have a situation when $x_{c1,j,t}=0$, but $x_{c1,jj,t}=1$, for example. This is a way that optimization can satisfy the constraint, but not actually satisfy what the constraint should be doing.

I have decided to implement it in the way described at the beginning:

$$
x_{c1, j, t} + x_{c2, j, t} = x_{c1, jj, t} + x_{c2, jj,t} \forall j \neq jj
$$
