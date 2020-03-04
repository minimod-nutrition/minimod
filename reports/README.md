# Generating Reports with `codebraid`

The reports in this directory are generated using `codebraid`, a package that provides live code execution during pandoc processing. 

## Installation

To generate the report, first install `pandoc` from [here](https://pandoc.org/installing.html). Then install `codebraid`

```
pip install codebraid

```

or 

```
conda install codebraid
```

## Generating the Report

To generate the pdf report, run:

```
codebraid pandoc report.md -f markdown+tex_math_single_backslash -t latex -o report.pdf --overwrite
```


