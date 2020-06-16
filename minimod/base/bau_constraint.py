import mip

class BAUConstraintCreator:
    
    def __init__(self):
        pass
    
    def bau_df(self, data, constraint, discounted_variable = None):
        
        if discounted_variable is None:
            discounted_variable = data.columns
        
        df = (data
         .loc[(constraint, 
               slice(None), 
               slice(None)),:][discounted_variable]
         )
        
        return df
        
    
    def create_bau_constraint(self, data, constraint, discounted_variable):
        
        minimum_constraint = (
            self.bau_df(data, constraint, discounted_variable)
            .sum()
        )
        
        return minimum_constraint