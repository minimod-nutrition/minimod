
class ForbiddenExtensionException(Exception):
    """Raise when wrong file type is loaded"""
    pass

class DataNotLoaded(Exception):
    """Raise when data isn't loaded before analysis"""
    pass

    