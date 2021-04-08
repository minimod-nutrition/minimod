class DataProcessor:
    
    def __init__(self, 
                 data: pd.DataFrame,
                 vehicle: str,
                 compound: list,
                 vehicle_col: str = None,
                 nutrient_col : str = None,
                 compound_col : str = None,
                 activity_col : str = None,
                 fort_level_col :  str = None,
                 overage_col : str = None,
                 price_col : str = None):
                
        self.vehicle_col = vehicle_col if vehicle_col is not None else 'vehicle'
        self.nutrient_col = nutrient_col if nutrient_col is not None else 'nutrient'
        self.compound_col = compound_col if compound_col is not None else 'compound'
        self.activity_col = activity_col if activity_col is not None else 'activity'
        self.fort_level_col = fort_level_col if fort_level_col is not None else 'fort_level'
        self.overage_col = overage_col if overage_col is not None else 'overage'
        self.price_col = price_col if price_col is not None else 'price'
        
        self._data = (
            data
            .loc[lambda df: df[self.vehicle_col] == vehicle]
            .loc[lambda df: df[self.compound_col].isin(compound)]
            .set_index([self.nutrient_col, self.compound_col])
            )
        
        self.nutrient = self._data.index.get_level_values(self.nutrient_col)
        self.compound = self._data.index.get_level_values(self.compound_col)
        self.activity = self._data[self.activity_col]
        self.fort_level = self._data[self.fort_level_col]
        self.overage = self._data[self.overage_col]
        self.price = self._data[self.price_col]
        
    @property
    def data(self):
        return self._data
        
    @property
    def amt_fort(self):
        return (self.fort_level + (self.fort_level * self.overage))/self.activity