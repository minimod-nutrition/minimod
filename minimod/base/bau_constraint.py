import pandas
import mip

class BAUConstraintCreator:
    
    def __init__(self):
        pass
    
    def bau_df(self, data:pandas.DataFrame, constraint:str, discounted_variable:str = None) -> pandas.DataFrame:
        """XX

        Args:
            data (pandas.DataFrame): dataframe with XX
            constraint (str): name of dataframe's column with information on XX
            discounted_variable (str, optional): name of dataframe's column with information on XX. Defaults to None.

        Returns:
            pandas.DataFrame: XX
        """
     
        if discounted_variable is None:
            discounted_variable = data.columns
        
        df = (data
         .loc[(constraint, 
               slice(None), 
               slice(None)),:][discounted_variable]
         )
        
        summed_bau_df = df.sum()
                        
        return df
        
    
    def create_bau_constraint(self, data:pandas.DataFrame, constraint:str, discounted_variable:str, over:str = None)->pandas.DataFrame:
        """This function sums the values of each column in the given dataframe. 
            If the option `over' is provided, the function sums across groups as well

        Args:
            data (pandas.DataFrame): dataframe with XX
            constraint (str): name of dataframe's column with information on XX
            discounted_variable (str): name of dataframe's column with information on XX
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
    
