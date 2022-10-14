
class NotPandasDataframe(Exception):
    """Raise when data isn't a pandas dataframe"""
    pass

class MissingData(Exception):
    """Raise when data isn't specified"""
    pass

class MissingColumn(Exception):
    """Raise when a column is not provided when necessary"""
    pass
    
class MissingOptimizationMethod(Exception):
    """Raise when an optimization method is not defined for the fit."""
    pass
    
class IncorrectKeys(Exception):
    """ Raise when dictionary keys are incorrectly specified."""
    pass

class NoVars(Exception):
    """Raise when variables not included in the model"""
    pass

class NoConstraints(Exception):
    """Raise when no constraints added to the model"""
    pass

class NoObjective(Exception):
    """Raise when no objective function is in the model"""
    pass

class OptimizationNotInitialized(Exception):
    """Riases when fitter hasn't been called yet."""
    pass