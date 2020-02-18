class Summary:
    
    def __init__(self, model, **kwargs):
        
        self.model = model
        
        if model._opt_df is not None:
            self._opt_df = model._opt_df
        else:
            raise Exception("Results from fit not found. Did you run the fit method before summarizing?")
        
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
    
    def _sum_of_all(self, 
                    intervention_specific = None, 
                    col = 'costs'):
        
 
        
        if intervention_specific is None:
            intervention_specific = slice(None)
            
        sum_ = (self._opt_df[col]
                                                  .loc[(intervention_specific, slice(None), slice(None)), :]).sum()
        return sum_
        
        
    def _group_summarizer(self, 
                 intervention_specific = None,
                 over_time = True,
                 across_space = False,
                 style = None):
        

        
        if style is None:
            print("[Note]: style not specified, printing as pandas dataframe")
            print_style = self.pandas_show
        if style is not None:
            print_style = self._print_specific_style
        
        grouper = []
        
        if intervention_specific is None:
            intervention_specific = slice(None)
        
        if across_space == True:
            grouper.append(self.model._space_col)
            
        if over_time == True:
            grouper.append(self.model._time_col)
            
        summary_data = (self._opt_df
                        .loc[(intervention_specific, slice(None), slice(None)), :]
                        .groupby(grouper)
                        .sum())
        
        return print_style(style, summary_data)
    
    def _report(self):
        
        print(f"""
              Optimized Scenario with:
              
              Method: {self.model._method}
              Discount Factor on Costs: {self.model.discount_costs}
              Discount Factor on Benefits: {self.model.discount_benefits}
              """)
        
        print("+-----------------------------+")
        
        if self.model._method == 'min':
            
            print(f"""
                  With a Minimum Benefit Constraint of: {self.model.minimum_benefit}
                  """)
        if self.model._method == 'max':
            print(f"""
                  With a Total Funds Constraint of: {self.model.total_funds}
                  """)
        print("+------------------------------+")
        print("\n")    
        print("Total Costs and Coverage by Year")
        print("+------------------------------+")
        print("\n")
        self._group_summarizer(over_time=True, style='markdown')            
        print("\n")


        print("+---------------------------------+")
        print("+---------------------------------+")
        print("\n")
        
        print("Total Costs and Coverage by Year for BAU*")
        print("+------------------------------+")
        print("\n")

        self._group_summarizer(over_time=True, style='markdown',intervention_specific='vasoilold')            
        print("\n")

        print("+---------------------------------+")
        print("+---------------------------------+")
        print("\n")

        
        print("Total Cost for BAU")
        print("+------------------------------+")
        print("\n")
        
        total_cost_intervention_specific= self._sum_of_all(col = 'opt_costs', intervention_specific = 'vasoilold')
        total_benefit_intervention_specific = self._sum_of_all(col = 'opt_benefit', intervention_specific = 'vasoilold')

        print(str(total_cost_intervention_specific))
        print("\n")
        print("Total Benefit for BAU")
        print("+------------------------------+")
        print("\n")

        print(str(total_benefit_intervention_specific)) 
        
        print("\n")
        
        print("Cost per Woman for reproductive age for BAU")
        print("+------------------------------+")
        print("\n")
        print(f"""{total_cost_intervention_specific/total_benefit_intervention_specific}""") 
        
        print("\n")
        
        total_cost = self._sum_of_all(col = 'opt_costs')
        total_benefit = self._sum_of_all(col = 'opt_benefit')
        
        print("Total Cost")
        print("+------------------------------+")
        print("\n")
        print(str(total_cost))
        
        print("\n")
        
        print("Total Coverage")
        print("+------------------------------+")
        print("\n")
        print(str(total_benefit))
        
        print("\n")
        

        print("Cost per Coverage")
        print("+------------------------------+")
        print("\n")
        print(f"""{total_cost/total_benefit}""")  
        
        
    