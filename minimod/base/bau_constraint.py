import mip

class BAUConstraintCreator:
    
    def __init__(self, other, sense):
        
        self.other = other
        
        if sense == mip.MINIMIZE:
            self.discounted_variable = 'discounted_benefits'
        elif sense == mip.MAXIMIZE:
            self.discounted_variable = 'discounted_costs'
    
    def bau_df(self):
        
        df = (self.other._df
         .loc[(self.other.minimum_benefit, 
               slice(None), 
               slice(None)),:][self.discounted_variable]
         )
        
        return df
        
    
    def create_bau_constraint(self):
        
        minimum_constraint = (
            self.bau_df()
            .sum()
        )
        
        return minimum_constraint