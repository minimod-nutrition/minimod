import pandas
import mip

class BAUConstraintCreator:
    
    def __init__(self):
        pass
    
    def bau_df(self, data:pandas.DataFrame, constraint:str, discounted_variable:str = None) -> pandas.DataFrame:
        """A dataframe of costs and benefits for the BAU (business as usual) intervention

        Args:
            data (pandas.DataFrame): input data
            constraint (str): name of dataframe BAU column
            discounted_variable (str, optional): outputs a series of the variable of interest. Defaults to None.

        Returns:
            pandas.DataFrame
        """
     
        if discounted_variable is None:
            discounted_variable = data.columns
        
        df = (data
         .loc[(constraint, 
               slice(None), 
               slice(None)),:][discounted_variable]
         )
                                
        return df
        
    
    def create_bau_constraint(self, data:pandas.DataFrame, constraint:str, discounted_variable:str, over:str = None)->pandas.DataFrame:
        """This function sums the values of each column in the given dataframe. 
            If the option `over' is provided, the function sums across groups as well

        Args:
            data (pandas.DataFrame): input data
            constraint (str): name of dataframe's column with information BAU
            discounted_variable (str): column of interest.
            over (str, optional): name of dataframe's column  with attribute used to group data by (e.g., time, region). Defaults to None.

        Returns:
            pandas.DataFrame: dataframe with the sum of values for each column-group
        """

      
        if over is None:
            minimum_constraint = (
                self.bau_df(data, constraint, discounted_variable)
                .sum()
            )
        else:
            minimum_constraint = (
                self.bau_df(data, constraint, discounted_variable)
                .groupby(over)
                .sum()
            )
        
        return minimum_constraint
    
