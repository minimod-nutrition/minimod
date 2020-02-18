
class Print:    
    """This class takes the output of the Solver methods and prints out a summary table.
    """
    
    def __init__(self, model, decimals =2, **kwargs):
        
        self.decimals = decimals
        
        if model._opt_df is not None:
            self.model = model
        else:
            raise Exception("Did you run the fit method before summarizing?")     
        
    def print_specific_style(self, style):
        if style == "html":
            return self.html_print()
        elif style == "markdown":
            return self.markdown_print()
        elif style == "latex":
            return self.latex_print()
        else:
            raise ValueError("style not available.") 
        
    

    def to_markdown(self, data)
            
    def show(self, style = None):
        
        if style is not None:
            style = self.print_specific_style(style)
        else:
            self.to_markdown()
        
        
        
        
        