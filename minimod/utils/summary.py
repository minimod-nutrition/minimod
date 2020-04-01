from tabulate import tabulate
import pandas as pd


class Summary:

    def __init__(self, model, table_fmt = "psql", decimals = 3, **kwargs):

        
        self.model = model
        self.table_fmt = table_fmt
        self.decimals = decimals

        # if model.opt_df is not None:
        #     self.opt_df = model.opt_df
        # else:
        #     raise Exception("Results from fit not found. Did you run the fit method before summarizing?")

    def _print_specific_style(self, style, data):
        if style == "html":
            return self.html_print(data)
        elif style == "markdown":
            return self.markdown_print(data)
        elif style == "latex":
            return self.latex_print(data)
        elif style == 'pandas':
            return self.pandas_show(data)
        else:
            raise ValueError("style not available.")

    def html_print(self, data):
        return print(data.to_html())

    def markdown_print(self, data):
        return print(data.to_markdown())

    def latex_print(self, data):
        return print(data.to_latex())

    def pandas_show(self, data):
        return print(data)

    def _group_summarizer(self,
                          data = None,
                          intervention_specific=None,
                          over_time=True,
                          across_space=False,
                          style=None):

        if style is None:
            print("[Note]: style not specified, printing as pandas dataframe")
            print_style = self.pandas_show
        if style is not None:
            print_style = self._print_specific_style

        grouper = []

        if intervention_specific is None:
            intervention_specific = slice(None)

        if across_space:
            grouper.append(self.model._space)

        if over_time:
            grouper.append(self.model._time)

        summary_data = (data
                        .loc[(intervention_specific, slice(None), slice(None)), :]
                        .groupby(grouper)
                        .sum())

        return print_style(style, summary_data)
    
    def print_ratio(self, name, num, denom):
        
        try:
            ratio = num/denom
        except TypeError:
            ratio = "NaN"
            
        print(tabulate([(name, ratio)], tablefmt=self.table_fmt))
        
        return ratio
    
    def print_grouper(self, name, show_group = True, **kwargs):
        
        print(tabulate([(name, "")], tablefmt=self.table_fmt))
        
        if show_group:
            self._group_summarizer(**kwargs)    

    def print_generic(self, *args):

        for table in args:
            
            print(tabulate(table, tablefmt=self.table_fmt))
            
         
            
    
            
        
        
        
        
        


        
        



