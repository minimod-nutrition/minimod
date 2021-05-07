class NonUniqueNutrient(Exception):
    
    def __init__(self, message = "Nutrient occurs multiple times for given vehicle."):
        
        self.message = message
        super().__init__(self.message)

class NutrientNotFound(Exception):
    
    def __init__(self, nutrient,  message=None):
        
        self.nutrient = nutrient
        
        if message is None:
            self.message = f"No nutrient with name {nutrient} found in vehicle_dict"
        super().__init__(self.message)
        
class FunctionValueIncompatible(Exception):
    
    def __init__(self, col, message=None):
        
        self.col = col
        
        if message is None:
            self.message = f"The number of values given to {self.col} does not equal the number of functions"
        
        super().__init__(self.message)