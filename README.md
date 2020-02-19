# minimod
A mixed-integer solver that solves optimal intervention allocation across time and space (Port from GAMS)

This python module is designed as a port from GAMS and uses `mip` to do mixed-integer optimization.


## Introduction

This solver uses `mip` to find the optimal nutritional programs in a spatio-temporal model to find the right set of interventions, given the benefits and costs of each intervention at each time period and region given.

The problem can be written in terms of a primal and dual. One can either define the problem as a benefit maximization problem:

<a href="https://www.codecogs.com/eqnedit.php?latex=\begin{array}{c}{\operatorname{Max}&space;\sum_{k}&space;\sum_{t}&space;Y_{k,&space;t}&space;\sum_{j}&space;\frac{E&space;f&space;C&space;v&space;g_{k&space;j,&space;t}}{(1&plus;r)^{t}}}&space;\\&space;&plus;\sum_{k}&space;\sum_{j}&space;\sum_{t}&space;X_{k,&space;j,&space;t}&space;\frac{E&space;f&space;C&space;v&space;g_{k,&space;j,&space;t}}{(1&plus;r)^{t}}&space;\\&space;s.t.&space;\\&space;\begin{array}{l}{\sum_{k}&space;\sum_{t}&space;Y_{k,&space;t}&space;\sum_{j}&space;\frac{\mathrm{TC}_{k,&space;j,&space;t}}{(1&plus;i)^{t}}}&space;\\&space;{&plus;\sum_{k}&space;\sum_{j}&space;\sum_{t}&space;X_{k,&space;j,&space;t}&space;\frac{\mathrm{TC}_{k,&space;j,&space;t}}{(1&plus;i)^{t}}&space;\leq&space;\mathrm{TF}}\end{array}&space;\end{array}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\begin{array}{c}{\operatorname{Max}&space;\sum_{k}&space;\sum_{t}&space;Y_{k,&space;t}&space;\sum_{j}&space;\frac{E&space;f&space;C&space;v&space;g_{k&space;j,&space;t}}{(1&plus;r)^{t}}}&space;\\&space;&plus;\sum_{k}&space;\sum_{j}&space;\sum_{t}&space;X_{k,&space;j,&space;t}&space;\frac{E&space;f&space;C&space;v&space;g_{k,&space;j,&space;t}}{(1&plus;r)^{t}}&space;\\&space;s.t.&space;\\&space;\begin{array}{l}{\sum_{k}&space;\sum_{t}&space;Y_{k,&space;t}&space;\sum_{j}&space;\frac{\mathrm{TC}_{k,&space;j,&space;t}}{(1&plus;i)^{t}}}&space;\\&space;{&plus;\sum_{k}&space;\sum_{j}&space;\sum_{t}&space;X_{k,&space;j,&space;t}&space;\frac{\mathrm{TC}_{k,&space;j,&space;t}}{(1&plus;i)^{t}}&space;\leq&space;\mathrm{TF}}\end{array}&space;\end{array}" title="\begin{array}{c}{\operatorname{Max} \sum_{k} \sum_{t} Y_{k, t} \sum_{j} \frac{E f C v g_{k j, t}}{(1+r)^{t}}} \\ +\sum_{k} \sum_{j} \sum_{t} X_{k, j, t} \frac{E f C v g_{k, j, t}}{(1+r)^{t}} \\ s.t. \\ \begin{array}{l}{\sum_{k} \sum_{t} Y_{k, t} \sum_{j} \frac{\mathrm{TC}_{k, j, t}}{(1+i)^{t}}} \\ {+\sum_{k} \sum_{j} \sum_{t} X_{k, j, t} \frac{\mathrm{TC}_{k, j, t}}{(1+i)^{t}} \leq \mathrm{TF}}\end{array} \end{array}" /></a>

Essentially this entails maximizing discounted effective coverage with respect to a total funds constraint. 

The model allows for maximizing on region-specific basis (in the form of <a href="https://www.codecogs.com/eqnedit.php?latex=X_{k,j,t}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?X_{k,j,t}" title="X_{k,j,t}" /></a>) or to take part in a nationwide intervention (with <a href="https://www.codecogs.com/eqnedit.php?latex=Y_{k,j,t}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?Y_{k,j,t}" title="Y_{k,j,t}" /></a>).

The dual model entails minimizing discounted costs with respect to a minimum amount of effective coverage, or benefits.

## Installation

To install the module, first run `git clone`

`git clone https://github.com/amichuda/minimod.git`

then run `install.py`, or `pip install` once in the directory.

`pip install .`

`python setup.py install`

## Quick Start

### The Data Form

The data input needs to be in a particular form. Specifically, the dataset needs to be pandas dataframe. It needs to be a long dataset, with a column for intervention `k`, space `j` and time `t`. There must also be a column for benefits or costs:

        
        |k     | j   |t   | benefits   | costs |
        |------|-----|----|------------|-------|
        |maize |north|0   | 100        | 10    |
        |maize |south|0   | 50         | 20    |
        |maize |east |0   | 30         |30     |
        |maize |west |0   | 20         |40     |

### Running the fitter

In order to run the fitter, first get the data into the right form. We'll call this dataframe, `df`. Then instantiate the minimod class, run the fitter and run the report function:

```python

import minimod as mm

c = mm.CostSolver(data = df)

opt = c.opt()

c.report()
```
