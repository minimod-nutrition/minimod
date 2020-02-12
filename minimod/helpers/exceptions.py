
class NotPandasDataframe(Exception):
    """Raise when data isn't a pandas dataframe"""
    pass

class MissingColumn(Exception):
    """Raise when a column is not provided when necessary"""
    
class MissingOptimizationMethod(Exception):
    """Raise when an optimization method is not defined for the fit."""